import zmq
import logging
from threading import Thread

from . utils import ACK

log = logging.getLogger(__name__)


class Server(Thread):

    def __init__(self, port=52002, address='0.0.0.0'):
        Thread.__init__(self, daemon=True)
        self.port = port
        self.address = address
        self.should_stop = False

    def run(self):
        log.info(f'Starting server on port {self.port}')
        self.ctx = zmq.Context()

        self.rep = self.ctx.socket(zmq.REP)
        self.rep.setsockopt(zmq.RCVTIMEO, 10)

        self.pub = self.ctx.socket(zmq.PUB)

        log.info(f'binding..')
        self.rep.bind(f"tcp://{self.address}:{self.port}")
        self.pub.bind(f"tcp://{self.address}:{self.port + 1}")

        self.should_stop = False
        while not self.should_stop:
            try:
                msg = self.rep.recv()
            except zmq.Again:
                continue

            self.rep.send(ACK)
            self.pub.send(msg)

        self.rep.unbind(f"tcp://{self.address}:{self.port}")
        self.pub.unbind(f"tcp://{self.address}:{self.port + 1}")

    def __del__(self):
        self.stop()

    def stop(self):
        if not self.is_alive():
            return

        self.pub.send(b'__server_disconnect')
        self.should_stop = True
        self.join()
