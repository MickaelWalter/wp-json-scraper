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
        if args.what == "all" or args.what == "users":
            print("Users list")
            try:
                users = self.scanner.get_users(start=args.start, num=args.limit, force=not args.cache)
                InfoDisplayer.display_users(users)
                InteractiveShell.export_decorator(Exporter.export_users, args.what == "all", "users", args.json, args.csv, users)
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        if args.what == "all" or args.what == "tags":
            print("Tags list")
            try:
                tags = self.scanner.get_tags(start=args.start, num=args.limit, force=not args.cache)
                InfoDisplayer.display_tags(tags)
                InteractiveShell.export_decorator(Exporter.export_tags, args.what == "all", "tags", args.json, args.csv, tags)
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        if args.what == "all" or args.what == "categories":
            print("Categories list")
            try:
                categories = self.scanner.get_categories(start=args.start, num=args.limit, force=not args.cache)
                InfoDisplayer.display_categories(categories)
                InteractiveShell.export_decorator(Exporter.export_categories, args.what == "all", "categories", args.json, args.csv, 
                    categories, {'category_list': self.scanner.categories})
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        if args.what == "all" or args.what == "posts":
            print("Posts list")
            try:
                posts = self.scanner.get_posts(comments=False, start=args.start, num=args.limit, force=not args.cache)
                Console.log_success("Got %d entries" % len(posts))
                InfoDisplayer.display_posts(posts)
                InteractiveShell.export_decorator(Exporter.export_posts, args.what == "all", "posts", args.json, args.csv, 
                    posts, 
                    {
                        'tags_list': self.scanner.tags,
                        'categories_list': self.scanner.categories,
                        'users_list': self.scanner.users
                    }
                )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        if args.what == "all" or args.what == "pages":
            print("Pages list")
            try:
                pages = self.scanner.get_pages(start=args.start, num=args.limit, force=not args.cache)
                InfoDisplayer.display_pages(pages)
                InteractiveShell.export_decorator(Exporter.export_pages, args.what == "all", "pages", args.json, args.csv, 
                    pages, 
                    {
                        'parent_pages': self.scanner.pages,
                        'users': self.scanner.users
                    }
                )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        if args.what == "all" or args.what == "comments":
            print("Comments list")
            try:
                comments = self.scanner.get_comments(start=args.start, num=args.limit, force=not args.cache)
                InfoDisplayer.display_comments(comments)
                InteractiveShell.export_decorator(Exporter.export_comments_interactive, args.what == "all", "comments", args.json, 
                    args.csv, comments, 
                    {
                        #'parent_posts': self.scanner.posts, # May be too verbose
                        'users': self.scanner.users
                    }
                )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        if args.what == "all" or args.what == "media":
            print("Media list")
            try:
                media = self.scanner.get_media(start=args.start, num=args.limit, force=not args.cache)
                InfoDisplayer.display_media(media)
                InteractiveShell.export_decorator(Exporter.export_media, args.what == "all", "media", args.json, 
                    args.csv, media, 
                    {
                        'users': self.scanner.users
                    }
                )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()

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
        if args is None:
            return
        if args.what == "user":
            print("User details")
            try:
                user = self.scanner.get_obj_by_id(WPApi.USER, args.id, use_cache=args.cache)
                if len(user) == 0:
                    Console.log_info("User not found\n")
                else:
                    InfoDisplayer.display_users(user, True)
                InteractiveShell.export_decorator(Exporter.export_users, False, "", args.json, args.csv, user)
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        elif args.what == "tag":
            print("Tag details")
            try:
                tag = self.scanner.get_obj_by_id(WPApi.TAG, args.id, use_cache=args.cache)
                if len(tag) == 0:
                    Console.log_info("Tag not found\n")
                else:
                    InfoDisplayer.display_tags(tag, True)
                    InteractiveShell.export_decorator(Exporter.export_tags, False, "", args.json, args.csv, tag)
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        elif args.what == "category":
            print("Category details")
            try:
                category = self.scanner.get_obj_by_id(WPApi.CATEGORY, args.id, use_cache=args.cache)
                if len(category) == 0:
                    Console.log_info("Category not found\n")
                else:
                    if 'parent' in category[0].keys():
                        obj = get_by_id(self.scanner.categories, category[0]['parent'])
                        if obj is not None and 'name' in obj.keys():
                            category[0] = copy.deepcopy(category[0])
                            category[0]['parent'] = "%s (%d)" % (obj['name'], category[0]['parent'])

                    InfoDisplayer.display_categories(category, True)
                    InteractiveShell.export_decorator(Exporter.export_categories, False, "", args.json, args.csv, category)
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        elif args.what == "post":
            print("Post details")
            try:
                post = self.scanner.get_obj_by_id(WPApi.POST, args.id, use_cache=args.cache)
                if len(post) == 0:
                    Console.log_info("Post not found\n")
                else:
                    InfoDisplayer.display_posts(post, details=True)
                    InteractiveShell.export_decorator(Exporter.export_posts, False, "", args.json, args.csv, 
                        post, 
                        {
                            'tags_list': self.scanner.tags,
                            'categories_list': self.scanner.categories,
                            'users_list': self.scanner.users
                        }
                    )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
        elif args.what == "page":
            print("Page details")
            try:
                page = self.scanner.get_obj_by_id(WPApi.PAGE, args.id, use_cache=args.cache)
                if len(page) == 0:
                    Console.log_info("Page not found\n")
                else:
                    InfoDisplayer.display_pages(page, details=True)
                    InteractiveShell.export_decorator(Exporter.export_pages, False, "", args.json, args.csv, 
                        page, 
                        {
                            'parent_pages': self.scanner.pages,
                            'users': self.scanner.users
                        }
                    )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        elif args.what == "comment":
            print("Comment details")
            try:
                comment = self.scanner.get_obj_by_id(WPApi.COMMENT, args.id, use_cache=args.cache)
                if len(comment) == 0:
                    Console.log_info("Comment not found\n")
                else:
                    InfoDisplayer.display_comments(comment, True)
                    InteractiveShell.export_decorator(Exporter.export_comments_interactive, False, "", args.json, 
                        args.csv, comment, 
                        {
                            #'parent_posts': self.scanner.posts, # May be too verbose
                            'users': self.scanner.users
                        }
                    )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        elif args.what == "media":
            print("Media details")
            try:
                media = self.scanner.get_obj_by_id(WPApi.MEDIA, args.id, use_cache=args.cache)
                if len(media) == 0:
                    Console.log_info("Media not found\n")
                else:
                    InfoDisplayer.display_media(media, details=True)
                    InteractiveShell.export_decorator(Exporter.export_media, False, "", args.json, 
                        args.csv, media, 
                        {
                            'users': self.scanner.users
                        }
                    )
            except WordPressApiNotV2:
                Console.log_error("The API does not support WP V2")
            except IOError as e:
                Console.log_error("Could not open %s for writing" % e.filename)
            print()
        else:
            print("Not implemented")
            print()

def start_interactive(target, session, version):
    """
    Starts a new interactive session
    """
    InteractiveShell(target, session, version).cmdloop()