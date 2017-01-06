#!/usr/bin/env python
""" Node class for use in gnutella """

class Node(object):
    """ A node in a P2P system """
    def __init__(self, host, port):
        self.neighbour = []
        self.hostname = host
        self.full_name = host + ":" + str(port)
        self.port = port
        self.rpc_name = None
        self.number_of_neighbours = 5
        self.caller = None

    def set_caller(self, caller):
        """ Set the caller variable """
        self.caller = caller

    def get_neighbour_list(self):
        """ Return the neighbour list """
        if len(self.neighbour) == 0:
            #The list is empty
            return None
        if len(self.neighbour) == 1:
            #Only one object in list, return first item
            return self.neighbour[0]
        else:
            return "\n".join(self.neighbour)

    def add_neighbour(self, host, port):
        """ Add a host to neighbour list """
        if len(self.neighbour) < self.number_of_neighbours:
            hostname = host + ":" + str(port)
            self.neighbour.append(hostname)
            print "Added neighbour"

    def remove_neighbour(self, name):
        """ Remove a host from neighbour list """
        if name in self.neighbour:
            self.neighbour.remove(name)

    def create_remote_hostname(self, host, port):
        """ Create a RPC compatible hostname """
        port = int(port) + 1
        hostname = "http://" + host + ":" + str(port)
        return hostname

    def split_hostname(self, name, symbol):
        """ Split hostname and return name and port """
        split = name.split(symbol)
        name = split[0]
        port = split[1]
        return name, port

