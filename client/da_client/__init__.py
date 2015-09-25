
import logging
import sys

from da_client import arguments, clients, settings
from da_client.logger import logger

def run():
    cmd_tree = [] # We do not know the tree of server commands yet

    # Processing of the help flags is turned off here because if the
    # connection to the server succeeds, the user will see the help message
    # from the argument parser instantiated in the clients.*Client's run()
    # method (that parser has all the arguments this one does, plus the ones
    # from the server assistant tree).
    #
    # If the connection to the server fails, the help message of this
    # argument parser will be shown when ConnectionError is caught at the end
    # of this routine.
    ap = arguments.get_argument_parser(cmd_tree, add_help=False)
    args = ap.parse_known_args()
    comm_dict = vars(args[0])
    da_args = args[1]

    # LOGGING
    if comm_dict.get('__comm_debug__'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # GET SERVER ADDRESS
    if '__tcp__' in comm_dict:
        try:
            host, port = (comm_dict['__tcp__'] or '{}:{}'.format(settings.SOCKET_HOST, settings.SOCKET_PORT)).split(':')
        except ValueError:
            ap.error('Invalid TCP address: "{}", must be HOST:PORT'.format(comm_dict['__tcp__']))
            sys.exit(2)
        client = clients.TCPClient(host=host, port=int(port))
    else:
        filename = comm_dict.get('__unix__') or settings.SOCKET_FILENAME
        client = clients.UNIXClient(filename)

    # RUN
    try:
        client.start()
        sys.exit(client.run(da_args))
    except KeyboardInterrupt:
        sys.exit(130)
    except PermissionError:
        ap.error('Permission denied: {}'.format(comm_dict.get('__unix__')))
        sys.exit(2)
    except FileNotFoundError:
        ap.error('File not found: ' + comm_dict.get('__unix__'))
        sys.exit(2)
    except ConnectionError as e:
        logger.error(client.format_connection_error())
        logger.error('The message was: {}'.format(e))
        # Show help if everything fails
        ap.print_help()
        sys.exit(1)
