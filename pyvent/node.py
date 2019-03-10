from pydispatch import dispatcher
from functools import partial
from logging import getLogger
import time

from . client import Client
from . server import Server

log = getLogger(__name__)

class Node():

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
