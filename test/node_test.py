import time
from pyvent.node import Node
import nose.tools as nt
from multiprocessing import Process, Value

S = Value('i', 0)


def send_fn(signal='event', delay=0.25, **kargs):
    n = Node(id='process', server=False)

    time.sleep(delay)
    n.send(signal,  **kargs)
    time.sleep(delay)



def listen_fn(signal='event', delay=1):
    n = Node()
    @n.connect(signal)
    def fn(arg):
        S.value = arg

    time.sleep(delay)


def test_is_alive():
    node = Node()

    nt.assert_false(node.is_server())
    node.start_server()
    nt.assert_true(node.is_server())
    node.stop()
    nt.assert_false(node.is_server())


def test_start():
    node = Node()

    nt.assert_false(node.is_server())

    hit = False

    @node.connect('test')
    def fn():
        nonlocal hit
        hit = True

    nt.assert_true(node.is_server())
    nt.assert_false(hit)
    time.sleep(0.1)

    node.send('test')
    time.sleep(0.1)

    nt.assert_true(hit)
    node.stop()

def test_emit():
    p = Process(target=listen_fn)
    p.start()

    n = Node()

    time.sleep(0.1)
    n.send('event', arg=1)
    time.sleep(0.1)
    nt.assert_equal(S.value, 1)

    nt.assert_false(n.is_server())

    time.sleep(0.1)
    n.send('event', arg=2)
    time.sleep(0.1)
    nt.assert_equal(S.value, 2)

    n.stop()
    p.terminate()

def test_emit_2():
    n = Node()
    nt.assert_true(n.send('event', arg=3))

    p = Process(target=listen_fn)
    p.start()

    time.sleep(0.2)
    n.send('event', arg=3)
    time.sleep(0.2)
    nt.assert_equal(S.value, 3)

    nt.assert_true(n.is_server())

    time.sleep(0.2)
    n.send('event', arg=2)
    time.sleep(0.2)
    nt.assert_equal(S.value, 2)

    n.stop()
    p.terminate()


def test_stop_start():
    n = Node()
    n.start_server()
    n.stop()
    n.start_server()


def test_delete():
    n = Node()
    n.send('test')

    n2 = Node()
    n2.send('test')

    nt.assert_true(n.is_server())
    nt.assert_false(n2.is_server())

    del n
    n3 = Node()
    n3.send('test')
    nt.assert_true(n3.is_server())


def test_restart():
    n = Node()
    n.send('test')

    n2 = Node()
    n2.send('test')


    # n2.send('test')


def test_wait_for():
    n = Node()
    n.start_server()

    p = Process(target=send_fn, kwargs={'arg1': 'value'})
    time.sleep(0.1)
    p.start()

    args, kargs = n.wait_for('event', timeout=1)

    nt.assert_equal(kargs['arg1'], 'value')
    nt.assert_equal(args, ())
    p.terminate()


def test_wait_for_timeout():
    n = Node()
    n.start_server()
#
    args, kargs = n.wait_for('event', timeout=1)

    nt.assert_equal(args, None)
    nt.assert_equal(kargs, None)

def test_wait_with_send():
    n = Node()
    n.try_start()
    time.sleep(0.5)

    args, kargs = n.wait_for('test_event', timeout=2, send={'signal': 'test_event', 'value': 1})

    nt.assert_equal(kargs['value'], 1)

def test_configure():
    n = Node()
    n.try_start()

    time.sleep(1)
    n.configure(server=False)
