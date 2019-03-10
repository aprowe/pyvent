import zmq
import logging
import time

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

        self.req_endpoint = f"tcp://{self.address}:{self.port}"
        self.sub_endpoint = f"tcp://{self.address}:{self.port+1}"

        self.start_req()

    def check(self, rep=1):
        for i in range(rep):
            if self.send('__check', id=id(self)):
                return True

        return False

    def wait_for_server(self):
        return self.check(10)

    def wait_for(self, signal, sender='pyvent', timeout=0, send=None):
        ret_val = None, None

        def fn(*args, **kargs):
            nonlocal ret_val
            ret_val = (args, kargs)
        dispatcher.connect(receiver=fn, signal=signal, sender=sender, weak=False)
        self.subscribe(signal)

        if send:
            self.send(**send)

        time_started = time.time()
        while not ret_val[0] and self.is_alive():
            if timeout and time.time() - time_started > timeout:
                log.info(f'Wait for {signal} timed out')
                break

        dispatcher.disconnect(receiver=fn, signal=signal, sender=sender, weak=False)

        return ret_val

    def start(self, id=None, wait=True):
        if not id:
            id = f'pyvent.{hex(id(self))}'
        self.id = id

        # Start sub thread
        super().start()

        # Start req socket
        self.start_req(reset=True)

        # Wait for server and send connect
        wait and self.wait_for_server()
        self.send('__connect', id=self.id)

    def run(self):
        self.start_sub()

        self.should_stop = False
        while not self.should_stop:
            try:
                msg = self.sub.recv()
            except zmq.Again:
                continue

            topic, payload = unmarshall(msg)

            payload.setdefault('sender', self.id)
            dispatcher.send(signal=topic, **payload)

        self.sub.disconnect(self.sub_endpoint)

    def send(self, signal, **kargs):
        try:
            self.req.send(marshall(signal, kargs))
            return self.req.recv() == ACK
        except zmq.Again:
            log.error(f"Client could not send message: {signal}")

        except zmq.ZMQError:
            log.error(f"Client could not send message: {signal}")
            self.start_req(True)

        return False

    def subscribe(self, sub=''):
        self.sub.setsockopt_string(zmq.SUBSCRIBE, sub)

    def start_req(self, reset=False):
        if reset:
            self.req.close()

        self.req = self.ctx.socket(zmq.REQ)
        self.req.setsockopt(zmq.RCVTIMEO, 50)
        self.req.connect(self.req_endpoint)

    def start_sub(self, reset=False):
        if reset:
            self.sub.close()

        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.setsockopt(zmq.RCVTIMEO, 10)
        self.sub.connect(self.sub_endpoint)
        self.subscribe('__')

    def __del__(self):
        self.stop()

    def stop(self):
        # Wait for Sub to stop
        if self.is_alive():
            self.should_stop = True
            self.join()

        return
        # disconnect req
        self.send('__disconnect')
        self.req.disconnect(self.req_endpoint)
