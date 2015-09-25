#!/usr/bin/python3

import argparse
import getpass
import json
import logging
import socket
import sys
import os

from da_client import arguments, exceptions, settings
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
    def format_stop_request(cls):
        json_message = json.dumps({'query': {'request': 'shutdown'}})
        logger.debug('Query to server: {}'.format(json_message))
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
            message['query']['options']['loglevel'] = 'DEBUG'
        json_message = json.dumps(message)
        logger.debug('Query to server: {}'.format(json_message))
        return cls.format_message(json_message)

    @classmethod
    def format_answer(cls, run_id, value):
        json_message = json.dumps({'answer': {'id': run_id, 'value': str(value)}})
        return cls.format_message(json_message)

class ConsoleClient(object):

    BUFFER_SIZE = 8182

    def __init__(self):
        self.socket = None

    def connect_socket(self):
        raise NotImplementedError

    def format_connection_error(self):
        raise NotImplementedError

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
        self.socket = self.connect_socket()

    def run(self, server_args):
        ret = 0
        if self.socket is None:
            raise exceptions.ClientException('Not connected')

        # check if the first non -- argument is server-stop
        if [a for a in server_args if not a.startswith('--')][0] == 'server-stop':
            self.send(RequestFormatter.format_stop_request())
            try:
                reply = json.loads(self.receive())  # this will fail when the server stopped
                if 'error' in reply:
                    print('Error: ' + reply['error']['reason'])
                    return 1
            except:
                pass
            return 0

        self.send(RequestFormatter.format_tree_request())
        reply = json.loads(self.receive())

        if 'error' in reply:
            print('Error: ' + reply['error']['reason'])
            ret = 1
        elif 'tree' in reply:
            ap = arguments.get_argument_parser(reply['tree'], debug=True)
            user_args = vars(ap.parse_args(server_args))
            self.send(RequestFormatter.format_run_request(user_args))
            run_id = None
            while True:
                data = self.receive()
                if not data:
                    break

                finished = False
                for line in data.splitlines():
                    json_data = json.loads(line)
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
                        finished = True
                        break
                    elif 'question' in json_data:
                        self.handle_question(run_id, json_data)
                    else:
                        raise exceptions.ClientException('Invalid message: ' + str(json_data))
                if finished:
                    break
        else:
            print('Wrong reply: ' + reply)
            ret = 1
        return ret

    def handle_question(self, run_id, args):
        question = args['question']
        try:
            print(question['message'])
        except KeyError:
            pass  # some questions don't have message, just prompt
        if question['type'] == 'password':
            reply = getpass.getpass(question['prompt'] + ' ')
        else:
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


class UNIXClient(ConsoleClient):

    def __init__(self, filename=settings.SOCKET_FILENAME):
        super(UNIXClient, self).__init__()
        self.filename = filename

    def connect_socket(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.filename)
        return sock

    def format_connection_error(self):
        return 'Could not connect to server at "{}", maybe it\'s not running?'.format(self.filename)

class TCPClient(ConsoleClient):

    def __init__(self, host=settings.SOCKET_HOST, port=settings.SOCKET_PORT):
        super(TCPClient, self).__init__()
        self.host = host
        self.port = port

    def connect_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def format_connection_error(self):
        return  'Could not connect to server at {}:{}, maybe it\'s not running?'.format(self.host, self.port)

