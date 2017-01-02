#!/usr/bin/env python
""" HTTP server and Threded HTTP server """

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from nutella import 

class NodeHttpHandler(BaseHTTPRequestHandler):
    """ Gnutella like HTTP request handler """
    def do_GET(self):
        """ GET request for /neighbours """
        if self.path == "/neighbours":
            n_list = get_neighbour()
            self.send_response(200)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in a separate thread """
    