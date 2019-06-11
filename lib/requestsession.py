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

from lib.console import Console

class ConnectionCouldNotResolve(Exception):
    pass

class ConnectionReset(Exception):
    pass

class ConnectionRefused(Exception):
    pass

class ConnectionTimeout(Exception):
    pass

class HTTPError400(Exception):
    pass

class HTTPError401(Exception):
    pass

class HTTPError403(Exception):
    pass

class HTTPError404(Exception):
    pass

class HTTPError500(Exception):
    pass

class HTTPError502(Exception):
    pass

class HTTPError(Exception):
    pass

class RequestSession:
    """
    Wrapper to handle the requests library with session support
    """

    def __init__(self, proxy=None, cookies=None, authorization=None):
        """
        Creates a new RequestSession instance
        param proxy: a dict containing a proxy server string for HTTP and/or
        HTTPS connection
        param cookies: a string in the format of the Cookie header
        param authorization: a tuple containing login and password or
        requests.auth.HTTPBasicAuth for basic authentication or
        requests.auth.HTTPDigestAuth for NTLM-like authentication
        """
        self.s = requests.Session()
        if proxy is not None:
            prot = 'http'
            if proxy[:5].lower() == 'https':
                prot = 'https'
            self.s.proxies = {prot: proxy}
        if cookies is not None:
            self.s.headers.update({'Cookie': cookies})
        if authorization is not None and (
            type(authorization) is tuple and len(authorization) == 2 or
            type(authorization) is requests.auth.HTTPBasicAuth or
            type(authorization) is requests.auth.HTTPDigestAuth):
            self.s.auth = authorization

    def get(self, url):
        """
        Calls the get function from requests but handles errors to raise proper
        exception following the context
        """
        return self.do_request("get", url)


    def post(self, url, data=None):
        """
        Calls the post function from requests but handles errors to raise proper
        exception following the context
        """
        return self.do_request("post", url, data)

    def do_request(self, method, url, data=None):
        """
        Helper class to regroup requests and handle exceptions at the same
        location
        """
        response = None
        try:
            if method == "post":
                response = self.s.post(url, data)
            else:
                response = self.s.get(url)
        except requests.ConnectionError as e:
            if "Errno -5" in str(e) or "Errno -2" in str(e)\
              or "Errno -3" in str(e):
                Console.log_error("Could not resolve host %s" % url)
                raise ConnectionCouldNotResolve
            elif "Errno 111" in str(e):
                Console.log_error("Connection refused by %s" % url)
                raise ConnectionRefused
            elif "RemoteDisconnected" in str(e):
                Console.log_error("Connection reset by %s" % url)
                raise ConnectionReset
            else:
                print(e)
                raise e
        except Exception as e:
            raise e

        if response.status_code == 400:
            raise HTTPError400
        elif response.status_code == 401:
            Console.log_error("Error 401 (Unauthorized) while trying to fetch"
            " the API")
            raise HTTPError401
        elif response.status_code == 403:
            Console.log_error("Error 403 (Authorization Required) while trying"
            " to fetch the API")
            raise HTTPError403
        elif response.status_code == 404:
            raise HTTPError404
        elif response.status_code == 500:
            Console.log_error("Error 500 (Internal Server Error) while trying"
            " to fetch the API")
            raise HTTPError500
        elif response.status_code == 502:
            Console.log_error("Error 502 (Bad Gateway) while trying"
            " to fetch the API")
            raise HTTPError404
        elif response.status_code > 400:
            Console.log_error("Error %d while trying to fetch the API" %
            response.status_code)
            raise HTTPError

        return response
