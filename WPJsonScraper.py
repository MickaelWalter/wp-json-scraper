#!/usr/bin/env python3

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

import argparse
import requests
import re

from lib.console import Console
from lib.wpapi import WPApi
from lib.infodisplayer import InfoDisplayer
from lib.exceptions import NoWordpressApi

version = '0.1'

def main():
    parser = argparse.ArgumentParser(description='Reads a WP-JSON API on a WordPress installation to retrieve a maximum of publicly available information. These information comprise, but not only: posts, comments, pages, medias or users. As this tool could allow to access confidential (but not well-protected) data, it is recommended that you get first a written permission from the site owner. The author won\'t endorse any liability for misuse of this software',
    epilog='(c) 2018 Mickaël "Kilawyn" Walter. This program is licensed under the MIT license, check LICENSE.txt for mor information')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
    parser.add_argument('target', type=str,
                        help='the base path of the WordPress installation to examine')
    parser.add_argument('-i', '--info', dest='info', action='store_true',
                        help='dumps basic information about the WordPress installation')
    parser.add_argument('-a', '--all', dest='all', action='store_true',
                        help='dumps all available information from the target API')
    parser.add_argument('--no-color', dest='nocolor', action='store_true',
                        help='remove color in the output (e.g. to pipe it)')

    args = parser.parse_args()

    motd = """
 _    _______  ___                  _____
| |  | | ___ \|_  |                /  ___|
| |  | | |_/ /  | | ___  ___  _ __ \ `--.  ___ _ __ __ _ _ __   ___ _ __
| |/\| |  __/   | |/ __|/ _ \| '_ \ `--. \/ __| '__/ _` | '_ \ / _ \ '__|
\  /\  / |  /\__/ /\__ \ (_) | | | /\__/ / (__| | | (_| | |_) |  __/ |
 \/  \/\_|  \____/ |___/\___/|_| |_\____/ \___|_|  \__,_| .__/ \___|_|
                                                        | |
                                                        |_|
    WPJsonScraper v%s
    By Mickaël \"Kilawyn\" Walter

    Make sure you use this tool with the approval of the site owner. Even if these information are public or available with proper authentication, this could be considered as an intrusion.

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

    try:
        connectivity_check = requests.get(target)
        Console.log_success("Connection OK")
    except requests.ConnectionError as e:
        if "Errno -5" in str(e) or "Errno -2" in str(e):
            Console.log_error("Could not resolve host %s" % target)
        elif "Errno 111" in str(e):
            Console.log_error("Connection refused by %s" % target)
        elif "RemoteDisconnected" in str(e):
            Console.log_error("Connection reset by %s" % target)
        else:
            print(e)
        exit(0)

    scanner = WPApi(target)
    if args.info or args.all:
        try:
            basic_info = scanner.get_basic_info()
            Console.log_info("General information on the target")
            InfoDisplayer.display_basic_info(basic_info)
        except NoWordpressApi:
            Console.log_error("No WordPress API available at the given URL (too old WordPress or not WordPress?)")



if __name__ == "__main__":
    main()
