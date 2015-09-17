
import errno
import json
import socketserver

from client_server import helpers, exceptions
from client_server.logger import logger

class DARequestHandler(socketserver.BaseRequestHandler):
    '''This class takes care of communicating with the client. It only handles
    sending and receiving of data, all formatting and API compliance is
    the responsibility of helpers.QueryProcessor.'''

    def get_answer(self):
        '''Wait for client to provide input'''
        logger.info('Asking client...')
        msg = self.receive()
        logger.info('Answer received: ' + msg)
        return msg

    def receive(self):
        '''Receive message from client'''
        return self.request.recv(1024).decode('utf-8').strip()

    def send(self, message):
        '''Send a message to the client. Message is a JSON entity'''
        self.request.send((message + '\n').encode('utf-8'))

    def handle(self):
        logger.info('Incoming connection')
        try:
            while True: # Wait for client
                data = self.receive()
                if not data:
                    logger.info('Client disconnected (EOF)')
                    break
                processor = helpers.QueryProcessor(handler=self)
                processor.process_query(data)

        # Trouble communicating with the client
        except IOError as e:
            if e.errno == errno.EPIPE:
                logger.info('Client disconnected (broken pipe)')
            else:
                raise

        # Other exceptions
        except Exception as e:
            try:
                self.send_error('Unexpected server error')
            except:
                pass
            raise

