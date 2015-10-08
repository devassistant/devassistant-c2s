# DevAssistant Client/Server Prototype

This repository contains code that will likely become the client/server (c2s)
implementation of DevAssistant (DA). This is *not* a DA replacement yet, is
buggy, and is not meant to be used in production in any way.

This repository contains both the client and the server code in the respective
directories. Each of the directories contains a `docker` directory with a
Dockerfile that is used for building the respective CentOS-based Docker image.
Running DA in Docker is perfectly optional.

# How to Build

If you wish to build the Docker images, you can use the provided `build.sh`
script. This script packages the respective parts in tarballs, and uses these
tarballs in building the images.

If you want to run DA locally, go to the `client` and `server` directories and
run:

```
./setup.py sdist
```

This creates a tarball in the newly created `dist` directory. Install that on
your system by running:

```
pip3 install --user dist/da*.tar.gz
```

# How to Run

## Local

The server can run both as a UNIX socket server (`--unix`, by default creates a
socket at `~/.devassistant-socket`) and a TCP server (`--tcp`, defaults to
`localhost:7776`). You may specify a filename or `HOST:PORT` if you wish to
override defaults. Example:

    $ ./server.py --debug --unix ~/.foo

    $ ./server.py --debug --client-stoppable --tcp 0.0.0.0:7776

To connect to the server, run the `client.py` script in the `client` directory,
or use the Linux socket utility `socat`:

    $ ./client.py --help

    $ socat - UNIX-CONNECT:~/.devassistant-socket
    {"query": {"request": "get_tree", "options": {}}}


## Docker

The commands to invoke the containers are a bit long, therefore we
recommend you create bash aliases for them.

```
sudo docker run --privileged -v $HOME:/home/dev -v $PWD:/cwd da-server
```

The container needs to run in the privileged mode becase otherwise SELinux
would block it from accessing your local files.

At the moment, it is impossible for the server to change the current directory
(mounted via `-v $PWD:/cwd`), so in case you need to perform changes on files
that reside elsewhere, you need to stop the server and re-launch it. Stopping
the server is done by invoking the `server-stop` command on the client.

To invoke the client, run the following command:

```
sudo docker run -i da-client --tcp IP_OF_SERVER:7776 --help
```
