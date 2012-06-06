import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.setsockopt(zmq.LINGER, 0)    # discard unsent messages on close
socket.connect('tcp://127.0.0.1:5000')

while True:
    msg = raw_input('> ')
    if msg == 'quit':
        break
    else:
        socket.send(msg)
socket.close()
