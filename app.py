import os

import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install()

import tornado
import tornado.web
import tornadio
import tornadio.router
import tornadio.server

ROOT = os.path.normpath(os.path.dirname(__file__))


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class ClientConnection(tornadio.SocketConnection):
    clients = set()

    @classmethod
    def dispatch_message(cls, message):
        for client in cls.clients:
            client.send(message)

    def on_open(self, *args, **kwargs):
        self.clients.add(self)

    def on_message(self, message):
        pass

    def on_close(self):
        self.clients.remove(self)

WebClientRouter = tornadio.get_router(ClientConnection)


application = tornado.web.Application(
    [(r"/", IndexHandler), WebClientRouter.route()],
    enabled_protocols = ['websocket', 'flashsocket', 'xhr-multipart', 'xhr-polling'],
    flash_policy_port = 843,
    flash_policy_file = os.path.join(ROOT, 'flashpolicy.xml'),
    socket_io_port = 8001
)

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind('tcp://127.0.0.1:5000')
    socket.setsockopt(zmq.SUBSCRIBE, '')
    stream = zmqstream.ZMQStream(socket, tornado.ioloop.IOLoop.instance())
    stream.on_recv(ClientConnection.dispatch_message)

    tornadio.server.SocketServer(application)
