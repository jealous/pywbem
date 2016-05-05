PyWBEM Client
=============

The PyWBEM Client project provides a WBEM client library and some related
utilities, written in pure Python.

A WBEM client allows issuing operations to a WBEM server, using the CIM
operations over HTTP (CIM-XML) protocol defined in the DMTF standards
DSP0200 and DSP0201. See http://www.dmtf.org/standards/wbem for information
about WBEM. This is used for all kinds of systems management tasks that are
supported by the system running the WBEM server.

Usage
-----

For information on how to use the PyWBEM Client for your own development
projects, or how to contribute to it, go to the
`PyWBEM Client page`_.

License
-------

The PyWBEM Client is provided under the
`GNU Lesser General Public License (LGPL) version 2.1`_,
or (at your option) any later version.


About this Fork for pywbem - pywbemReq
======================================

A simplified wbem client.

Remove mof compiler and twisted client.
And remove the dependencies caused by them.

Remove some xml validation.  Do not break the xml parsing/construction
if request/response xml is not align with the schema.
 
Introduce python 3 compatible code.  The wbem client should be working fine
under python 3.

Replace the m2crypto/httplib with requests_.


.. _GNU Lesser General Public License (LGPL) version 2.1: LICENSE.txt
.. _PyWBEM Client page: http://pywbem.github.io/pywbem/
.. _requests: https://github.com/kennethreitz/requests