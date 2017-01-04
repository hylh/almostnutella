#!/usr/bin/env python
""" Gnutella like node system """

import argparse
import socket
import threading
import signal
import sys
from node import Node
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

class NodeHttpHandler(BaseHTTPRequestHandler):
    """ Gnutella like HTTP request handler """
    def do_GET(self):
        """ GET request for /neighbours """
        if self.path == "/neighbours":
            n_list = THIS_NODE.get_neighbour_list()
            self.send_response(200)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in a separate thread """

def parse_args():
    """ Parse command line arguments """
    default_port = 8000
    default_timeout = 60
    parser = argparse.ArgumentParser(prog="nutella", description="P2P network")

    parser.add_argument("-p", "--port", type=int, default=default_port,
    help="port number to listen on, default: {}".format(default_port))

    parser.add_argument("--timeout", type=float, default=default_timeout)

    return parser.parse_args()

def start_http():
    """ Try to start a HTTP server.
        On error: exit """
    try:
        server = ThreadedHTTPServer(('', THIS_NODE.port), NodeHttpHandler)
    except:
        sys.exit(1)

    return server


if __name__ == "__main__":
    ARGS = parse_args()
    HOSTNAME = socket.gethostname()
    THIS_NODE = Node(HOSTNAME, ARGS.port)
    print "Hostname: {} Port: {}".format(THIS_NODE.hostname, THIS_NODE.port)
    HTTP_SERVER = start_http()

    def run_server():
        """ Run the server forever """
        print "Running server"
        HTTP_SERVER.serve_forever()

    def shutdown_server_on_signal(signum, frame):
        """ Gracefull shutdown of server on ctrl+c """
        print "Server shutting down"
        HTTP_SERVER.shutdown()

    HTTP_THREAD = threading.Thread(target=run_server)
    HTTP_THREAD.daemon = True
    HTTP_THREAD.start()

    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)

    HTTP_THREAD.join(ARGS.timeout)

    if HTTP_THREAD.isAlive():
        print "Reached timeout. Asking node to shut down"
        HTTP_SERVER.shutdown()


