
import json
import os

from client_server import exceptions, settings
from client_server.logger import logger

def prepare_socket(path):
    try:
        os.unlink(path)
    except OSError as e:
        if os.path.exists(path):
            raise


class QueryProcessor(object):
    '''Process a query. The constructor takes a DARequestHandler instance so
    that it can send and request data from the user'''

    def __init__(self, handler):
        '''An instance of a DARequestHandler is required'''
        self.handler = handler

    def send_json(self, dictionary):
        '''Send a JSON-formatted message'''
        dictionary['version'] = settings.API_VERSION
        self.handler.send(json.dumps(dictionary))

    def send_error(self, reason):
        '''Send an API-compliant error message with the specified reason'''
        self.send_json({'error': {'reason': reason}})

    def process_run(self, args):
        '''Run an assistant'''
        logger.info('Serving a run request')
        run_id = uuid.uuid4().replace('-', '')
        self.send_json({'run': {'id': run_id}})
        self.send_json({'finished': {'id': run_id, 'status': 'ok'}})

    def process_tree(self, args):
        '''Get a tree of runnables'''
        logger.info('Serving a tree request')
        self.send_json({'foo': {'bar': 'baz'}})

    def process_detail(self, args):
        '''Get a detail of a runnable'''
        logger.info('Serving a tree request')
        self.send_json({'foo': {'baz': 'qux'}})

    def process_query(self, data):
        try:
            query = json.loads(data)['query']
            if query['request'] == 'get_tree':
                self.process_tree(query['options'])
            elif query['request'] == 'get_detail':
                self.process_detail(query['options'])
            elif query['request'] == 'run':
                self.process_run(query['options'])
            else:
                raise KeyError('Not a valid request')
            logger.info('Done')
        except ValueError as e:
            logger.info('Request not valid JSON: "{data}" ({e}) '.format(data=data, e=e))
            self.send_error('Request not valid JSON')
        except KeyError as e:
            logger.info('Request not valid DA API call: "{data}" ({e}) '.format(data=data, e=e))
            self.send_error('Request not valid API call')


