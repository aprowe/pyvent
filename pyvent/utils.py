import pickle

ACK = b'1'


def unmarshall(msg):
    try:
        index = msg.index(b' ')
        payload = pickle.loads(msg[index+1:])
    except ValueError:
        index = None
        payload = {}

    topic = msg[0:index].decode()

    return topic, payload


def marshall(topic, payload={}):
    msg = topic.encode() + b' ' + pickle.dumps(payload)
    return msg
