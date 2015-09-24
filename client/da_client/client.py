#!/usr/bin/python3

import argparse
import json
import logging
import socket
import sys
import os

from da_client import exceptions, settings
from da_client.logger import logger

class RequestFormatter(object):

    @classmethod
    def format_message(cls, message):
        return message + '\n'

    @classmethod
    def format_tree_request(cls, depth=0):
        json_message = json.dumps({'query': {'request': 'get_tree', 'options': {'depth': depth, 'arguments': True}}})
        return cls.format_message(json_message)

    @classmethod
    def format_run_request(cls, args):
        new_args = args.copy()
        path = ''
        for key in sorted([a for a in new_args.keys() if a.startswith('subassistant_')]):
            if new_args[key]:
                path += '/' + new_args[key]
            del new_args[key]

        for key in [a for a in new_args.keys() if a.startswith('__') and a.endswith('__')]:
            del new_args[key]

        message = {'query': {'request': 'run', 'options': {'path': path,
                                                           'pwd': os.getcwd(),
                                                           'arguments': new_args}}}
        if args.get('__debug__'):
            message['query']['options']['loglevel'] = 'debug'
        json_message = json.dumps(message)
        logger.debug('Query to server: {}'.format(json_message))
        return cls.format_message(json_message)

    @classmethod
    def format_answer(cls, run_id, value):
        json_message = json.dumps({'answer': {'id': run_id, 'value': str(value)}})
        return cls.format_message(json_message)

class ConsoleClient(object):

    BUFFER_SIZE = 8182

    def __init__(self, filename=settings.SOCKET_FILENAME):
        self.filename = filename
        self.socket = None

    def send(self, message):
        self.socket.send(message.encode('utf-8'))

    def receive(self):
        result = b''
        while True:
            data = self.socket.recv(self.BUFFER_SIZE)
            if not data:
                break

            result += data
            if len(data) < self.BUFFER_SIZE:
                break
        return result.decode('utf-8')

    def start(self):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.filename)
            self.socket = sock
        except ConnectionError as e:
            logger.error('Could not connect to the server, maybe it\'s not running?')
            logger.error('The message was: {}'.format(e))
            sys.exit(1)

    def run(self, args):
        ret = 0
        if self.socket is None:
            raise exceptions.ClientException('Not connected')

        self.send(RequestFormatter.format_tree_request())
        reply = json.loads(self.receive())

        if 'error' in reply:
            print('Error: ' + reply['error']['reason'])
            ret = 1
        elif 'tree' in reply:
            ap = get_argument_parser(reply['tree'])
            user_args = vars(ap.parse_args(sys.argv[1:]))
            if user_args.get('__comm_debug__'):
                logger.setLevel(logging.DEBUG)
            self.send(RequestFormatter.format_run_request(user_args))
            run_id = None
            while True:
                data = self.receive()
                if not data:
                    break
                json_data = json.loads(data)
                if 'run' in json_data:
                    run_id = json_data['run']['id']
                    print('Executing assistant...')
                elif 'log' in json_data:
                    self.handle_log(json_data['log']['level'], json_data['log']['message'])
                elif 'error' in json_data:
                    self.handle_error(json_data['error']['reason'])
                elif 'finished' in json_data:
                    self.handle_finish(json_data['finished']['status'])
                    ret = self.retcode_finish(json_data['finished']['status'])
                    break
                elif 'question' in json_data:
                    self.handle_question(run_id, json_data)
                else:
                    raise exceptions.ClientException('Invalid message: ' + str(json_data))
        else:
            print('Wrong reply: ' + reply)
            ret = 1
        return ret

    def handle_question(self, run_id, args):
        print(args)
        question = args['question']
        try:
            print(question['text'])
        except KeyError:
            pass
        reply = input(question['prompt'] + ' ')
        self.send(RequestFormatter.format_answer(run_id, reply))

    def handle_log(self, level, message):
        print('{}: {}'.format(level, message))

    def handle_error(self, reason):
        print('Error Processing: ' + reason)

    def handle_finish(self, status):
        if status == 'ok':
            print('Run Finished OK')
        else:
            print('Run Finished with Errors')

    def retcode_finish(self, status):
        if status == 'ok':
            return 0
        return 1

def get_argument_parser(tree):
    '''Generate an ArgumentParser based on the tree of assistants/actions received'''
    parser = argparse.ArgumentParser(description='',argument_default=argparse.SUPPRESS)
    add_toplevel_arguments(parser)
    subparsers = parser.add_subparsers(dest='subassistant_0')
    for runnable in tree:
        add_parser_recursive(subparsers, runnable, 1)
    return parser

def add_toplevel_arguments(parser):
    parser.add_argument('--debug',
                        help='Show debug output of devassistant (may be a verbose a lot!).',
                        action='store_true',
                        dest='__debug__',
                        default=False)
    parser.add_argument('--comm-debug',
                        help='Show debug output of communication with server.',
                        action='store_true',
                        dest='__comm_debug__',
                        default=False)

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


