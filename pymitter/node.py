from pydispatch import dispatcher
from functools import partial
from logging import getLogger
from . client import Client
from . server import Server

log = getLogger(__name__)

class Node():

    defaults = {
        'server': True,
        'id': 'pymitter',
        'address': '0.0.0.0',
        'port': 52002,
    }

    def __init__(self, **options):
        self.client = Client()
        self.server = Server()

        self.options = {
            **Node.defaults,
            **options,
        }

    def configure(self, **kargs):
        self.options = {
            **self.options,
            **kargs,
        }

    def is_server(self):
        return self.server.is_alive()

    def start_server(self, port=None, address=None):
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
        if self.client.is_alive():
            return

        # Create client
        if self.options['server'] and not self.client.check():
            log.info('Starting server on node')
            self.start_server(port=self.options['port'], address=self.options['address'])

        # Start Client and wait for server to respond
        log.info('Starting Client on node')
        self.client.start(id=self.options['id'])
        self.client.wait_for_server()

    def connect(self, signal, callback=None, sender='pymitter', weakref=True):
        if callback is None:
            return partial(self.connect, signal, sender=sender, weakref=False)

        self.try_start()
        self.client.subscribe(signal)
        dispatcher.connect(callback, signal=signal, sender=sender, weak=weakref)

    def send(self, topic, **kargs):
        self.try_start()
        return self.client.send(topic, **kargs)


    def stop(self, client=True, server=True):
        if self.client.is_alive() and client:
            self.client.stop()
            self.client = Client()

        if self.server.is_alive() and server:
            self.server.stop()
            self.server = Server()

    def __del__(self):
        self.stop()
