#!/usr/bin/env python
""" Node class for use in gnutella """

class Node(object):
    """ A node in a P2P system """
    def __init__(self, host, port):
        self.neighbour = []
        self.hostname = host
        self.port = port
        self.rpc_name = None

    def get_neighbour_list(self):
        """ Return the neighbour list """
        return self.neighbour

    def add_neighbour(self):
        """ Add a host to neighbour list """

    def remove_neighbour(self):
        """ Remove a host from neighbour list """

    def create_remote_hostname(self):
        """ Create a RPC compatible hostname """

    def split_hostname(self):
        """ Split hostname and return name and port """
