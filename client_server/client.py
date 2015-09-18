#!/usr/bin/python3

import argparse
import json
import socket
import sys

from client_server import exceptions, settings

class RequestFormatter(object):

    @classmethod
    def format_message(cls, message):
        return message + '\n'

    @classmethod
    def format_tree_request(cls, depth=0):
        json_message = json.dumps({'query': {'request': 'get_tree', 'options': {'depth': depth, 'arguments': True}}})
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
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.filename)
        self.socket = sock

    def run(self, args):
        if self.socket is None:
            raise exceptions.ClientException('Not connected')

        self.send(RequestFormatter.format_tree_request())
        reply = json.loads(self.receive())

        if 'error' in reply:
            print('Error: ' + reply['error']['reason'])
        elif 'tree' in reply:
            ap = get_argument_parser(reply['tree'])
            user_args = ap.parse_args(sys.argv[1:])
            print(user_args)
        else:
            print('Wrong reply: ' + reply)

def get_argument_parser(tree):
    parser = argparse.ArgumentParser(description='')
    subparsers = parser.add_subparsers()
    for runnable in tree:
        add_parser_recursive(subparsers, runnable)
    return parser

def add_parser_recursive(parsers, runnable):
    parser = parsers.add_parser(name=runnable['name'], description=runnable['description'])
    subparsers = parser.add_subparsers()
    for arg in runnable.get('arguments', []):
        kwargs = {k:v for k,v in arg['kwargs'].items() if k in ['help', 'nargs', 'action', 'dest', 'const']}
        if isinstance(kwargs.get('action'), list): # DA allows a list [default_iff_used, value]
            del(kwargs['action'])
        parser.add_argument(*arg['flags'], **kwargs)
    for child in runnable['children']:
        add_parser_recursive(subparsers, child)


