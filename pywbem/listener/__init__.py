"""
The `WBEM listener API`_ is provided by the :mod:`pywbem.listener` module.

It provides functionality for managing subscriptions for indications from
one or more WBEM servers, and implements a thread-based WBEM listener service.

.. note::

   Requirements for the WBEM listener API:

   * Must support an easy way for applications to subscribe for indications, and
     to get the corresponding indications.

   * Subscriptions from one "application" must be independent from subscriptions
     by another application, so that each application has its own scope and can
     manage its own subscriptions independently.

   * Must be able to start and stop the listener service.

   * The listener service should have a simple default way to be run (e.g. as a
     thread) but should also be integrateable into external service frameworks.

   * Must support multiple WBEM servers.

.. note::

   Design notes:

   * An "application" is a Python process.

   * Each Python process has the listener demon included in the form of a thread.

     - That automatically results in each application having its own scope of 
       managing subcriptions.
     - On the downside, the price for that is that two Python processes on the
       same client system that subscribe for the same set of indications get
       them delivered bythe WBEM server once for each of them.
     - Another downside is that each such listener demon occupies one port
       (or set of ports) on the client system.
     - However, it is probably rare to have multiple applications interested
       in indications on the same system.

   * Indications are communicated to the subscribing application:

     - By callback function
     - Other mechanisms are left for the future (e.g. some event notification)

Example
-------

The following example code subscribes for a CIM alert indication
on two WBEM servers and registers a callback function for indication
delivery:

::

    from socket import getfqdn
    from pywbem import WBEMConnection
    from pywbem.listener import WBEMListener
    from pywbem.server import WBEMServer

    def process_indication(indication):
        '''This function gets called when an indication is received.'''
        print("Received CIM indication: {0!r}".format(indication))

    def main():

        conn1 = WBEMConnection('http://server1')
        server1 = WBEMServer(conn1)
        server1.determine_interop_ns()

        conn2 = WBEMConnection('http://server2')
        server2 = WBEMServer(conn2)
        server2.validate_interop_ns('root/PG_InterOp')

        listener = WBEMListener(getfqdn())  # default http + https ports
        listener.add_callback(process_indication)
        listener.add_server(server1)
        listener.add_server(server2)
        listener.start()

        # Subscribe for a static filter of a given name
        filters = listener.get_filters(server1)
        for f in filters:
            if f['Name'] == "DMTF:Indications:GlobalAlertIndicationFilter":
                listener.add_subscription(f.path)
                break

        # Create a dynamic alert indication filter and subscribe for it
        filter2_path = listener.add_dynamic_filter(
            query_language="DMTF:CQL"
            query="SELECT * FROM CIM_AlertIndication " \\
                  "WHERE OwningEntity = 'DMTF' " \\
                  "AND MessageID LIKE 'SVPC0123|SVPC0124|SVPC0125'")
        listener.add_subscription(filter2_path)
"""

import os
import sys
import time
from socket import getfqdn

import six
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
#from twisted.python import log

_ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'

if six.PY2 and not _ON_RTD:  # RTD has no swig to install M2Crypto
    from M2Crypto import SSL           # pylint: disable=wrong-import-position
    from M2Crypto.Err import SSLError  # pylint: disable=wrong-import-position
    _HAVE_M2CRYPTO = True
else:
    import ssl as SSL                  # pylint: disable=wrong-import-position
    from ssl import SSLError           # pylint: disable=wrong-import-position
    _HAVE_M2CRYPTO = False

import pywbem
from pywbem.server import WBEMServer

DEFAULT_LISTENER_PORT_HTTP = 5988
DEFAULT_LISTENER_PORT_HTTPS = 5989
DEFAULT_QUERY_LANGUAGE = 'WQL'

__all__ = ['WBEMListener']


class WBEMListener(object):
    """
    A WBEM listener, supporting the CIM-XML protocol for CIM indications.

    It supports starting and stopping a WBEM listener thread.
    The WBEM listener thread is an HTTP/HTTPS server that listens for
    CIM indications from one or more WBEM servers.

    It also supports the management of subscriptions for CIM indications
    from one or more WBEM servers, including the creation and deletion of
    the necessary listener, filter and subscription instances in the WBEM
    servers.
    """

    def __init__(self, host, http_port=DEFAULT_LISTENER_PORT_HTTP,
                 https_port=DEFAULT_LISTENER_PORT_HTTPS):
        """
        Parameters:

          host (:term:`string`):
            IP address or host name this listener can be reached at.

          http_port (:term:`string` or :term:`integer`):
            HTTP port this listener can be reached at.

            `None` means not to set up a port for HTTP.

          https_port (:term:`string` or :term:`integer`):
            HTTPS port this listener can be reached at.

            `None` means not to set up a port for HTTPS.
        """

        self._host = host

        if isinstance(http_port, six.integer_types):
            self._http_port = int(http_port)  # Convert Python 2 long to int
        elif isinstance(http_port, six.string_types):
            self._http_port = int(http_port)
        elif http_port is None:
            self._http_port = http_port
        else:
            raise TypeError("Invalid type for http_port: %s" % \
                            type(http_port))

        if isinstance(https_port, six.integer_types):
            self._https_port = int(https_port)  # Convert Python 2 long to int
        elif isinstance(https_port, six.string_types):
            self._https_port = int(https_port)
        elif https_port is None:
            self._https_port = https_port
        else:
            raise TypeError("Invalid type for https_port: %s" % \
                            type(https_port))

        # The following dictionaries have the WBEM server URL as a key.
        self._servers = {}
        self._subscriptions = {}
        self._dynamic_filters = {}
        self._destinations = {}
        self._callbacks = ()

    @property
    def host(self):
        """The IP address or host name this listener can be reached at,
        as a :term:`string`."""
        return self._host

    @property
    def http_port(self):
        """
        The HTTP port this listener can be reached at, as an :term:`integer`.

        `None` means there is no port set up for HTTP.
        """
        return self._http_port

    @property
    def https_port(self):
        """
        The HTTPS port this listener can be reached at, as an :term:`integer`.

        `None` means there is no port set up for HTTPS.
        """
        return self._https_port

    def start(self):
        """
        Start the WBEM listener thread.

        Once the WBEM listener thread is up and running, return.
        """
        # TODO: Start logging
        #log.startLogging(sys.stdout)
        site = Site(_WBEMListenerResource(self))
        if self.http_port:
            reactor.listenTCP(self.http_port, site)
        if self.https_port:
            reactor.listenSSL(self.https_port, site,
                              _HTTPSServerContextFactory())
        reactor.run()

    def stop(self):
        """
        Stop the WBEM listener thread.
        """
        raise NotImplementedError  # TODO: Implement

    def add_server(self, server):
        """
        Add a WBEM server to this listener and register with the WBEM server by
        creating an indication listener instance for this listener in its
        Interop namespace.

        Parameters:

          server (:class:`~pywbem.server.WBEMServer`):
            The WBEM server to be added.

        Returns:

          The URL of the WBEM server, as a :term:`string`.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """

        if server.url in self._servers:
            raise ValueError("WBEM server already known by listener: %s" % \
                             server.url)
        self._servers[server.url] = server
        self._subscriptions[server.url] = []
        self._dynamic_filters[server.url] = []
        self._destinations[server.url] = []
        self._callbacks[server.url] = []

        # We let the WBEM server use HTTP or HTTPS dependent on whether we
        # contact it using HTTP or HTTPS.
        if server.conn.url.lower().startswith('http'):
            scheme = 'http'
            port = self.http_port
        elif server.conn.url.lower().startswith('https'):
            scheme = 'https'
            port = self.https_port
        else:
            raise ValueError("Invalid scheme in server URL: %s" % \
                             server.conn.url)

        dest_url = '%s://%s:%s' % (scheme, self.host, port)
        dest_inst_path = server.create_destination(dest_url)
        self._destinations[server.url].append(dest_inst_path)

        return server.url

    def remove_server(self, server_url):
        """
        Remove a WBEM server from this listener and unregister this listener
        from that WBEM server by deleting all indication subscriptions,
        dynamic indication filters and listener destinations in the WBEM server
        that were created by this listener.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """

        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]

        # Delete any instances we recorded to be cleaned up

        if server_url in self._subscriptions:
            sub_tuples = self._subscriptions[server_url]
            for i, sub_tuple in enumerate(sub_tuples):
                server.conn.DeleteInstance(sub_tuple[0])
                del sub_tuples[i]
            del self._subscriptions[server_url]

        if server_url in self._dynamic_filters:
            filter_insts = self._dynamic_filters[server_url]
            for i, inst in enumerate(filter_insts):
                server.conn.DeleteInstance(inst.path)
                del filter_insts[i]
            del self._dynamic_filters[server_url]

        if server_url in self._destinations:
            cleanup_insts = self._destinations[server_url]
            for i, inst_path in enumerate(cleanup_insts):
                server.conn.DeleteInstance(inst_path)
                del cleanup_insts[i]
            del self._destinations[server_url]

        # Remove server from this listener
        del self._servers[server_url]

    def add_dynamic_filter(self, server_url, query,
                           query_language=DEFAULT_QUERY_LANGUAGE):
        """
        Add a dynamic indication filter to a WBEM server that defines a
        particular set of indications, and remember it for cleanup.

        This function creates an indication filter instance in the WBEM server.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

          query (:term:`string`):
            Filter query in the specified query language.

          query_language (:term:`string`):
            Query language for the specified filter query.

            Examples: 'WQL', 'DMTF:CQL'.

        Returns:
            Instance path of the indication filter instance, as a
            :class:`~pywbem.CIMInstanceName` instance.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        filter_inst = server.create_filter(query, query_language)
        self._dynamic_filters[server_url].append(filter_inst)
        return filter_inst.path

    def remove_dynamic_filter(self, server_url, filter_path):
        """
        Remove a dynamic indication filter from a WBEM server, and forget it for
        cleanup.

        This function deletes an indication filter instance in the WBEM server.

        The indication filter must be a dynamic indication filter that has been
        created by this listener, and there must not exist any subscriptions
        referencing the filter.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

          filter_path (:class:`~pywbem.CIMInstanceName`):
            Instance path of the indication filter instance in the WBEM
            server.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        if server_url in self._dynamic_filters:
            filter_insts = self._dynamic_filters[server_url]
            for i, inst in enumerate(filter_insts):
                if inst.path == filter_path:
                    server.conn.DeleteInstance(filter_path)
                del filter_insts[i]

    def get_dynamic_filters(self, server_url):
        """
        Return the dynamic indication filters in a WBEM server that have been
        created by this listener.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

        Returns:

          List of :class:`~pywbem.CIMInstance` objects representing the
          indication filter instances.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        filter_insts = self._dynamic_filters[server_url]
        return filter_insts

    def get_filters(self, server_url):
        """
        Return all (dynamic and static) indication filters in a WBEM server.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

        Returns:

          List of :class:`~pywbem.CIMInstance` objects representing the
          indication filter instances.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        filter_insts = server.conn.EnumerateInstance(
            'CIM_IndicationFilter', namespace=server.interop_ns)
        return filter_insts

    def add_subscription(self, server_url, filter_path):
        """
        Add a subscription to a WBEM server for particular set of indications
        defined by an indication filter, and remember it for cleanup.

        This function creates an indication subscription instance linking
        the specified indication filter with the listener destination
        in the WBEM server.

        The indication filter can be a dynamic filter created specifically for
        this listener via :meth:`add_dynamic_filter`, or a static filter that
        pre-exists in the WBEM server. Filters defined in the WBEM server can
        be retrieved via :meth:`get_filters`.

        Upon successful return of this method, the subscription is active.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

          filter_path (:class:`~pywbem.CIMInstanceName`):
            Instance path of the indication filter instance in the WBEM
            server that specifies the indications to be sent.

        Returns:
            Instance path of the indication subscription instance, as a
            :class:`~pywbem.CIMInstanceName` instance.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        dest_path = self._destinations[server_url][0]
        sub_inst_path = server.create_subscription(dest_path, filter_path)
        self._subscriptions[server_url].append(tuple(sub_inst_path, callback))
        return sub_inst_path

    def remove_subscription(self, server_url, sub_path):
        """
        Remove an indication subscription from a WBEM server, and forget it for
        cleanup.

        This function deletes an indication subscription instance in the WBEM
        server.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

          sub_path (:class:`~pywbem.CIMInstanceName`):
            Instance path of the indication subscription instance in the WBEM
            server.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        if server_url in self._subscriptions:
            sub_tuples = self._subscriptions[server_url]
            for i, sub_tuple in enumerate(sub_tuples):
                if sub_tuple[0] == sub_path:
                    server.conn.DeleteInstance(sub_path)
                    del sub_tuples[i]
                    break

    def get_subscriptions(self, server_url):
        """
        Return the indication subscriptions in a WBEM server that have been
        created by this listener.

        Parameters:

          server_url (:term:`string`):
            The URL of the WBEM server.

        Returns:

          List of :class:`~pywbem.CIMInstanceName` objects representing the
          indication subscription instance paths.

        Raises:

            Exceptions raised by :class:`~pywbem.WBEMConnection`.
        """
        if server_url not in self._servers:
            raise ValueError("WBEM server not known by listener: %s" % \
                             server_url)
        server = self._servers[server_url]
        sub_paths = self._subscriptions[server_url]
        return sub_paths

    def _deliver_indication(self, indication):
        """
        Deliver an indication to a subscriber.

        This function is called by the listener thread once it receives
        an indication. It delivers the indication to the application by
        calling the callback functions known to this listener.

        Parameters:

          indication (pywbem.CIMIndication):
            Representation of the CIM indication to be delivered.
        """
        for callback in self._callbacks:
            callback(indication)

    def add_callback(self, callback):
        """
        Add a callback function to the listener.

        The callback function will be called for each indication this listener
        receives from the WBEM server.

        If the callback function is already known to the listener, it will not
        be added.

        Parameters:

          callback (callback_interface):
            Callable that is being called for each CIM indication that is
            received while the listener thread is active.
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)


def callback_interface(indication):
    """
    Interface of a function that is provided by the user of the API and
    that will be called by the listener for each received CIM indication.

    Parameters:

      indication (:class:`~pywbem.CIMInstance`):
        Representation of the CIM indication that has been received.
        Its `path` component is not set.

    Raises:
      TBD
    """
    raise NotImplementedError


class _WBEMListenerResource(Resource):


    def __init__(self, listener):
        """
        Store the specified WBEMListener object for later use.
        """
        super(_WBEMListenerResource, self)
        self._listener = listener

    def render_POST(self, request):
        """
        Will be called for each POST to the WBEM listener. It handles
        the CIM-XML export message and delivers the contained CIM
        indication to the stored listener object.
        """
        # TODO: Convert CIM-XML payload into a CIMInstance
        indication = CIMInstance('CIM_Indication') # dummy, for now
        self._listener._deliver_indication(indication)


class _HTTPSServerContextFactory:

    def getContext(self):
        """Create an SSL context with a dodgy certificate."""
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file('server.pem')
        ctx.use_privatekey_file('server.pem')
        return ctx

