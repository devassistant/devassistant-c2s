#!/usr/bin/python3

from client_server.client import ConsoleClient

if __name__ == '__main__':

    cc = ConsoleClient()
    cc.start()
    cc.run({})
