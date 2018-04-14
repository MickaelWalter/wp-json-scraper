"""
Copyright (c) 2018 Mickaël "Kilawyn" Walter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests

from lib.exceptions import NoWordpressApi

class WPApi:
    """
    Queries the WordPress API to retrieve information
    """

    def __init__(self, target, api_path="wp-json/"):
        """
        Creates a new instance of WPApi
        param target: the target of the scan
        param api_path: the api path, if non-default
        """
        self.api_path = api_path
        self.has_v2 = None
        self.name = None
        self.description = None
        self.url = target

    def get_basic_info(self):
        """
        Collects and stores basic information about the target
        """
        req = requests.get(self.url + self.api_path)
        if req.status_code >= 400:
            raise NoWordpressApi
        basic_info = req.json()
        if 'name' in basic_info.keys():
            self.name = basic_info['name']
        if 'description' in basic_info.keys():
            self.description = basic_info['description']
        if 'namespaces' in basic_info.keys() and 'wp/v2' in basic_info['namespaces']:
            self.has_v2 = True
        return basic_info
