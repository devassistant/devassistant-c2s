#!/usr/bin/python3
import sys

from client_server.client import ConsoleClient

if __name__ == '__main__':

    cc = ConsoleClient()
    try:
        cc.start()
        sys.exit(cc.run({}))
    except KeyboardInterrupt:
        sys.exit(130)
