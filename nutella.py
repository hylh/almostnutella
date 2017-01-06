#!/usr/bin/env python
""" Gnutella like node system """

import argparse
import socket
import threading
import signal
import sys
import os
import xmlrpclib
import subprocess
from node import Node
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

HOSTLIST = []
STATUS_DICT = {}

class NodeHttpHandler(BaseHTTPRequestHandler):
    """ Gnutella like HTTP request handler """
    def do_GET(self):
        """ GET request for /neighbours """
        if self.path == "/neighbours":
            n_list = THIS_NODE.get_neighbour_list()
            if n_list == None:
                return self.not_found()
            return self.send_text(n_list)

    def do_POST(self):
        """ Reponse to a POST message to the server """
        if self.path == "/addNode":
            #Add a new node to the system
            new_node = start_new_node()
            if new_node == None:
                return self.not_found()
            return self.send_text(new_node)

        if self.path == "/shutdown":
            #Shutdown this node
            self.send_response(200)
            self.end_headers()
            kill()

    def send_text(self, text):
        """ Send 200 OK response with text to HTTP request """
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-length', len(text))
        self.end_headers()
        self.wfile.write(text)

    def not_found(self):
        """ Send 404 Not Found response to HTTP request """
        self.send_response(404)
        self.end_headers()
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in a separate thread """

class ThreadedRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """ Handle requests in a separate thread """

def kill():
    """ Shutdown this node """
    neighbours = THIS_NODE.get_neighbour_list()
    if neighbours == None:
        return shutdown()
    remove_host = THIS_NODE.full_name
    if isinstance(neighbours, basestring):
        #Check if it's a string, if so, only one object in list
        node = neighbours
        remove(node, remove_host)
    else:
        for node in neighbours:
            remove(node, remove_host)
    return shutdown()

def shutdown():
    """ Shutdown RPC and HTTP server """
    RPC.shutdown()
    HTTP_SERVER.shutdown()

def remove(node, hostname):
    """ Send RPC message to a node to remove a hostname """
    host, port = THIS_NODE.split_hostname(node, ":")
    remote_name = THIS_NODE.create_remote_hostname(host, port)
    remote = xmlrpclib.ServerProxy(remote_name)
    remote.remove_remote(hostname)

def remove_remote(hostname):
    """ Remove a hostname and inform the others """
    THIS_NODE.remove_neighbour(hostname)
    remaining = THIS_NODE.get_neighbour_list()
    if remaining == None:
        return
    for node in remaining:
        remove(node, hostname)
    #fill_neighbour_list()

def start_new_node():
    """ Start a new node """
    if len(HOSTLIST) == 0:
        create_host_list()

    name = HOSTLIST.pop()
    name, port = THIS_NODE.split_hostname(name, ":")
    program = "python nutella.py --port={} --caller={}".format(port, \
        (THIS_NODE.full_name))
    print "GIT"
    new_node = launch(name, program)
    if new_node == None:
        print "Used all entries in the HOSTLIST!"
        return None
    print "GOT"
    THIS_NODE.add_neighbour(new_node, port)
    return new_node

def fill_neighbour_list():
    """ Fill up neighbour list if it's not full """
    node = iter(THIS_NODE.neighbour)
    visited = [THIS_NODE.full_name]
    print "hello"
    while len(THIS_NODE.neighbour) < THIS_NODE.number_of_neighbours:
        print "visited:", visited
        if len(THIS_NODE.neighbour) == 0:
            print "Caller:", THIS_NODE.caller
            if THIS_NODE.caller in visited:
                print "reutnring"
                return
            neighbour = get_remote_neighbour(THIS_NODE.caller, visited)
        else:
            print "Current node:", THIS_NODE.full_name
            remote = node.next()
            if remote == None:
                return
            neighbour = get_remote_neighbour(remote, visited)

        if neighbour == None:
            continue
        if isinstance(neighbour, basestring):
            #Only one neighbour returned
            host, port = THIS_NODE.split_hostname(neighbour, ":")
            THIS_NODE.add_neighbour(host, port)
            continue
        else:
            for node in neighbour:
                host, port = THIS_NODE.split_hostname(node, ":")
                THIS_NODE.add_neighbour(host, port)

def get_remote_neighbour(hostname, visited):
    """ Connect to remote node to get neighbour list """
    print "remote hostname is:", hostname
    if hostname in visited:
        return
    else:
        visited.append(hostname)

    host, port = THIS_NODE.split_hostname(hostname, ":")
    remote_name = THIS_NODE.create_remote_hostname(host, port)
    remote = xmlrpclib.ServerProxy(remote_name)
    result = remote.get_neighbours()
    print "result:", result
    return result


def get_neighbours():
    """ Remote function to get neighbour list """
    neighbours = THIS_NODE.get_neighbour_list()
    return neighbours


def launch(host, commandline, stdout=None, stderr=None):
    """ Runs a cmd command either locally or on a remote host via SSH """
    cwd = os.getcwd()
    if host == 'localhost':
        pass
    else:
        commandline = "ssh -f %s 'cd %s; %s'" % (host, cwd, commandline)

    print commandline

    subprocess.Popen(commandline, shell=True, stdout=stdout, stderr=stderr)
    #Check if process started successfully
    print "damn"
    host = check_node_status(host)
    print "shit"
    return host

def check_node_status(host, status=None):
    """ Check the state of a remote node """
    while True:
        status = update_node_status(host, status)
        if status == "ok":
            return host
        if status == "error":
            return None

def update_node_status(host, status):
    """ Update or check the status of a remote node """
    if host in STATUS_DICT:
        #If the host is in the status dictionary, return the status
        status = STATUS_DICT.pop(host, None)
        return status
    if status != None:
        #Add a new host and status to the dictionary
        STATUS_DICT[host] = status

def create_host_list():
    """ Create a new list with available hosts """
    HOSTLIST.append("localhost:8010")
    HOSTLIST.append("localhost:8020")
    HOSTLIST.append("localhost:8030")
    return

def parse_args():
    """ Parse command line arguments """
    default_port = 8000
    default_timeout = 60
    parser = argparse.ArgumentParser(prog="nutella", description="P2P network")

    parser.add_argument("--caller", type=str, default=None,
        help="id of the node that started this node")

    parser.add_argument("-p", "--port", type=int, default=default_port,
    help="port number to listen on, default: {}".format(default_port))

    parser.add_argument("--timeout", type=float, default=default_timeout)

    return parser.parse_args()

def start_http(caller):
    """ Try to start a HTTP server.
        On error: exit """
    try:
        server = ThreadedHTTPServer(('', THIS_NODE.port), NodeHttpHandler)
    except:
        host, port = THIS_NODE.split_hostname(caller, ":")
        remote_name = THIS_NODE.create_remote_hostname(host, port)
        remote = xmlrpclib.ServerProxy(remote_name)
        host = THIS_NODE.full_name
        status = "error"
        remote.update_node_status(host, status)
        sys.exit(1)

    return server

def send_ok_response(host, port):
    """ Send startup "ok" response to remote node """
    remote_host = THIS_NODE.create_remote_hostname(host, port)
    remote = xmlrpclib.ServerProxy(remote_host)
    host = THIS_NODE.full_name
    status = "ok"
    remote.update_node_status(host, status)

def register_rpc_functions():
    """ Register all the RPC functions """
    RPC.register_function(update_node_status, 'update_node_status')
    RPC.register_function(remove_remote, 'remove_remote')
    RPC.register_function(get_neighbours, 'get_neighbours')

if __name__ == "__main__":
    ARGS = parse_args()
    HOSTNAME = socket.gethostname()
    THIS_NODE = Node(HOSTNAME, ARGS.port)
    print "Hostname: {}".format(THIS_NODE.full_name)
    HTTP_SERVER = start_http(ARGS.caller)

    RPC = ThreadedRPCServer(('', ARGS.port + 1), SimpleXMLRPCRequestHandler, \
        allow_none=True, logRequests=True)

    def run_server():
        """ Run the HTTP server forever """
        print "Running HTTP server"
        HTTP_SERVER.serve_forever()

    def run_rpc_server():
        """ Run the RPC server forever """
        if ARGS.caller != None:
            THIS_NODE.set_caller(ARGS.caller)
            #Need to check which name we send with
            name, port = THIS_NODE.split_hostname(THIS_NODE.caller, ":")
            send_ok_response(name, port)
        if ARGS.caller != None:
            fill_neighbour_list()
        print "Running RPC server"
        RPC.serve_forever()


    def shutdown_server_on_signal(signum, frame):
        """ Gracefull shutdown of server on ctrl+c """
        print "Server shutting down"
        RPC.shutdown()
        HTTP_SERVER.shutdown()

    register_rpc_functions()

    HTTP_THREAD = threading.Thread(target=run_server)
    HTTP_THREAD.daemon = True
    HTTP_THREAD.start()

    RPC_THREAD = threading.Thread(target=run_rpc_server)
    RPC_THREAD.daemon = True
    RPC_THREAD.start()

    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)

    HTTP_THREAD.join(ARGS.timeout)
    RPC_THREAD.join(ARGS.timeout)

    if HTTP_THREAD.isAlive():
        print "Reached timeout. Asking HTTP server to shut down"
        HTTP_SERVER.shutdown()
    if RPC_THREAD.isAlive():
        print "Reached timeout. Asking RPC server to shut down"


