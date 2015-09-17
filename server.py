#!/usr/bin/python3

import socketserver

from client_server import handlers, helpers, settings
from client_server.logger import logger


if __name__ == '__main__':

    helpers.prepare_socket(settings.SOCKET_FILENAME)
    server = socketserver.UnixStreamServer(settings.SOCKET_FILENAME, handlers.DARequestHandler)
    try:
        logger.info('Server started')
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Killed by user')

