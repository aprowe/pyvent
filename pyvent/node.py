'''Node Class'''

from pydispatch import dispatcher
from functools import partial
from logging import getLogger
import time

from . client import Client
from . server import Server

log = getLogger(__name__)

class Node():
    '''
    Primary class that contains a server and client.
    '''

    Any = dispatcher.Any
    Anonymous = dispatcher.Anonymous

    defaults = {
        'server': True,
        'id': 'pyvent',
        'address': '0.0.0.0',
        'port': 52002,
    }

    def __init__(self, **options):
        self.options = {
            **Node.defaults,
            **options,
        }

        self.client = Client(port=self.options['port'])
        self.server = Server(port=self.options['port'])

    def configure(self, **kargs):
        self.options = {
            **self.options,
            **kargs,
        }

    def is_server(self):
        '''returns whether this node has a running server

        Node can be either a server, client or both. The first
        node to be started will also start server. This function
        will check if it is the server node

        :param self:
        :rtype: bool
        '''

        return self.server.is_alive()

    def start_server(self, port=None, address=None):
        '''Starts the pyvent server

        If it is already running, does nothing

        .. note:: This will be automatically called with :meth:`pyvent.node.Node.connect` and
            :meth:`pyvent.node.Node.send`

        :param port: The port to bind to
        :param address: The address to bind to
        :type port: int
        :type address: str
        :rtype: None
        '''

        if self.server.is_alive():
            log.warning("Server is already running")
            return

        if port is None:
            port = self.options['port']

        if address is None:
            address = self.options['address']

        self.server.port = port
        self.server.address = address
        self.server.start()

    def try_start(self):
        '''Attempts to start a client and server if needed

        Checks if a pyvent server is running, if it is, it creates a Client
        and connects to that. If a server is not running, it creates a server
        and then creates a client.

        If it is already running, does nothing

        .. note:: This will be automatically called with :meth:`pyvent.node.Node.connect` and
            :meth:`pyvent.node.Node.send`

        :rtype: None
        '''
        # Create server
        if self.options['server'] and not self.client.check():
            log.info(f"Starting server on '{self.options['id']}'")
            self.start_server()

        # Create client
        if not self.client.is_alive():
            # Start Client and wait for server to respond
            log.info(f"Starting Client '{self.options['id']}'")
            self.client.start(id=self.options['id'], wait=True)

    def connect(self, signal, callback=None, sender='pyvent', weak=True):
        # Allow for decorators
        if callback is None:
            return partial(self.connect, signal, sender=sender, weak=False)

        self.try_start()
        self.client.subscribe(signal)
        dispatcher.connect(callback, signal=signal, sender=sender, weak=weak)
        return callback

    def disconnect(self, callback, signal=Any, sender='pyvent', weak=True):
        dispatcher.disconnect(signal=signal, receiver=callback, sender=sender, weak=weak)

    def send(self, signal, **kargs):
        self.try_start()
        return self.client.send(signal, **kargs)

    def wait_for(self, signal, sender='pyvent', timeout=0, send=None):
        self.try_start()
        return self.client.wait_for(signal=signal, sender=sender, timeout=timeout, send=send)

    def stop(self, client=True, server=True):
        if self.client.is_alive() and client:
            self.client.stop()
            self.client = Client(port=self.options['port'])

        if self.server.is_alive() and server:
            self.server.stop()
            self.server = Server(port=self.options['port'])

    def __del__(self):
        self.stop()
