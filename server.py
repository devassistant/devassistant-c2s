#!/usr/bin/python3

import sys
import argparse
import logging
import socketserver

from client_server import handlers, helpers, settings
from client_server.logger import logger

if __name__ == '__main__':

    ap = argparse.ArgumentParser(usage='DevAssistant server. If no arguments are provided, the UNIX server is started',
                                 argument_default=argparse.SUPPRESS)
    ap.add_argument('--unix',
                    nargs='?',
                    metavar='FILENAME',
                    help='Run a UNIX socket server listening on a filename (default: {})'.format(settings.SOCKET_FILENAME))
    ap.add_argument('--tcp',
                    nargs='?',
                    metavar='HOST:PORT',
                    help='Run a TCP server listening on HOST:PORT (default: {}:{})'.format(settings.SOCKET_HOST, settings.SOCKET_PORT))
    ap.add_argument('--client-stoppable', action='store_true', help='Clients may stop the server via an API call')
    args = vars(ap.parse_args())

    if 'tcp' in args and 'unix' in args:
        print('Can not specify both UNIX and TCP at once!', file=sys.stdout)
        sys.exit(1)

    if 'tcp' in args:
        try:
            host, port = args.get('tcp', '').split(':')
            port = int(port)
        except AttributeError:
            host, port = (settings.SOCKET_HOST, settings.SOCKET_PORT)
        server = socketserver.TCPServer((host, port), handlers.DARequestHandler)
        logger.info('TCP server started on {}:{}'.format(host, port))

    else: # UNIX server is default
        filename = args.get('unix') or settings.SOCKET_FILENAME
        helpers.prepare_socket(filename)
        server = socketserver.UnixStreamServer(filename, handlers.DARequestHandler)
        logger.info('UNIX server started at ' + filename)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Killed by user')

