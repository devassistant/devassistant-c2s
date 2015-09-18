
import json
import os

from client_server import api, exceptions, settings
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
        msg = api.APIFormatter.format_json(dictionary)
        print(len(msg))
        self.handler.send(msg)

    def send_error(self, reason):
        '''Send an API-compliant error message with the specified reason'''
        self.handler.send(api.APIFormatter.format_error(reason))

    def process_run(self, args):
        '''Run an assistant'''
        logger.info('Serving a run request')
        run_id = uuid.uuid4().replace('-', '')
        self.send_json({'run': {'id': run_id}})
        self.send_json({'finished': {'id': run_id, 'status': 'ok'}})

    def process_tree(self, args):
        '''Get a tree of runnables'''
        logger.info('Serving a tree request')
        runnables = api.DevAssistantAdaptor.get_top_runnables()
        tree = [api.APISerializer.serialize_runnable(runnable,
                                                     '/',
                                                     get_icons = args.get('icons', False),
                                                     get_arguments = args.get('arguments', False),
                                                     ) for runnable in runnables]
        self.send_json({'tree': tree})

    def process_detail(self, args):
        '''Get a detail of a runnable'''
        logger.info('Serving a detail request')
        path = args['path']
        runnable = api.DevAssistantAdaptor.get_runnable_by_path(args['path'])
        detail = api.APISerializer.serialize_runnable(runnable,
                                                      path[:path.rfind('/')],
                                                      get_icons=args.get('icons', False),
                                                      get_arguments=args.get('arguments', False),
                                                      names_only=True)
        self.send_json({"detail": detail})

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
        except exceptions.ProcessingError as e:
            logger.info('Error processing request: "{data}" ({e}) '.format(data=data, e=e))
            self.send_error('Error processing request: ' + str(e))


