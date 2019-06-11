"""
Copyright (c) 2018-2019 Mickaël "Kilawyn" Walter

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
from urllib.parse import urlencode

from json.decoder import JSONDecodeError

from lib.exceptions import NoWordpressApi, WordPressApiNotV2, \
                            NSNotFoundException
from lib.requestsession import RequestSession, HTTPError400
from lib.utils import url_path_join, print_progress_bar

class WPApi:
    """
    Queries the WordPress API to retrieve information
    """

    def __init__(self, target, api_path="wp-json/", session=None,
                 search_terms=None):
        """
        Creates a new instance of WPApi
        param target: the target of the scan
        param api_path: the api path, if non-default
        param session: the requests session object to use for HTTP requests
        param search_terms : the terms of the keyword search, if any
        """
        self.api_path = api_path
        self.search_terms = search_terms
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
        self.s = None
        self.comments_loaded = False
        self.orphan_comments = []

        if session is not None:
            self.s = session
        else:
            self.s = RequestSession()

    def get_orphans_comments(self):
        """
        Returns the list of comments for which a post hasn't been found
        """
        return self.orphan_comments

    def get_basic_info(self):
        """
        Collects and stores basic information about the target
        """
        rest_url = url_path_join(self.url, self.api_path)
        if self.basic_info is not None:
            return self.basic_info

        try:
            req = self.s.get(rest_url)
        except Exception:
            raise NoWordpressApi
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

    def crawl_pages(self, url):
        """
        Crawls all pages while there is at least one result for the given
        endpoint
        """
        page = 1
        total_entries = 0
        total_pages = 0
        more_entries = True
        entries = []
        base_url = url
        if self.search_terms is not None:
            if '?' in base_url:
                base_url += '&' + urlencode({'search': self.search_terms})
            else:
                base_url += '?' + urlencode({'search': self.search_terms})
        while more_entries:
            rest_url = url_path_join(self.url, self.api_path, (base_url % page))
            try:
                req = self.s.get(rest_url)
                if page == 1 and 'X-WP-Total' in req.headers:
                    total_entries = int(req.headers['X-WP-Total'])
                    total_pages = int(req.headers['X-WP-TotalPages'])
                    print("Number of entries: %d" % total_entries)
            except HTTPError400:
                break
            except Exception:
                raise WordPressApiNotV2
            try:
                if type(req.json()) is list and len(req.json()) > 0:
                    entries += req.json()
                    if total_entries > 0:
                        print_progress_bar(page, total_pages,
                        length=70)
                else:
                    more_entries = False
            except JSONDecodeError:
                more_entries = False

            page += 1

        return entries

    def get_all_posts(self, comments=False):
        """
        Retrieves all posts
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if not self.has_v2:
            raise WordPressApiNotV2
        if self.posts is not None and (self.comments_loaded and comments or not comments):
            return self.posts
        elif self.posts is None:
            self.posts = self.crawl_pages('wp/v2/posts?page=%d')
        if not self.comments_loaded and comments:
            # Load comments
            comment_list = self.crawl_pages('wp/v2/comments?page=%d')
            for comment in comment_list:
                found_post = False
                for i in range(0, len(self.posts)):
                    if self.posts[i]['id'] == comment['post']:
                        if "comments" not in self.posts[i]:
                            self.posts[i]['comments'] = []
                        self.posts[i]["comments"].append(comment)
                        found_post = True
                        break
                if not found_post:
                    self.orphan_comments.append(comment)
            self.comments_loaded = True
        
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

        self.tags = self.crawl_pages('wp/v2/tags?page=%d')
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

        self.categories = self.crawl_pages('wp/v2/categories?page=%d')
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

        self.users = self.crawl_pages('wp/v2/users?page=%d')
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

        self.media = self.crawl_pages('wp/v2/media?page=%d')
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

        self.pages = self.crawl_pages('wp/v2/pages?page=%d')
        return self.pages

    def get_namespaces(self):
        """
        Retrieves an array of namespaces
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if 'namespaces' in self.basic_info.keys():
            return self.basic_info['namespaces']
        return []

    def get_routes(self):
        """
        Retrieves an array of namespaces
        """
        if self.has_v2 is None:
            self.get_basic_info()
        if 'routes' in self.basic_info.keys():
            return self.basic_info['routes']
        return []

    def crawl_namespaces(self, ns):
        """
        Crawls all accessible get routes defined for the specified namespace.
        """
        namespaces = self.get_namespaces()
        routes = self.get_routes()
        ns_data = {}
        if ns != "all" and ns not in namespaces:
            raise NSNotFoundException
        for url, route in routes.items():
            if 'namespace' not in route.keys() \
               or 'endpoints' not in route.keys():
                continue
            url_as_ns = url.lstrip('/')
            if '(?P<' in url or url_as_ns in namespaces:
                continue
            if ns != 'all' and route['namespace'] != ns or \
               route['namespace'] in ['wp/v2', '']:
                continue
            for endpoint in route['endpoints']:
                if 'GET' not in endpoint['methods']:
                    continue
                keep = True
                if len(endpoint['args']) > 0 and type(endpoint['args']) is dict:
                    for name,arg in endpoint['args'].items():
                        if arg['required']:
                            keep = False
                if keep:
                    rest_url = url_path_join(self.url, self.api_path, url)
                    try:
                        ns_request = self.s.get(rest_url)
                        ns_data[url] = ns_request.json()
                    except Exception:
                        continue
        return ns_data
