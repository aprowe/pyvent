import time
from pymitter.node import Node
import nose.tools as nt
from multiprocessing import Process, Value

S = Value('i', 0)


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


def run():
    n = Node()
    @n.connect('event')
    def fn(arg):
        S.value = arg

    time.sleep(1)

def test_emit():
    p = Process(target=run)
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

    p = Process(target=run)
    p.start()

    time.sleep(0.1)
    n.send('event', arg=3)
    time.sleep(0.1)
    nt.assert_equal(S.value, 3)

    nt.assert_true(n.is_server())

    time.sleep(0.1)
    n.send('event', arg=2)
    time.sleep(0.1)
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
