# coding=utf-8
from __future__ import unicode_literals
from hamcrest import assert_that, equal_to

from pywbemReq.cim_http import parse_url
from unittest import TestCase

__author__ = 'Cedric Zhuang'


class CimHttpTest(TestCase):
    def test_parse_url(self):
        url = 'http://www.abc.com:5050/page.xml'
        host, port, ssl = parse_url(url)
        assert_that(host, equal_to('www.abc.com'))
        assert_that(port, equal_to(5050))
        assert_that(ssl, equal_to(False))

    def test_parse_url_ssl(self):
        url = 'https://10.0.0.1:4443/page/my.html?filter=name'
        host, port, ssl = parse_url(url)
        assert_that(host, equal_to('10.0.0.1'))
        assert_that(port, equal_to(4443))
        assert_that(ssl, equal_to(True))

    def test_parse_url_ipv6(self):
        url = 'https://[2001:db8:a0b:12f0::1%eth0]:21/my.txt'
        host, port, ssl = parse_url(url)
        assert_that(host, equal_to('2001:db8:a0b:12f0::1%eth0'))
        assert_that(port, equal_to(21))
        assert_that(ssl, equal_to(True))

    def test_parse_url_default_port(self):
        url = 'https://2001:db8:a0b:12f0::1-eth0/my.txt'
        host, port, ssl = parse_url(url)
        assert_that(host, equal_to('2001:db8:a0b:12f0::1%eth0'))
        assert_that(port, equal_to(5989))
        assert_that(ssl, equal_to(True))

    def test_parse_url_default_protocol(self):
        url = '10.0.0.1/my.txt'
        host, port, ssl = parse_url(url)
        assert_that(host, equal_to('10.0.0.1'))
        assert_that(port, equal_to(5988))
        assert_that(ssl, equal_to(False))
