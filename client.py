#!/usr/bin/python3
import sys

from client_server.client import ConsoleClient

if __name__ == '__main__':

    cc = ConsoleClient()
    cc.start()
    sys.exit(cc.run({}))
