#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

class NodeHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/neighbours":
            self.send_response(200)
            self.end_headers()
            
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in a separate thread """
    