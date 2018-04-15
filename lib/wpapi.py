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

from lib.exceptions import NoWordpressApi, WordPressApiNotV2

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
        self.basic_info = None
        self.posts = None
        self.tags = None
        self.categories = None
        self.users = None
        self.media = None
        self.pages = None

    def get_basic_info(self):
        """
        Collects and stores basic information about the target
        """
        if self.basic_info is not None:
            return self.basic_info

        req = requests.get(self.url + self.api_path)
        if req.status_code >= 400:
            raise NoWordpressApi
        self.basic_info = req.json()

        if 'name' in self.basic_info.keys():
            self.name = self.basic_info['name']

        if 'description' in self.basic_info.keys():
            self.description = self.basic_info['description']

        if 'namespaces' in self.basic_info.keys() and 'wp/v2' in \
                self.basic_info['namespaces']:
            self.has_v2 = True

        return self.basic_info

    def get_all_posts(self):
        """
        Retrieves all posts
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.posts is not None:
            return self.posts

        self.posts = []
        page = 1
        more_posts = True
        while more_posts:
            req = requests.get(self.url + self.api_path +
                               'wp/v2/posts?page=%d' % page)
            if req.status_code > 400:
                raise WordPressApiNotV2
            if type(req.json()) is list and len(req.json()) > 0:
                self.posts += req.json()
            else:
                more_posts = False
            page += 1
        return self.posts

    def get_all_tags(self):
        """
        Retrieves all tags
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.tags is not None:
            return self.tags

        self.tags = []
        page = 1
        more_tags = True
        while more_tags:
            req = requests.get(self.url + self.api_path +
                               'wp/v2/tags?page=%d' % page)
            if req.status_code > 400:
                raise WordPressApiNotV2
            if type(req.json()) is list and len(req.json()) > 0:
                self.tags += req.json()
            else:
                more_tags = False
            page += 1
        return self.tags

    def get_all_categories(self):
        """
        Retrieves all categories
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.categories is not None:
            return self.categories

        self.categories = []
        page = 1
        more_categories = True
        while more_categories:
            req = requests.get(self.url + self.api_path +
                               'wp/v2/categories?page=%d' % page)
            if req.status_code > 400:
                raise WordPressApiNotV2
            if type(req.json()) is list and len(req.json()) > 0:
                self.categories += req.json()
            else:
                more_categories = False
            page += 1
        return self.categories

    def get_all_users(self):
        """
        Retrieves all users
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.users is not None:
            return self.users

        self.users = []
        page = 1
        more_users = True
        while more_users:
            req = requests.get(self.url + self.api_path +
                               'wp/v2/users?page=%d' % page)
            if req.status_code > 400:
                raise WordPressApiNotV2
            if type(req.json()) is list and len(req.json()) > 0:
                self.users += req.json()
            else:
                more_users = False
            page += 1
        return self.users

    def get_all_media(self):
        """
        Retrieves all media objects
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.media is not None:
            return self.media

        self.media = []
        page = 1
        more_media = True
        while more_media:
            req = requests.get(self.url + self.api_path +
                               'wp/v2/media?page=%d' % page)
            if req.status_code > 400:
                raise WordPressApiNotV2
            if type(req.json()) is list and len(req.json()) > 0:
                self.media += req.json()
            else:
                more_media = False
            page += 1
        return self.media

    def get_all_pages(self):
        """
        Retrieves all pages
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.pages is not None:
            return self.pages

        self.pages = []
        page = 1
        more_pages = True
        while more_pages:
            req = requests.get(self.url + self.api_path +
                               'wp/v2/pages?page=%d' % page)
            if req.status_code > 400:
                raise WordPressApiNotV2
            if type(req.json()) is list and len(req.json()) > 0:
                self.pages += req.json()
            else:
                more_pages = False
            page += 1
        return self.pages
