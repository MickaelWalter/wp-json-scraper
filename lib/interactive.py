"""
Copyright (c) 2018-2020 Mickaël "Kilawyn" Walter

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

import cmd
import argparse
import shlex
import sys
import re
import copy

from lib.wpapi import WPApi, WordPressApiNotV2
from lib.requestsession import RequestSession
from lib.console import Console
from lib.infodisplayer import InfoDisplayer
from lib.exporter import Exporter
from lib.utils import get_by_id

class ArgumentParser(argparse.ArgumentParser):
    """
    Wrapper for argparse.ArgumentParser (especially the help function that quits the application after display)
    """
    def __init__(self, prog="", description=""):
        argparse.ArgumentParser.__init__(self, prog=prog, add_help=False, description=description)
        self.add_argument("--help", "-h", help="print this help", action="store_true")
        self.should_help = True

    def custom_parse_args(self, args):
        args = self.parse_args(shlex.split(args))
        if args.help:
            if self.should_help:
                self.print_help(sys.stdout)
                print()
            self.should_help = False
            return None
        if self.should_help:
            return args
        else:
            return None

    def error(self, message):
        if self.should_help:
            self.print_help(sys.stdout)
            print()
            self.should_help = False

class InteractiveShell(cmd.Cmd):
    """
    The interactive shell for the application
    """
    intro = """
    Entering interactive session
    Use the 'help' command to get a list of available commands and parameters, 'exit' to quit
    `command -h` gives more details about a command
    """
    prompt = "> "

    def __init__(self, target, session, version):
        cmd.Cmd.__init__(self)
        self.target = target
        InteractiveShell.prompt = Console.red + target + Console.normal + " > "
        self.session = session
        self.version = version
        self.scanner = WPApi(self.target, session=session)

    @staticmethod
    def export_decorator(export_func, is_all, export_str, json, csv, values, kwargs = {}):
        if json is not None:
            json_file = json
            if is_all:
                json_file = json + "-" + export_str
            args = [values]
            args.append(Exporter.JSON)
            args.append(json_file)
            export_func(*args, **kwargs)
        if csv is not None:
            csv_file = csv
            if is_all:
                csv_file = csv + "-" + export_str
            args = [values]
            args.append(Exporter.CSV)
            args.append(csv_file)
            export_func(*args, **kwargs)
    
    def get_fetch_or_list_type(self, obj_type, plural=False):
        """
            Returns a dict containing all necessary metadata
             about the obj_type to list and fetch data

            :param obj_type: the type of the object
            :param plural: whether the name must be plural or not
        """
        display_func = None
        export_func = None
        additional_info = {}
        obj_name = ""
        if obj_type == WPApi.USER:
            display_func = InfoDisplayer.display_users
            export_func = Exporter.export_users
            additional_info = {}
            obj_name = "Users" if plural else "User"
        elif obj_type == WPApi.TAG:
            display_func = InfoDisplayer.display_tags
            export_func = Exporter.export_tags
            additional_info = {}
            obj_name = "Tags" if plural else "Tag"
        elif obj_type == WPApi.CATEGORY:
            display_func = InfoDisplayer.display_categories
            export_func = Exporter.export_categories
            additional_info = {
                'category_list': self.scanner.categories
            }
            obj_name = "Categories" if plural else "Category"
        elif obj_type == WPApi.POST:
            display_func = InfoDisplayer.display_posts
            export_func = Exporter.export_posts
            additional_info = {
                'tags_list': self.scanner.tags,
                'categories_list': self.scanner.categories,
                'users_list': self.scanner.users
            }
            obj_name = "Posts" if plural else "Post"
        elif obj_type == WPApi.PAGE:
            display_func = InfoDisplayer.display_pages
            export_func = Exporter.export_pages
            additional_info = {
                'parent_pages': self.scanner.pages,
                'users': self.scanner.users
            }
            obj_name = "Pages" if plural else "Page"
        elif obj_type == WPApi.COMMENT:
            display_func = InfoDisplayer.display_comments
            export_func = Exporter.export_comments_interactive
            additional_info = {
                #'parent_posts': self.scanner.posts, # May be too verbose
                'users': self.scanner.users
            }
            obj_name = "Comments" if plural else "Comment"
        elif obj_type == WPApi.MEDIA:
            display_func = InfoDisplayer.display_media
            export_func = Exporter.export_media
            additional_info = {'users': self.scanner.users}
            obj_name = "Media"
        elif obj_type == WPApi.NAMESPACE:
            display_func = InfoDisplayer.display_namespaces
            export_func = Exporter.export_media
            additional_info = {}
            obj_name = "Namespaces" if plural else "Namespace"

        return {
            "display_func": display_func,
            "export_func": export_func,
            "additional_info": additional_info,
            "obj_name": obj_name
        }

    def fetch_obj(self, obj_type, obj_id, cache=True, json=None, csv=None):
        """
            Displays and exports (if relevant) the object fetched by ID

            :param obj_type: the type of the object
            :param obj_id: the ID of the obj
            :param cache: whether to use the cache of not
            :param json: json export filename
            :param csv: csv export filename
        """
        prop = self.get_fetch_or_list_type(obj_type)
        print(prop["obj_name"] + " details")
        try:
            obj = self.scanner.get_obj_by_id(obj_type, obj_id, use_cache=cache)
            if len(obj) == 0:
                Console.log_info(prop["obj_name"] + " not found\n")
            else:
                prop["display_func"](obj, details=True)
                if len(prop["additional_info"].keys()) > 0:
                    InteractiveShell.export_decorator(prop["export_func"], False, "", json, csv, obj, prop["additional_info"])
                else:
                    InteractiveShell.export_decorator(prop["export_func"], False, "", json, csv, obj)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")
        except IOError as e:
            Console.log_error("Could not open %s for writing" % e.filename)
        print()
    
    def list_obj(self, obj_type, start, limit, is_all=False, cache=True, json=None, csv=None):
        """
            Displays and exports (if relevant) the object list

            :param obj_type: the type of the object
            :param start: the offset of the first object
            :param limit: the maximum number of objects to list
            :param is_all: are all object types requested?
            :param cache: whether to use the cache of not
            :param json: json export filename
            :param csv: csv export filename
        """
        prop = self.get_fetch_or_list_type(obj_type, plural=True)
        print(prop["obj_name"] + " details")
        try:
            kwargs = {}
            if obj_type == WPApi.POST:
                kwargs = {"comments": False}
            obj_list = self.scanner.get_obj_list(obj_type, start, limit, cache, kwargs=kwargs)
            prop["display_func"](obj_list)
            InteractiveShell.export_decorator(prop["export_func"], is_all, prop["obj_name"].lower(), json, csv, obj_list)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")
        except IOError as e:
            Console.log_error("Could not open %s for writing" % e.filename)
        print()

    def do_exit(self, arg):
        'Exit wp-json-scraper'
        return True
    
    def do_show(self, arg):
        'Shows information about parameters in memory'
        parser = ArgumentParser(prog='show', description='show information about global parameters')
        parser.add_argument("what", choices=['all', 'target', 'proxy', 'cookies', 'credentials', 'version'],
        help='choose the information to be displayed', default='all')
        args = parser.custom_parse_args(arg)
        if args is None:
            return
        if args.what == 'all' or args.what == 'target':
            print("Target: %s" % self.target)
        if args.what == 'all' or args.what == 'proxy':
            proxies = self.session.get_proxies()
            if proxies is not None and len(proxies) > 0:
                print ("Proxies:")
                for key, value in proxies.items():
                    print("\t%s: %s" % (key, value))
            else:
                print ("Proxy: none")
        if args.what == 'all' or args.what == 'cookies':
            cookies = self.session.get_cookies()
            if len(cookies) > 0:
                print("Cookies:")
                for key, value in cookies.items():
                    print("\t%s: %s" % (key, value))
            else:
                print("Cookies: none")
        if args.what == 'all' or args.what == 'credentials':
            credentials = self.session.get_creds()
            if credentials is not None:
                creds_str = "Credentials: "
                for el in credentials:
                    creds_str += el + ":"
                print(creds_str[:-1])
            else:
                print("Credentials: none")
        if args.what == 'all' or args.what == 'version':
            print("WPJsonScraper version: %s" % self.version)
        print()
    
    def do_set(self, arg):
        'Sets a global parameter of WPJsonScanner'
        parser = ArgumentParser(prog='set', description='sets global parameters for WPJsonScanner')
        parser.add_argument("what", choices=['target', 'proxy', 'cookies', 'credentials'],
        help='the parameter to set')
        parser.add_argument("value", type=str, help='the new value of the parameter (for cookies, set as cookie string: "n1=v1; n2=v2")')
        args = parser.custom_parse_args(arg)
        if args is None:
            return
        if args.what == 'target':
            self.target = args.value
            if re.match(r'^https?://.*$', self.target) is None:
                self.target = "http://" + self.target
            if re.match(r'^.+/$', self.target) is None:
                self.target += "/"
            InteractiveShell.prompt = Console.red + self.target + Console.normal + " > "
            print("target = %s" % args.value)
            self.scanner = WPApi(self.target, session=self.session)
            Console.log_info("Cache is erased but session stays the same (with cookies and authorization)")
        elif args.what == 'proxy':
            self.session.set_proxy(args.value)
            print("proxy = %s" % args.value)
        elif args.what == 'cookies':
            self.session.set_cookies(args.value)
            print("Cookies set!")
        elif args.what == "credentials":
            authorization_list = args.value.split(':')
            if len(authorization_list) == 1:
                authorization = (authorization_list[0], '')
            elif len(authorization_list) >= 2:
                authorization = (authorization_list[0],
                ':'.join(authorization_list[1:]))
            self.session.set_creds(authorization)
            print("Credentials set!")
        print()

    def do_list(self, arg):
        'Gets the list of something from the server'
        parser = ArgumentParser(prog='list', description='gets a list of something from the server')
        parser.add_argument("what", choices=[
            'posts', 
            #'post-revisions', 
            #'wp-blocks', 
            'categories',
            'tags',
            'pages',
            'comments',
            'media',
            'users',
            #'themes',
            #'search-results',
            'namespaces',
            'all',
            ],
            help='what to list')
        parser.add_argument("--json", "-j", help="list and store as json to the specified file")
        parser.add_argument("--csv", "-c", help="list and store as csv to the specified file")
        parser.add_argument("--limit", "-l", type=int, help="limit the number of results")
        parser.add_argument("--start", "-s", type=int, help="start at the given index")
        parser.add_argument("--no-cache", dest="cache", action="store_false", help="don't lookup in cache and ask the server")
        args = parser.custom_parse_args(arg)
        if args is None:
            return
        # The checks must be ordered by dependencies
        kwargs = {
            "start": args.start, 
            "limit": args.limit, 
            "is_all": args.what == "all", 
            "cache": args.cache, 
            "json": args.json, 
            "csv": args.csv
        }
        if args.what == "all" or args.what == "users":
            self.list_obj(WPApi.USER, **kwargs)
        if args.what == "all" or args.what == "tags":
            self.list_obj(WPApi.TAG, **kwargs)
        if args.what == "all" or args.what == "categories":
            self.list_obj(WPApi.CATEGORY, **kwargs)
        if args.what == "all" or args.what == "posts":
            self.list_obj(WPApi.POST, **kwargs)
        if args.what == "all" or args.what == "pages":
            self.list_obj(WPApi.PAGE, **kwargs)
        if args.what == "all" or args.what == "comments":
            self.list_obj(WPApi.COMMENT, **kwargs)
        if args.what == "all" or args.what == "media":
            self.list_obj(WPApi.MEDIA, **kwargs)
        if args.what == "all" or args.what == "namespaces":
            self.list_obj(WPApi.NAMESPACE, **kwargs)

    def do_fetch(self, arg):
        'Fetches a specific content specified by ID'
        parser = ArgumentParser(prog='fetch', description='fetches something from the server or the cache by ID')
        parser.add_argument("what", choices=[
            'post', 
            #'post-revision', 
            #'wp-block', 
            'category',
            'tag',
            'page',
            'comment',
            'media',
            'user',
            #'theme',
            #'search-result',
            ],
            help='what to fetch')
        parser.add_argument("id", type=int, help='the ID of the content to fetch')
        parser.add_argument("--json", "-j", help="list and store as json to the specified file")
        parser.add_argument("--csv", "-c", help="list and store as csv to the specified file")
        parser.add_argument("--no-cache", dest="cache", action="store_false", help="don't lookup in cache and ask the server")
        args = parser.custom_parse_args(arg)
        what_type = None
        if args is None:
            return
        what_type = WPApi.str_type_to_native(args.what)
        
        if what_type is not None:
            self.fetch_obj(what_type, args.id, cache=args.cache, json=args.json, csv=args.csv)
        else:
            print("Not implemented")
            print()
    
    def do_search(self, arg):
        'Looks for specific keywords in the WordPress API'
        parser = ArgumentParser(prog='search', description='searches something from the server')
        parser.add_argument("--type", "-t", action="append", choices=[
            'all',
            'post', 
            #'post-revision', 
            #'wp-block', 
            'category',
            'tag',
            'page',
            'comment',
            'media',
            'user',
            #'theme',
            #'search-result',
            ],
            help='the types to look for (default all)',
            dest='what'
            )
        parser.add_argument("keywords", help='the keywords to look for')
        parser.add_argument("--json", "-j", help="list and store as json to the specified file(s)")
        parser.add_argument("--csv", "-c", help="list and store as csv to the specified file(s)")
        parser.add_argument("--limit", "-l", type=int, help="limit the number of results")
        parser.add_argument("--start", "-s", type=int, help="start at the given index")
        args = parser.custom_parse_args(arg)
        if args is None:
            return
        what_types = WPApi.convert_obj_types_to_list(args.what)
        results = self.scanner.search(what_types, args.keywords, args.start, args.limit)
        print()
        for k, v in results.items():
            prop = self.get_fetch_or_list_type(k, plural=True)
            print(prop["obj_name"] + " details")
            if len(v) == 0:
                Console.log_info("No result")
            else:
                try:
                    prop["display_func"](v)
                    InteractiveShell.export_decorator(
                        prop["export_func"],
                        len(what_types) > 1 or WPApi.ALL_TYPES in what_types,
                        prop["obj_name"].lower(),
                        args.json,
                        args.csv,
                        v
                    )
                except WordPressApiNotV2:
                    Console.log_error("The API does not support WP V2")
                except IOError as e:
                    Console.log_error("Could not open %s for writing" % e.filename)
            print()

def start_interactive(target, session, version):
    """
    Starts a new interactive session
    """
    InteractiveShell(target, session, version).cmdloop()