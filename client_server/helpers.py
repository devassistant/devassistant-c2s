
import json
import os
import traceback
import uuid

from client_server import api, dialog_helper, exceptions, settings
from client_server.logger import logger, JSONHandler

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
        '''JSON-format and send a message'''
        msg = api.APIFormatter.format_json(dictionary)
        self.handler.send(msg)

    def send(self, msg):
        '''Send already JSON-formatted message'''
        logger.debug('Sent a message ({} bytes)'.format(len(msg)))
        self.handler.send(msg)

    def send_error(self, reason, run_id=''):
        '''Send an API-compliant error message with the specified reason'''
        self.handler.send(api.APIFormatter.format_error(reason, run_id))

    def get_answer(self):
        '''Recieve an answer from the client'''
        return json.loads(self.handler.get_answer())

    def set_dialoghelper_contex(self, run_id):
        '''Set static context in JSONDialogHelper'''
        # TODO: solve this in some less smelly way
        dialog_helper.JSONDialogHelper.comm = self
        dialog_helper.JSONDialogHelper.run_id = run_id

    def clean_dialoghelper(self):
        '''Remove static context from JSONDialogHelper'''
        # TODO: solve this in some less smelly way
        dialog_helper.JSONDialogHelper.comm = None
        dialog_helper.JSONDialogHelper.run_id = None

    def process_run(self, args):
        '''Run an assistant/action'''
        logger.info('Serving a run request')
        path = args['path']
        run_id = str(uuid.uuid4()).replace('-', '')

        da_args = args.copy()
        del(da_args['path'])
        da_args['__ui__'] = 'json'

        # TODO process arguments for the runnable!

        to_run = api.DevAssistantAdaptor.get_runnable_to_run(path, da_args)
        dalogger = api.DevAssistantAdaptor.get_logger()

        try:
            self.set_dialoghelper_contex(run_id)  # TODO: solve this in some less smelly way
            self.send(api.APIFormatter.format_run_ack(run_id))
            dalogger.handlers = []
            dalogger.addHandler(JSONHandler(self, run_id))
            dalogger.setLevel(args.get('loglevel', "INFO").upper())
            logger.info('Running with args: {}'.format(da_args))
            to_run.run()
            self.send(api.APIFormatter.format_run_finished(run_id, 'ok'))
        except BaseException as e:
            logger.info(traceback.format_exc())
            raise exceptions.ProcessingError(str(e), run_id=run_id)
        finally:
            dalogger.handlers = []
            self.clean_dialoghelper()

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
            try:
                run_id = e.run_id
                self.send_error('Error processing request: ' + str(e), run_id)
                self.send(api.APIFormatter.format_run_finished(run_id, 'error'))
            except AttributeError:
                self.send_error('Error processing request: ' + str(e))


