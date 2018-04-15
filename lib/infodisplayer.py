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

import html

from lib.console import Console

class InfoDisplayer:
    """
    Static class to display information for different categories
    """

    @staticmethod
    def display_basic_info(information):
        """
        Displays basic information about the WordPress instance
        param information: information as a JSON object
        """
        print()

        if 'name' in information.keys():
            print("Site name: %s" % html.unescape(information['name']))

        if 'description' in information.keys():
            print("Site description: %s" %
                  html.unescape(information['description']))

        if 'home' in information.keys():
            print("Site home: %s" % html.unescape(information['home']))

        if 'gmt_offset' in information.keys():
            timezone_string = ""
            gmt_offset = information['gmt_offset']
            if '-' not in gmt_offset:
                gmt_offset = '+' + gmt_offset
            if 'timezone_string' in information.keys():
                timezone_string = information['timezone_string']
            print("Site Timezone: %s (GMT%s)" % (timezone_string, gmt_offset))

        if 'namespaces' in information.keys():
            print('Namespaces (API provided by addons):')
            for ns in information['namespaces']:
                tip = ""
                if ns == 'oembed/1.0':
                    tip = " - Allows embedded representation of a URL"
                elif ns == 'wp/v2':
                    tip = " - The API integrated by default with WordPress 4.7"
                print('    %s%s' % (ns, tip))

        # TODO, dive into authentication
        print()

    @staticmethod
    def display_endpoints(information):
        """
        Displays endpoint documentation of the WordPress API
        param information: information as a JSON object
        """
        print()

        if 'routes' not in information.keys():
            Console.log_error("Did not find the routes for endpoint discovery")
            return None

        for url, route in information['routes'].items():
            print("%s (Namespace: %s)" % (url, route['namespace']))
            for endpoint in route['endpoints']:
                methods = "    "
                first = True
                for method in endpoint['methods']:
                    if first:
                        methods += method
                        first = False
                    else:
                        methods += ", " + method
                print(methods)
                if len(endpoint['args']) > 0:
                    for arg, props in endpoint['args'].items():
                        required = ""
                        if props['required']:
                            required = " (required)"
                        print("        " + arg + required)
                        if 'type' in props.keys():
                            print("            type: " + str(props['type']))
                        if 'default' in props.keys():
                            print("            default: " +
                                  str(props['default']))
                        if 'enum' in props.keys():
                            allowed = "            allowed values: "
                            first = True
                            for val in props['enum']:
                                if first:
                                    allowed += val
                                    first = False
                                else:
                                    allowed += ", " + val
                            print(allowed)
                        if 'description' in props.keys():
                            print("            " + str(props['description']))
            print()

    @staticmethod
    def display_posts(information):
        """
        Displays posts published on the WordPress instance
        param information: information as a JSON object
        """
        print()
        for post in information:
            line = ""
            if 'id' in post.keys():
                line += "ID: %d" %post['id']
            if 'title' in post.keys():
                line += " - " + html.unescape(post['title']['rendered'])
            if 'link' in post.keys():
                line += " - " + post['link']
            print(line)
        print()

    @staticmethod
    def display_users(information):
        """
        Displays users on the WordPress instance
        param information: information as a JSON object
        """
        print()
        for user in information:
            line = ""
            if 'id' in user.keys():
                line += "User ID: %d\n" % user['id']
            if 'name' in user.keys():
                line += "    Display name: %s\n" % user['name']
            if 'slug' in user.keys():
                line += "    User name (probable): %s\n" % user['slug']
            if 'description' in user.keys():
                line += "    User description: %s\n" % user['description']
            if 'url' in user.keys():
                line += "    User website: %s\n" % user['url']
            if 'link' in user.keys():
                line += "    User personal page: %s\n" % user['link']
            print(line)
        print()

    @staticmethod
    def display_categories(information):
        """
        Displays categories of the WordPress instance
        param information: information as a JSON object
        """
        print()
        for category in information:
            line = ""
            if 'id' in category.keys():
                line += "Category ID: %d\n" % category['id']
            if 'name' in category.keys():
                line += "    Name: %s\n" % category['name']
            if 'description' in category.keys():
                line += "    Description: %s\n" % category['description']
            if 'count' in category.keys():
                line += "    Number of posts: %d\n" % category['count']
            if 'link' in category.keys():
                line += "    User personal page: %s\n" % category['link']
            print(line)
        print()
