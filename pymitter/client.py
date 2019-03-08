import zmq
import logging

from pydispatch import dispatcher
from threading import Thread

from . utils import ACK, marshall, unmarshall

log = logging.getLogger(__name__)


class Client(Thread):

    def __init__(self, port=52002, address='0.0.0.0'):
        Thread.__init__(self, daemon=True)

        self.port = port
        self.address = address
        self.id = None
        self.should_stop = False

        self.ctx = zmq.Context()
        self.req = self.ctx.socket(zmq.REQ)
        self.sub = self.ctx.socket(zmq.SUB)
        self.req.setsockopt(zmq.RCVTIMEO, 10)
        self.sub.setsockopt(zmq.RCVTIMEO, 10)
        self.subscribe('__')

    def check(self):
        if self.is_alive():
            return self.send('__check')

        req = self.ctx.socket(zmq.REQ)
        req.setsockopt(zmq.RCVTIMEO, 10)

        # Try to connect
        try:
            req.connect(f"tcp://{self.address}:{self.port}")

        # Connection failed, no server
        except zmq.error.ZMQError:
            return False

        # Connection succeed, send check pyaload
        try:
            req.send(b'__check')
            if req.recv() == ACK:
                return True

        # Any Error
        except zmq.Again:
            return False

        # Disconnect
        finally:
            req.close()

        return False

    def wait_for_server(self):
        checked = False

        def fn():
            nonlocal checked
            checked = True

        dispatcher.connect(fn, signal='__check')

        for i in range(10):
            self.send('__check')

            if checked:
                break

        dispatcher.disconnect(fn, signal='__check')

    def start(self, id=None, wait=True):
        super().start()

        self.id = id
        wait and self.wait_for_server()
        self.send('__connect', id=self.id)

    def run(self):
        self.req.connect(f"tcp://{self.address}:{self.port}")
        self.sub.connect(f"tcp://{self.address}:{self.port + 1}")

        self.should_stop = False
        while not self.should_stop:
            try:
                msg = self.sub.recv()
            except zmq.Again:
                continue

            topic, payload = unmarshall(msg)

            payload.setdefault('sender', self.id)
            dispatcher.send(signal=topic, **payload)

        self.req.disconnect(f"tcp://{self.address}:{self.port}")
        self.sub.disconnect(f"tcp://{self.address}:{self.port + 1}")

    def send(self, topic, **kargs):
        try:
            self.req.send(marshall(topic, kargs))
            return self.req.recv() == ACK
        except zmq.Again:
            log.error(f"Client could not send message: {topic}")

        return False

    def subscribe(self, sub=''):
        self.sub.setsockopt_string(zmq.SUBSCRIBE, sub)

    def __del__(self):
        self.stop()

    def stop(self):
        if not self.is_alive():
            return

        # self.send('__disconnect', id=self.id)
        self.should_stop = True
        self.join()
