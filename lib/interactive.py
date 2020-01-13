import cmd
import argparse
import shlex
import sys

class ArgumentParser(argparse.ArgumentParser):
    """
    Wrapper for argparse.ArgumentParser (especially the help function that quits the application after display)
    """
    def __init__(self, prog=""):
        argparse.ArgumentParser.__init__(self, prog=prog, add_help=False)
        self.add_argument("--help", "-h", help="print this help", action="store_true")
        self.should_help = True

    def custom_parse_args(self, args):
        args = self.parse_args(shlex.split(args))
        if args.help:
            if self.should_help:
                self.print_help(sys.stdout)
            self.should_help = False
            return None
        if self.should_help:
            return args
        else:
            return None

    def error(self, message):
        if self.should_help:
            self.print_help(sys.stdout)
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

    def __init__(self, target, session, proxy, cookies, authorization, version):
        cmd.Cmd.__init__(self)
        self.target = target
        self.session = session
        self.version = version
        self.proxy = proxy
        self.cookies = cookies
        self.authorization = authorization

    def do_exit(self, arg):
        'Exit wp-json-scraper'
        return True
    
    def do_show(self, arg):
        'Shows information about parameters in memory'
        parser = ArgumentParser(prog='show')
        parser.add_argument("what", choices=['all', 'target', 'proxy', 'cookies', 'credentials', 'version'],
        help='choose the information to be displayed', default='all')
        args = parser.custom_parse_args(arg)
        if args is None:
            return
        if args.what == 'all' or args.what == 'target':
            print("Target: %s" % self.target)
        if args.what == 'all' or args.what == 'proxy':
            if self.proxy is not None:
                print("Proxy: %s" % self.proxy)
            else:
                print ("Proxy: none")
        if args.what == 'all' or args.what == 'cookies':
            if self.cookies is not None:
                print("Cookies: %s" % self.cookies)
            else:
                print("Cookies: none")
        if args.what == 'all' or args.what == 'credentials':
            if self.authorization is not None:
                print("Credentials: %s" % "")
            else:
                print("Credentials: none")
        if args.what == 'all' or args.what == 'version':
            print("WPJsonScraper version: %s" % self.version)
        print()
        

def start_interactive(target, session, proxy, cookies, authorization, version):
    """
    Starts a new interactive session
    """
    InteractiveShell(target, session, proxy, cookies, authorization, version).cmdloop()