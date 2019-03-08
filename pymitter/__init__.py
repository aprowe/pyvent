'''
Pymitter IPC
'''

from . node import Node

__version__ = '0.1.0'

options = Node.defaults

node = Node()


def configure(**kargs):
    '''
    Sets global configuration options
    Options are:
    server (bool): Wether or not this node can be a server
    id (string): ID of this node to be sent with every request
    address (string): Destination IP Address of messages
    port (int): Port to communicate over
    Must be configured before any other calls are made
    '''
    node.configure(**kargs)


def is_server():
    '''Returns whether or not this process is running a server'''
    return node.is_server()


def start_server(port=None, address=None):
    '''Starts the pymitter server thread'''
    return node.start_server(port, address)


def try_start():
    '''Attemps to start up the client and server'''
    return node.try_start()


def connect(signal, callback=None, sender='pymitter', weakref=True):
    '''
    Subscribes to a message. Can be used as a decorator.
    '''
    return node.connect(signal, callback, sender=sender, weakref=weakref)


def send(topic, **kargs):
    '''
    Sends a message to the server
    '''
    return node.send(topic, **kargs)


def stop(client=True, server=True):
    '''
    Closes down either the client or server or both
    '''
    return node.stop(client, server)
