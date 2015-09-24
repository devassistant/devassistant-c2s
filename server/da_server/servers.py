
import sys
import socketserver
import threading
import traceback

from da_server.logger import logger


class DAServer(socketserver.BaseServer):

    def set_context(self, context):
        self.context = context

    def die(self):
        threading.Thread(target=lambda s:s.shutdown(), args=(self,)).start()

    def handle_error(self, request, client_address):
        exc_type, exc_value, exc_tb =  sys.exc_info()
        if exc_type is KeyboardInterrupt:
            self.die()
            raise
        elif exc_type is SystemExit:
            self.die()
            raise
        else:
            logger.error(40*'-')
            logger.error('Exception happened')
            logger.error(traceback.format_exc())
            logger.error(40*'-')


class TCPServer(DAServer, socketserver.TCPServer):
    pass


class UNIXServer(DAServer, socketserver.UnixStreamServer):
    pass

