"""
Unit tests for the resolvers.py file
"""

from django.test import TestCase

from edx_notifications.channels.link_resolvers import (
    MsgTypeToUrlResolver,
)


class MsgTypeToUrlResolverTests(TestCase):
    """
    Make sure things resolve as we expect them to
    """

    def test_resolve(self):
        """
        Assert we can resolve a well formed type_name, link_name, and params
        """

        resolver = MsgTypeToUrlResolver({
            '_click_url': {
                # this will conver msg type 'test-type.type-with-links'
                # to /path/to/{param1}/url/{param2} with param subsitutations
                # that are passed in with the message
                'test-type.type-with-links': '/path/to/{param1}/url/{param2}'
            }
        })

        url = resolver.resolve(
            'test-type.type-with-links',
            '_click_url',
            {
                'param1': 'foo',
                'param2': 'bar',
            }
        )
        self.assertEqual(url, '/path/to/foo/url/bar')

    def test_missing_type(self):
        """
        Failure case when the msg_type cannot be found
        """

        resolver = MsgTypeToUrlResolver({
            '_click_url': {
                # this will conver msg type 'test-type.type-with-links'
                # to /path/to/{param1}/url/{param2} with param subsitutations
                # that are passed in with the message
                'test-type.type-with-links': '/path/to/{param1}/url/{param2}'
            }
        })

        url = resolver.resolve(
            'test-type.missing-type',
            '_click_url',
            {
                'param1': 'foo',
                'param2': 'bar',
            }
        )
        self.assertIsNone(url)

    def test_missing_link_name(self):
        """
        Failure case when the link_name cannot be found
        """

        resolver = MsgTypeToUrlResolver({
            '_click_url': {
                # this will conver msg type 'test-type.type-with-links'
                # to /path/to/{param1}/url/{param2} with param subsitutations
                # that are passed in with the message
                'test-type.type-with-links': '/path/to/{param1}/url/{param2}'
            }
        })

        url = resolver.resolve(
            'test-type.type-with-links',
            'missing_link_name',
            {
                'param1': 'foo',
                'param2': 'bar',
            }
        )
        self.assertIsNone(url)

    def test_missing_formatting_param(self):
        """
        Failure case wheen the msg_type cannot be found
        """

        resolver = MsgTypeToUrlResolver({
            '_click_url': {
                # this will conver msg type 'test-type.type-with-links'
                # to /path/to/{param1}/url/{param2} with param subsitutations
                # that are passed in with the message
                'test-type.type-with-links': '/path/to/{param1}/url/{param2}'
            }
        })

        url = resolver.resolve(
            'test-type.type-with-links',
            '_click_url',
            {
                'param1': 'foo',
            }
        )
        self.assertIsNone(url)
