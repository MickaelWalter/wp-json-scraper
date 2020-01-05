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


class Console:
    """
    A little helper class to allow console management (like color)
    """
    normal = "\033[0m"
    blue = "\033[94m"
    green = "\033[92m"
    red = "\033[31m"

    @staticmethod
    def wipe_color():
        """
        Deactivates color in terminal
        """
        Console.normal = ""
        Console.blue = ""
        Console.green = ""
        Console.red = ""

    @staticmethod
    def log_info(text):
        """
        Prints information log to the console
        param text: the text to display
        """
        print()
        print(Console.blue + "[*] " + text + Console.normal)

    @staticmethod
    def log_error(text):
        """
        Prints error log to the console
        param text: the text to display
        """
        print()
        print(Console.red + "[!] " + text + Console.normal)

    @staticmethod
    def log_success(text):
        """
        Prints error log to the console
        param text: the text to display
        """
        print(Console.green + "[+] " + text + Console.normal)
