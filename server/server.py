from enum import Enum
import json
from socket import (
    AF_INET,
    socket,
    SOCK_STREAM,
)
from threading import Thread


class Status(Enum):
    FAILED = "FAILED"
    READY = "READY"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"


class ClientConnection(Thread):

    def __init__(self, host, port, target, *args):
        super().__init__(target=target, args=args)
        self._host = host
        self._port = port


class Server(object):

    HOST = "127.0.0.1"
    PORT = 9020
    BUFFER_SIZE = 1024
    MAX_CONNECTIONS = 100

    def __init__(self, *args, **kwargs):
        self._host = ""
        self._port = 8888
        self._status = Status.READY

        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__clients = {}
        self.__addresses = {}

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def status(self):
        return self._status

    def start(self, backlog=None):
        # (1) Enable the server to accept connections/clients.
        self.__socket.bind(address=(self.HOST, self.PORT))
        self.__socket.listen(backlog=(backlog or self.MAX_CONNECTIONS))
        print("[Server] Listening on {0}:[1}".format(self.HOST, self.PORT))

        # (2) Cleanup any previous connections. Right now,
        # this is just a sanity check.
        if not self._status.READY:
            self.__addresses.clear()
            self.__clients.clear()

        # (3) This is where we actually "start" the server
        # and begin accepting inbound connections/clients.
        while True:
            try:
                # Client socket and the address (host, port).
                client, address = self.__socket.accept()
                self.__addresses[client] = address
                # Respond to the client and let them know they were successfully.
                client.send(message("[Server] You are now connected!"))
                client.send(message("[Server] Please type your name!"))
                # Start a new ClientConnection Thread
                args = (client, )
                ClientConnection(
                    address[0],
                    address[1],
                    self.handle_client,
                    *args,
                ).start()

            except Exception:
                # Client data (client, address) was not
                # correct.
                print("[Server] Failed client connection")

    def handle_client(self, client):
        """ Handles a single Client connection. """
        username = client.recv(self.BUFFER_SIZE).decode("UTF8")
        # TODO: Let Client know available commands.
        client.send(message("[Server] Welcome type {quit} to exit."))
        self._broadcast(username, "{} has joined the chat!".format(username))
        self.__clients[client] = username
        while True:
            try:
                msg = client.recv(self.BUFFER_SIZE)
                if msg != message("{quit}"):
                    self._broadcast("{}: ".format(username), msg)
                else:
                    client.send(message("{quit}"))
                    client.close()
                    self.__clients.pop(client)
                    self._broadcast("{}: ".format(username), "has left the chat!")
                    break
            except:
                client.close()

    def _broadcast(self, prefix="", msg=""):
        """
        Broadcasts the message to the entire chat room.

        :param prefix: Username (i.e. "dkindt: ")
        :param message: Message to be broadcast.
        """
        full_message = message("{}{}".format(prefix, msg))
        for client in self.__clients:
            client.send(full_message)


def message(message):
    """ Encodes message to send to a client"""
    return bytes(message, "UTF8")

