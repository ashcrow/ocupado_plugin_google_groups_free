# Copyright (C) 2015 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for the Google Groups Free plugin.
"""

import unittest

import mechanize
import mock

from contextlib import nested

from ocupado_plugin_google_groups_free import GoogleGroupsFree


RESPONSE_HEADERS = [
    ('Content-Type', 'text/html'),
]

LOGIN_URL = (
    'https://accounts.google.com/ServiceLogin'
    '?continue=https%3A%2F%2Fgroups.google.com%2Fd%2Foverview'
    '&hl=en&service=groups2&passive=true'
)

LOGOUT_URL = (
    'https://accounts.google.com/SignOutOptions'
    '?continue=https%3A%2F%2Fgroups.google.com%2Fd%2Foverview'
)

LOGIN_HTML = '''
<html><form><input name="Email" /><input name="Passwd"/></form></html>
'''


class TestOcupadoPluginGoogleGroupsFree(unittest.TestCase):
    """
    Tests the GoogleGroupsFree plugin.
    """

    def setUp(self):
        self.g = GoogleGroupsFree(
            user='user',
            password='secret',
            group='test')

    def test_plugin_google_groups_free_init(self):
        self.assertEquals(self.g._user, 'user')
        self.assertEquals(self.g._password, 'secret')
        self.assertEquals(self.g._group, 'test')

    def test_plugin_google_groups_free_authenticate(self):
        with mock.patch('mechanize.Browser.open') as _open:
            # Setting return data for the authenticate() state
            self.g._con._set_response(
                mechanize._response.make_response(
                    LOGIN_HTML, RESPONSE_HEADERS,
                    LOGIN_URL, 200, '200 OK'), False)
            # authenticate() shouldn't return anything
            self.assertEquals(self.g.authenticate(), None)
            # There should have been two calls
            self.assertEquals(_open.call_count, 2)
            # The first call should have oly taken in the login url
            self.assertEquals(_open.call_args_list[0][0][0], LOGIN_URL)

    def test_plugin_google_groups_free_logout(self):
        with mock.patch('mechanize.Browser.open') as _open:
            # logout() should return nothing
            self.assertEquals(self.g.logout(), None)
            _open.assert_called_once_with(LOGOUT_URL)

    def test_plugin_google_groups_free_exists(self):
        with nested(
                    mock.patch('mechanize.Browser.open'),
                    mock.patch('mechanize.Browser.retrieve'),
                ) as (_open, _retrieve):
            # Setting return data for the authenticate() state
            self.g._con._set_response(
                mechanize._response.make_response(
                    LOGIN_HTML, RESPONSE_HEADERS,
                    LOGIN_URL, 200, '200 OK'), False)

            self.g.authenticate()

            # Point the retrieve call to test/members.csv
            _retrieve.return_value = ('test/members.csv', [])

            exists, info = self.g.exists('human')
            self.assertTrue(exists)
            self.assertTrue(info['exists'])
            self.assertEquals(info['details']['username'], 'human')

    def test_plugin_google_groups_free_exists_with_no_results(self):
        with nested(
                    mock.patch('mechanize.Browser.open'),
                    mock.patch('mechanize.Browser.retrieve'),
                ) as (_open, _retrieve):
            # Setting return data for the authenticate() state
            self.g._con._set_response(
                mechanize._response.make_response(
                    LOGIN_HTML, RESPONSE_HEADERS,
                    LOGIN_URL, 200, '200 OK'), False)

            self.g.authenticate()

            # Point the retrieve call to test/members.csv
            _retrieve.return_value = ('test/nomembers.csv', [])

            exists, info = self.g.exists('doesnotexist')
            self.assertFalse(exists)
            self.assertFalse(info['exists'])
            self.assertEquals(info['details']['username'], 'doesnotexist')

    def test_plugin_google_groups_free_get_all_usernames(self):
        with nested(
                    mock.patch('mechanize.Browser.open'),
                    mock.patch('mechanize.Browser.retrieve'),
                ) as (_open, _retrieve):
            # Setting return data for the authenticate() state
            self.g._con._set_response(
                mechanize._response.make_response(
                    LOGIN_HTML, RESPONSE_HEADERS,
                    LOGIN_URL, 200, '200 OK'), False)

            self.g.authenticate()

            # Point the retrieve call to test/members.csv
            _retrieve.return_value = ('test/members.csv', [])

            users = self.g.get_all_usernames()
            # Verify the contents
            self.assertIn('human', users)
            self.assertIn('robot', users)
            self.assertNotIn('notthere', users)
