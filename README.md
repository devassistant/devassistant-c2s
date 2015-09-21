# DevAssistant Client/Server Prototype

This repository contains code that will likely become the client/server (c2s)
implementation of DevAssistant. This is *not* a DevAssistant replacement yet,
is buggy, and is not meant to be used in production in any way.

## How to Test

To run the UNIX domain sockets-based server, run

    ./server.py

The server automatically listens at `~/.devassistant-socket`. To connect to the
server, either use the `client.py` script, or the Linux socket utility `socat`:

    socat - UNIX-CONNECT:~/.devassistant-socket


