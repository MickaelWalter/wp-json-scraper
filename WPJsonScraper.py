#!/usr/bin/env python3

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

import argparse
import requests
import re

from lib.console import Console
from lib.wpapi import WPApi
from lib.infodisplayer import InfoDisplayer
from lib.exceptions import NoWordpressApi, WordPressApiNotV2, \
                            NSNotFoundException
from lib.exporter import Exporter
from lib.requestsession import RequestSession
from lib.interactive import start_interactive

version = '0.4.1'

def main():
    parser = argparse.ArgumentParser(description=
"""Reads a WP-JSON API on a WordPress installation to retrieve a maximum of
publicly available information. These information comprise, but not only:
posts, comments, pages, medias or users. As this tool could allow to access
confidential (but not well-protected) data, it is recommended that you get
first a written permission from the site owner. The author won\'t endorse any
liability for misuse of this software""",
    epilog=
"""(c) 2018-2020 Mickaël "Kilawyn" Walter. This program is licensed under the MIT
license, check LICENSE.txt for more information""")
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s ' + version)
    parser.add_argument('target',
                        type=str,
                        help='the base path of the WordPress installation to '
                        'examine')
    parser.add_argument('-i',
                        '--info',
                        dest='info',
                        action='store_true',
                        help='dumps basic information about the WordPress '
                        'installation')
    parser.add_argument('-e',
                        '--endpoints',
                        dest='endpoints',
                        action='store_true',
                        help='dumps full endpoint documentation')
    parser.add_argument('-p',
                        '--posts',
                        dest='posts',
                        action='store_true',
                        help='lists published posts')
    parser.add_argument('--export-posts',
                        dest='post_export_folder',
                        action='store',
                        help='export posts to a specified destination folder')
    parser.add_argument('-u',
                        '--users',
                        dest='users',
                        action='store_true',
                        help='lists users')
    parser.add_argument('-t',
                        '--tags',
                        dest='tags',
                        action='store_true',
                        help='lists tags')
    parser.add_argument('-c',
                        '--categories',
                        dest='categories',
                        action='store_true',
                        help='lists categories')
    parser.add_argument('-m',
                        '--media',
                        dest='media',
                        action='store_true',
                        help='lists media objects')
    parser.add_argument('-g',
                        '--pages',
                        dest='pages',
                        action='store_true',
                        help='lists pages')
    parser.add_argument('-o',
                        '--comments',
                        dest='comments',
                        action='store_true',
                        help="lists comments")
    parser.add_argument('--export-pages',
                        dest='page_export_folder',
                        action='store',
                        help='export pages to a specified destination folder')
    parser.add_argument('--export-comments',
                        dest='comment_export_folder',
                        action='store',
                        help='export comments to a specified destination folder')
    parser.add_argument('-r',
                        '--crawl-ns',
                        dest='crawl_ns',
                        action='store',
                        help='crawl all GET routes of the specified namespace '
                        'or all namespaces if all is specified')
    parser.add_argument('-a',
                        '--all',
                        dest='all',
                        action='store_true',
                        help='dumps all available information from the '
                        'target API')
    parser.add_argument('-S',
                        '--search',
                        dest='search',
                        action='store',
                        help='search for a string on the WordPress instance. '
                        'If one or several flag in agpmctu are set, search '
                        'only on these')
    parser.add_argument('--proxy',
                        dest='proxy_server',
                        action='store',
                        help='define a proxy server to use, e.g. for '
                        'enterprise network or debugging')
    parser.add_argument('--auth',
                        dest='credentials',
                        action='store',
                        help='define a username and a password separated by '
                        'a colon to use them as basic authentication')
    parser.add_argument('--cookies',
                        dest='cookies',
                        action='store',
                        help='define specific cookies to send with the request '
                        'in the format cookie1=foo; cookie2=bar')
    parser.add_argument('--no-color',
                        dest='nocolor',
                        action='store_true',
                        help='remove color in the output (e.g. to pipe it)')
    parser.add_argument('--interactive',
                        dest='interactive',
                        action='store_true',
                        help='start an interactive session')


    args = parser.parse_args()

    motd = """
 _    _______  ___                  _____
| |  | | ___ \\|_  |                /  ___|
| |  | | |_/ /  | | ___  ___  _ __ \\ `--.  ___ _ __ __ _ _ __   ___ _ __
| |/\\| |  __/   | |/ __|/ _ \\| '_ \\ `--. \\/ __| '__/ _` | '_ \\ / _ \\ '__|
\\  /\\  / |  /\\__/ /\\__ \\ (_) | | | /\\__/ / (__| | | (_| | |_) |  __/ |
 \\/  \\/\\_|  \\____/ |___/\\___/|_| |_\\____/ \\___|_|  \\__,_| .__/ \\___|_|
                                                        | |
                                                        |_|
    WPJsonScraper v%s
    By Mickaël \"Kilawyn\" Walter

    Make sure you use this tool with the approval of the site owner. Even if
    these information are public or available with proper authentication, this
    could be considered as an intrusion.

    Target: %s

    """ % (version, args.target)

    print(motd)

    if args.nocolor:
        Console.wipe_color()

    Console.log_info("Testing connectivity with the server")

    target = args.target
    if re.match(r'^https?://.*$', target) is None:
        target = "http://" + target
    if re.match(r'^.+/$', target) is None:
        target += "/"

    proxy = None
    if args.proxy_server is not None:
        proxy = args.proxy_server
    cookies = None
    if args.cookies is not None:
        cookies = args.cookies
    authorization = None
    if args.credentials is not None:
        authorization_list = args.credentials.split(':')
        if len(authorization_list) == 1:
            authorization = (authorization_list[0], '')
        elif len(authorization_list) >= 2:
            authorization = (authorization_list[0],
              ':'.join(authorization_list[1:]))
    session = RequestSession(proxy=proxy, cookies=cookies,
      authorization=authorization)
    try:
        Console.log_success("Connection OK")
    except Exception as e:
        exit(0)
    
    # Quite an ugly check to launch a search on all parameters edible 
    # Should find something better (maybe in argparser doc?)
    if args.search is not None and not (args.all | args.posts | args.pages | 
        args.users | args.categories | args.tags | args.media):
        Console.log_info("Searching on all available sources")
        args.posts = True
        args.pages = True 
        args.users = True
        args.categories = True
        args.tags = True
        args.media = True

    if args.interactive:
        start_interactive(args.target, session, version)
        return

    scanner = WPApi(target, session=session, search_terms=args.search)
    if args.info or args.all:
        try:
            basic_info = scanner.get_basic_info()
            Console.log_info("General information on the target")
            InfoDisplayer.display_basic_info(basic_info)
        except NoWordpressApi:
            Console.log_error("No WordPress API available at the given URL "
            "(too old WordPress or not WordPress?)")
            exit()
    
    if args.posts or args.all:
        try:
            if args.comments:
                Console.log_info("Post list with comments")
            else:
                Console.log_info("Post list")
            posts_list = scanner.get_all_posts(args.comments)
            InfoDisplayer.display_posts(posts_list, scanner.get_orphans_comments())
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.pages or args.all:
        try:
            Console.log_info("Page list")
            pages_list = scanner.get_all_pages()
            InfoDisplayer.display_pages(pages_list)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.users or args.all:
        try:
            Console.log_info("User list")
            users_list = scanner.get_all_users()
            InfoDisplayer.display_users(users_list)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.endpoints or args.all:
        try:
            Console.log_info("API endpoints")
            basic_info = scanner.get_basic_info()
            InfoDisplayer.display_endpoints(basic_info)
        except NoWordpressApi:
            Console.log_error("No WordPress API available at the given URL "
            "(too old WordPress or not WordPress?)")
            exit()

    if args.categories or args.all:
        try:
            Console.log_info("Category list")
            categories_list = scanner.get_all_categories()
            InfoDisplayer.display_categories(categories_list)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.tags or args.all:
        try:
            Console.log_info("Tags list")
            tags_list = scanner.get_all_tags()
            InfoDisplayer.display_tags(tags_list)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.media or args.all:
        try:
            Console.log_info("Media list")
            media_list = scanner.get_all_media()
            InfoDisplayer.display_media(media_list)
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.crawl_ns is None and args.all:
        args.crawl_ns = "all"

    if args.crawl_ns is not None:
        try:
            if args.crawl_ns == "all":
                Console.log_info("Crawling all namespaces")
            else:
                Console.log_info("Crawling %s namespace" % args.crawl_ns)
            ns_data = scanner.crawl_namespaces(args.crawl_ns)
            InfoDisplayer.display_crawled_ns(ns_data)
        except NSNotFoundException:
            Console.log_error("The specified namespace was not found")
        except Exception as e:
            print(e)

    if args.post_export_folder is not None:
        try:
            posts_list = scanner.get_all_posts()
            tags_list = scanner.get_all_tags()
            categories_list = scanner.get_all_categories()
            users_list = scanner.get_all_users()
            print()
            post_number = Exporter.export_posts(posts_list,
             args.post_export_folder,
             tags_list,
             categories_list,
             users_list)
            if post_number> 0:
                Console.log_success("Exported %d posts to %s" %
                (post_number, args.post_export_folder))
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")

    if args.page_export_folder is not None:
        try:
            pages_list = scanner.get_all_pages()
            users_list = scanner.get_all_users()
            print()
            page_number = Exporter.export_posts(pages_list,
             args.page_export_folder,
             None,
             None,
             users_list)
            if page_number> 0:
                Console.log_success("Exported %d pages to %s" %
                (page_number, args.page_export_folder))
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")
    
    if args.comment_export_folder is not None:
        try:
            post_list = scanner.get_all_posts(True)
            orphan_list = scanner.get_orphans_comments()
            print()
            page_number = Exporter.export_comments(post_list, orphan_list, args.comment_export_folder)
            if page_number > 0:
                Console.log_success("Exported %d comments to %s" %
                (page_number, args.comment_export_folder))
        except WordPressApiNotV2:
            Console.log_error("The API does not support WP V2")


if __name__ == "__main__":
    main()
