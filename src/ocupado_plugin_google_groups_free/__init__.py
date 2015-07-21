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
Google Groups plugin for the ocupado tool.
"""

import csv
import json
import os
import warnings

import mechanize
import cookielib

from ocupado.plugin import Plugin

# Attempt to use the fastest StringIO
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# turn off warnings
warnings.simplefilter('ignore')

__version__ = '0.0.1'


class GoogleGroupsFree:
    """
    GoogleGroups Free plugin for ocupado.
    """

    #: URL for login
    _login_endpoint = (
        'https://accounts.google.com/ServiceLogin'
        '?continue=https%3A%2F%2Fgroups.google.com%2Fd%2Foverview'
        '&hl=en&service=groups2&passive=true'
    )
    #: URL for logout
    _logout_endpoint = 'https://accounts.google.com/Logout?hl=en'

    #: URL template for user export. Requires "% self._group"
    _export_endpoint_tpl = 'https://groups.google.com/forum/exportmembers/%s'

    def __init__(self, user, password, group):
        """
        Creates an instance of the Google Groups plugin.

        :user: The username to auth with
        :password: The password to auth with
        """
        self._user = user
        self._password = password
        self._group = group
        self._export_endpoint = self._export_endpoint_tpl % self._group
        self._cookies = cookielib.LWPCookieJar()
        self._con = mechanize.Browser()
        self._con.set_cookiejar(self._cookies)
        self._con.set_handle_robots(False)
        self._con.set_handle_redirect(True)
        self._con.set_handle_equiv(True)
        self._con.set_handle_gzip(True)
        self._con.set_handle_referer(True)

    def authenticate(self):
        """
        Defines how to authenticate via Google Groups.
        """
        self._con.open(self._login_endpoint)
        # Use the first form
        self._con.select_form(nr=0)
        self._con.form['Email'] = self._user
        self._con.form['Passwd'] = self._password
        self._con.submit()
        self._cookies
        # Check cookies to make sure we are logged in
        # FWIW: This is an unfortunate side effect of scraping and trying to be
        # thorough
        google_com_cookies = ['APISID', 'SSID', 'SAPISID', 'SID', 'HSID']
        try:
            cookies = self._cookies._cookies
            for expected in ['APISID', 'SSID', 'SAPISID', 'SID', 'HSID']:
                if expected not in cookies['.google.com']['/'].keys():
                    # TODO: Use a real exception
                    raise Exception
            if 'LSID' not in cookies['accounts.google.com']['/']:
                # TODO: Use a real exception
                raise Exception
        except:
            # TODO: Use a real exception
            raise Exception(
                'Log in failed: Expected cookies missing. '
                'Required: .google.com:%s, accounts.google.com:LSID' % (
                    google_com_cookies))

    def logout(self):
        """
        Defines how to logout via a Google Groups Free.
        """
        self._con.open(self._logout_endpoint)
        # Check for removal of expected cookies post logout
        # FWIW: This is an unfortunate side effect of scraping and trying to be
        # thorough
        auth_cookies = []
        cookies = self._cookies._cookies
        if '.google.com' in self._cookies._cookies.keys():
            for removed in ['APISID', 'SSID', 'SAPISID', 'SID', 'HSID']:
                if removed in cookies['.google.com']['/'].keys():
                    auth_cookies.append('.google.com:/:' + removed)

        if 'accounts.google.com' in self._cookies._cookies.keys():
            if 'LSID' in cookies['accounts.google.com']['/']:
                auth_cookies.append('accounts.google.com:/:LSID')

        if auth_cookies:
            raise Exception('Log out failed: Cookies still exist: %s' % (
                auth_cookies))
        # We should be back to the log in pagea
        if self._con.title() != 'Google Accounts':
            # TODO: Make real exceptions
            raise Exception('Log out failed. Expected end flow did not occur.')
        # Clear all cookies for good measure
        self._cookies.clear()

    def exists(self, userid):
        """
        Checks for the existance of a user in Google Groups.

        :userid: The userid to check.
        """
        if userid in self.get_all_usernames():
            return True, {"exists": True, "details": {"username": userid}}
        return False, {'exists': False, 'details': {'username': userid}}

    def get_all_usernames(self):
        """
        Returns **all** user names.
        """
        filename, _ = self._con.retrieve(self._export_endpoint)
        result = []
        data = StringIO()

        with open(filename, 'r') as f:
            # Skip the first line
            f.next()
            for line in f:
                data.write(line + "\n")
            data.seek(0)
            results = csv.DictReader(data)
        # Clean up temp file
        os.unlink(filename)

        for member in results:
            result.append(member['Email address'].split('@')[0])
        return result

    # Read-only properties
    #: Shortcut for accessing the headers of the current page.
    _current_headers = property(lambda s: s._con.response().info().headers)
