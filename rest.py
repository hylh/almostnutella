#!/usr/bin/env python
""" HTTP server and Threded HTTP server """

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

class NodeHttpHandler(BaseHTTPRequestHandler):
    """ Gnutella like HTTP request handler """
    def do_GET(self):
        """ get request for /neighbours """
        if self.path == "/neighbours":
            self.send_response(200)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in a separate thread """
    