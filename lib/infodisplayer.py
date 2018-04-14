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
            print("Site description: %s" % html.unescape(information['description']))
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
    
