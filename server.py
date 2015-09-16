
import logging
import json
import errno
import os
import socketserver
import uuid

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

class RequestHandler(socketserver.BaseRequestHandler):

    def run(self, args):
        '''Run an assistant'''
        logger.info('Serving a run request')
        run_id = uuid.uuid4().replace('-', '')
        self.send({'run': {'id': run_id}})
        self.send({'finished': {'id': run_id, 'status': 'ok'}})

    def serve_tree(self, args):
        '''Get a tree of runnables'''
        logger.info('Serving a tree request')
        self.send('foo bar baz')

    def serve_detail(self, args):
        '''Get a detail of a runnable'''
        logger.info('Serving a tree request')
        self.send('foo bar baz qux')

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
        msg = (json.dumps(message) + '\n').encode('utf-8')
        self.request.send(msg)

    def send_error(self, message):
        '''Send an error with the specified message'''
        self.send({'error': {'reason': message}})

    def handle(self):
        logger.info('Incoming connection')
        try:
            while True:
                try:
                    data = self.receive()
                    if not data:
                        logger.info('Client disconnected (EOF)')
                        break

                    query = json.loads(data)['query']
                    if query['request'] == 'get_tree':
                        self.serve_tree(query['options'])
                    elif query['request'] == 'get_detail':
                        self.serve_detail(query['options'])
                    elif query['request'] == 'run':
                        self.run(query['options'])
                    else:
                        raise ValueError()
                    logger.info('Done')

                # Malformed request
                except (KeyError, ValueError) as e:
                    logger.info('Invalid request: ' + str(e))
                    self.send_error('Request invalid')
                    continue

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


if __name__ == '__main__':

    os.unlink('/home/tradej/.devassistant-socket')
    server = socketserver.UnixStreamServer('/home/tradej/.devassistant-socket', RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Killed by user')

