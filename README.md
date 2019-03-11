# Pyvent

Pyvent is a dead-simple IPC to use that uses [ZMQ](https://pyzmq.readthedocs.io/en/latest/api/zmq.html) and [PyDispatcher](https://grass.osgeo.org/grass77/manuals/libpython/pydispatch.html) under the hood.

### Concept
For python, ZMQ is one of the best options for a fast, easy IPC. The only problem is the relatively high amount of boilerplate code to get basic communication going between two processes. Pyvent is made to have all of
the benefits of a ZMQ IPC, with zero boiler plate code. The API uses a basic event emitter pattern, handling all threads and ZMQ behind the scenes. The ZMQ messages are basic enough that you could hook into the server from another language.

## Installation
```python
pip install pyvent
```

Pyvent requires python 3.6 or higher

## Usage

Pyvent employs a observer, event based pattern common in javascript and Qt. It uses PyDispatcher under the hood, and follows syntax as closely as possible to that.


### Basic

```python
# script1.py
import pyvent

@pyvent.connect('order-food')
def order(food, drink='water'):
  print(f'You ordered {food} and {drink}!')
```


```python
# script2.py
import pyvent

pyvent.send('order-food', food='sushi', drink='sake')
```

```shell
$ python3 script1.py &
$ python3 script2.py
> You ordered sushi and sake!
```

### Features

#### Connect as a decorator
Connect can be called as a decorator or a normal function with a callback argument
```python
import pyvent
@pyvent.connect('food-burnt')
def fn():
    print('Food is burnt :(')

# Same as
pyvent.connect('food-burnt', fn)
```

#### Nodes
Calling methods on the module are all proxy functions that call an underlying class called `Node`, which is the combination of a client and sometimes a server. For most use cases you can simply import `pyvent` and call it's module functions but for use in `multiprocessing` threads you likely need to manually start a node.

```python
import pyvent
from pyvent import Node
from multiprocessing import Process
from time import time

def process():
    node = Node()

    @node.connect('make-food')
    def fn(food):
        print(f'Making {food}')

    time.sleep(1)

# Create a process
p = Process(target=process)
p.start()

# Create a node on this process
# (Note that pyvent global functions would work too)
pyvent.send('make-food', food='chicken')

p.terminate()
```

#### Manually Starting Server
You may want more control over which process the server belongs to, and when it is started. Note that this happens on the first `send` or `connect` call
```python
pyvent.start_server()
```

#### Blocking Listeners
`pyvent.wait_for` is similar to connect, but will wait for a response and return the results. A timeout can be placed, and if it times out the response will be a tuple of `(None, None)`

```python
import pyvent

args, kargs = pyvent.wait_for('food-ready', timeout=1)

if kargs:
    print(f'Food ready: {kargs["food"]}')
else:
    print('Took too long!')
```

#### Configuration
There are several options that can be configured. As of v0.1.1, these has to be entered before any other calls
```python
import pyvent

pyvent.configure(
    # Default port that communication will be on
    # Note that as of v0.1.1 port and port + 1 will be used
    port=50020,

    # If False, the this process will not spawn a server
    # Ff True, will only start up if needed
    server=True,

    # ID of this process for identifying its calls
    id='pyvent'
)

# These options can also be entered into Node as construction arguments
node = pyvent.Node(server=False)
```

#### Stopping
To close all communication and halt threads, a `pyvent.stop()` call is needed. Upon deletion, `stop()` will be called.
Note that as of v0.1.1 stopping is sometimes buggy and blocks

#### Senders
To differentiate pyvent calls with other pydispatch calls, the default
sender parameter on all connects and sends is 'pyvent'.
If a client has an id set, it's calls will be 'pyvent.{id}'.
If you call `send` or `connect` with a `sender` parameter, it will overwrite that. Note that due to traveling to another process,
instances can not be senders, only serializable objects.

```python
import pyvent
from pydispatch import dispatcher

@pyvent.connect('new-customer', sender='customer-manager')
def fn(name):
    print(f'A customer has arrived: {name}')

# only sender='customer-manager.*' will trigger the vent
pyvent.send('new-customer', sender='customer-manager')

# This will also trigger the event
dispatcher.send(signal='new-customer', sender='customer-manager')
```
