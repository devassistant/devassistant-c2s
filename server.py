
from time import sleep

import errno
import sys
import os
import socket
import threading
import socketserver

class RequestHandler(socketserver.BaseRequestHandler):

    def run(self):
        self.send('run_id=1')
        self.send('log1')
        self.send('log2')
        sleep(3)
        self.send('log3')
        sleep(2)
        self.send('ask')
        print(self.get_answer())
        sleep(2)
        self.send('log5')
        self.send('ask')
        print(self.get_answer())
        self.send('done')

    def get_answer(self):
        print('Waiting for client input')
        return self.receive()

    def receive(self):
        return self.request.recv(1024).decode('utf-8').strip()

    def send(self, message):
        msg = (message + '\n').encode('utf-8')
        self.request.send(msg)

    def handle(self):
        print('Incoming connection')
        try:
            while True:
                data = self.receive()
                if data == 'tree':
                    print('Serving a tree request')
                    self.send('foo bar baz')
                elif data == 'run':
                    print('Serving a run request')
                    self.run()
                elif not data:
                    print('Client disconnected (EOF)')
                    break
                else:
                    print('Invalid request: ' + data)
                    self.send('request invalid')
        except IOError as e:
            if e.errno == errno.EPIPE:
                print('Client disconnected (broken pipe)')
            else:
                raise


if __name__ == '__main__':

    os.unlink('/home/tradej/.devassistant-socket')
    server = socketserver.UnixStreamServer('/home/tradej/.devassistant-socket', RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Killed by user')

