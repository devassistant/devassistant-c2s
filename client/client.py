#!/usr/bin/python3
import sys

from da_client.client import ConsoleClient

if __name__ == '__main__':

    cc = ConsoleClient()
    try:
        cc.start()
        sys.exit(cc.run({}))
    except KeyboardInterrupt:
        sys.exit(130)
