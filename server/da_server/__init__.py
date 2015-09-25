import sys
import argparse
import logging

from da_server import handlers, helpers, servers, settings
from da_server.logger import logger

def run():
    ap = argparse.ArgumentParser(usage='DevAssistant server. If no arguments are provided, the UNIX server is started',
                                 argument_default=argparse.SUPPRESS)
    ap.add_argument('-u', '--unix',
                    nargs='?',
                    metavar='FILENAME',
                    help='Run a UNIX socket server listening on a filename (default: {})'.format(settings.SOCKET_FILENAME))
    ap.add_argument('-t', '--tcp',
                    nargs='?',
                    metavar='HOST:PORT',
                    help='Run a TCP server listening on HOST:PORT (default: {}:{})'.format(settings.SOCKET_HOST, settings.SOCKET_PORT))
    ap.add_argument('-s', '--client-stoppable', action='store_true', help='Clients may stop the server via an API call')
    ap.add_argument('-d', '--debug', action='store_true', help='Display debug log messages on stdout')
    ap.add_argument('-v', '--verbose', action='store_true', help='Display informative log messages on stdout')
    args = vars(ap.parse_args())

    if args.get('verbose'):
        logger.setLevel(logging.INFO)
    elif args.get('debug'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    if 'tcp' in args and 'unix' in args:
        logger.error('Can not specify both UNIX and TCP at once!')
        sys.exit(1)

    if 'tcp' in args:
        try:
            host, port = args.get('tcp', '').split(':')
            port = int(port)
        except AttributeError:
            host, port = (settings.SOCKET_HOST, settings.SOCKET_PORT)
        server = servers.TCPServer((host, port), handlers.DARequestHandler)
        logger.info('TCP server started on {}:{}'.format(host, port))

    else: # UNIX server is default
        filename = args.get('unix') or settings.SOCKET_FILENAME
        helpers.prepare_socket(filename)
        server = servers.UNIXServer(filename, handlers.DARequestHandler)
        logger.info('UNIX server started at ' + filename)

    server.set_context({'client_stoppable': args.get('client_stoppable')})
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Killed by user')
        sys.exit(130)
    except SystemExit:
        logger.info('Killed by API call')
        sys.exit(0)


