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

import json

from urllib.parse import urlsplit, urlunsplit

def get_by_id(value, id):
    """
    Utility function to retrieve a value by and ID in a list of dicts, returns
    None of no correspondance have been made
    param value: the dict to process
    param id: the id to get
    """
    if value is None:
        return None
    for val in value:
        if 'id' in val.keys() and val['id'] == id:
            return val
    return None

# Neat code part from https://codereview.stackexchange.com/questions/13027/joini
# ng-url-path-components-intelligently
def url_path_join(*parts):
    """Normalize url parts and join them with a slash."""
    schemes, netlocs, paths, queries, fragments = \
    zip(*(urlsplit(part) for part in parts))
    scheme = first(schemes)
    netloc = first(netlocs)
    path = '/'.join(x.strip('/') for x in paths if x)
    query = first(queries)
    fragment = first(fragments)
    return urlunsplit((scheme, netloc, path, query, fragment))

def first(sequence, default=''):
    return next((x for x in sequence if x), default)

# Code from https://stackoverflow.com/questions/3173320/text-progress-bar-in-th
# e-console

def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1,\
 length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent \
        complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    try:
      percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / \
      float(total)))
      filledLength = int(length * iteration // total)
    except:
      percent = 0
      filledLength = 0

    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def get_content_as_json (response_obj):
    """
    When a BOM is present (see issue #2), UTF-8 is not properly decoded by 
    Response.json() method. This is a helper function that returns a json value 
    even if a BOM is present in UTF-8 text
    @params:
        response_obj: a requests Response instance
    @returns: a decoded json object (list or dict)
    """
    if response_obj.content[:3]== b'\xef\xbb\xbf': # UTF-8 BOM
        content = response_obj.content.decode("utf-8-sig")
        return json.loads(content)
    else:
        try:
            return response_obj.json()
        except:
            return {}
