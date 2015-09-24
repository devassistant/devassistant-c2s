# DevAssistant Client/Server Prototype

This repository contains code that will likely become the client/server (c2s)
implementation of DevAssistant. This is *not* a DevAssistant replacement yet,
is buggy, and is not meant to be used in production in any way.

## How to Test

The server can run both as a UNIX socket server (`--unix`, by default
`~/.devassistant-socket`) and a TCP server (`--tcp`, by default
`localhost:7776`). You may specify a filename or `HOST:PORT` if you wish to
override defaults. Example:

    $ ./server.py --debug --unix ~/.foo

To connect to the server, run the `client.py` script in the `client` directory,
or use the Linux socket utility `socat`:

    $ ./client.py --help

    $ socat - UNIX-CONNECT:~/.devassistant-socket
    {"query": {"request": "get_tree", "options": {}}}


