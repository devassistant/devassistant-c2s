
import argparse
import sys

from da_client import settings

class DAArgumentParser(argparse.ArgumentParser):
    '''ArgumentParser with a custom message when a required subcommand is missing'''

    def error(self, message):
        self.print_usage()
        string = 'Error: '
        if message.startswith('the following arguments are required'):
            string += 'You must select a subassistant!'
        else:
            string += message
        print(string)
        sys.exit(2)


def get_argument_parser(tree, add_help=True, first=True):
    '''Generate an ArgumentParser based on the tree of assistants/actions received

    Note that all dests of all arguments here must be enclosed in __ so we don't
    send them as argument in "run" API call'''
    parser = DAArgumentParser(description='',argument_default=argparse.SUPPRESS, add_help=add_help)
    parser.add_argument('-u', '--unix',
                        nargs='?',
                        metavar='FILENAME',
                        dest='__unix__',
                        help='Connect to a UNIX socket (default: {})'.format(settings.SOCKET_FILENAME))
    parser.add_argument('-t', '--tcp',
                        nargs='?',
                        metavar='HOST:PORT',
                        dest='__tcp__',
                        help='Connect to a TCP server on HOST:PORT (default: {}:{})'.format(settings.SOCKET_HOST, settings.SOCKET_PORT))
    parser.add_argument('-c', '--comm-debug',
                        dest='__comm_debug__',
                        help='Show debug output of communication with server.',
                        action='store_true',
                        default=False)

    if not first:
        # second parsing, we add parser for assistants and the debug option for server
        parser.add_argument('-d', '--debug',
                            dest='__debug__',
                            help='Show debug output of devassistant (may be a verbose a lot!).',
                            action='store_true',
                            default=False)
        if len(tree) > 0:
            subparsers = parser.add_subparsers(dest='subassistant_0')
            subparsers.required = True
            for runnable in tree:
                add_parser_recursive(subparsers, runnable, 1)

    return parser

def add_parser_recursive(parsers, runnable, level):
    parser = parsers.add_parser(name=runnable['name'], description='',argument_default=argparse.SUPPRESS)
    for arg in runnable.get('arguments', []):
        kwargs = arg['kwargs'].copy()
        if isinstance(kwargs.get('action'), list): # DA allows a list [default_iff_used, value]
            del(kwargs['action'])
        # Remove values that ArgumentParser can't understand
        for invalid in ['preserved']:
            try:
                del(kwargs[invalid])
            except KeyError:
                pass
        parser.add_argument(*arg['flags'], **kwargs)
    if runnable['children']:
        subparsers = parser.add_subparsers(dest='subassistant_{}'.format(level))
        subparsers.required = True
        for child in runnable['children']:
            add_parser_recursive(subparsers, child, level+1)


