#!/usr/bin/env python

import argparse
import socket
import threading
import signal
import sys
from rest import ThreadedHTTPServer, NodeHttpHandler

def parse_args():
    default_port = 8000
    default_timeout = 10
    parser = argparse.ArgumentParser(prog="nutella", description="P2P network")
    
    parser.add_argument("-p", "--port", type=int, default=default_port,
        help="port number to listen on, default %d" %default_port)
    
    parser.add_argument("--timeout", type=float, default=default_timeout)
    
    return parser.parse_args()
    
def start_http():
    try:
        server = ThreadedHTTPServer(('', ARGS.port), NodeHttpHandler)
    except:
        sys.exit(1)
        
    return server


if __name__ == "__main__":
    ARGS = parse_args()
    HOSTNAME = socket.gethostname()
    print "Hostname:", HOSTNAME
    http_server = start_http()
    
    def run_server():
        print "Running server"
        http_server.serve_forever()
    
    def shutdown_server_on_signal(signum, frame):
        print "Server shutting down"
        http_server.shutdown()
        
    http_thread = threading.Thread(target=run_server)
    http_thread.daemon = True
    http_thread.start()
    
    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)
        
    http_thread.join(ARGS.timeout)
    
    if http_thread.isAlive():
        print "Reached timeout. Asking node to shut down"
        http_server.shutdown()
    
  
    