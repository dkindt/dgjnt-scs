from enum import Enum
from socket import (
    AF_INET,
    socket,
    SOCK_STREAM,
    SOL_SOCKET,
    SO_REUSEADDR,
)
from threading import Thread

# Default CONSTANTS
_HOST = "127.0.0.1"
_PORT = 9020
_MAX_MESSAGE_SIZE = 1024
_MAX_ACTIVE_CONNECTIONS = 100


class Status(Enum):
    FAILED = -1
    READY = 0
    RUNNING = 1
    STOPPED = 2


class Server(object):

    AVAILABLE_COMMANDS = [
        "help",
        "name",
        "get",
        "push",
        "adios",
    ]

    def __init__(self, host, port, **kwargs):
        """
        The host and port number are required to have initialize
        this Server.
        """
        self._host = host
        self._port = port
        self._max_active_connections = kwargs.get(
            "MAX_ACTIVE_CONNECTIONS", _MAX_ACTIVE_CONNECTIONS)
        self._max_message_size = kwargs.get(
            "MAX_MESSAGE_SIZE", _MAX_MESSAGE_SIZE)
        self._status = Status.READY
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__clients = []

    @property
    def host(self):
        return self._host

    @property
    def max_active_connections(self):
        return self._max_active_connections
    
    @property
    def max_message_size(self):
        return self._max_message_size

    @property
    def port(self):
        return self._port

    @property
    def status(self):
        return self._status

    def prompt(self, name):
        """ Helper to prompt a Client with available commands. """
        msg = """
        Here are the available commands:
        {0} -- Displays this prompt again.
        {1} -- Update your username.
        {2} -- View chat history.
        {3} -- Send chat message.
        {4} -- Leave the chat room.        
        """.format(name, *self.AVAILABLE_COMMANDS)
        return msg

    def start(self, backlog=None):
        # (1) Enable the server to accept connections/clients.
        # socket.setsockopt is to avoid socket timeouts.
        self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__socket.bind(address=(self.host, self.port))
        self.__socket.listen(backlog=(backlog or self.max_active_connections))
        # (2) Cleanup any previous connections.
        if not self._status.READY:
            self.__clients.clear()
        # (3) This is where we actually "start" the server
        # and begin accepting inbound connections/clients.
        listener = Thread(target=self.listen)
        listener.start()
        listener.join()
        self.__socket.close()

    def listen(self):
        """ Listen for inbound connections from clients """
        self._status = Status.RUNNING
        while self.status.RUNNING:
            client = _Client(*self.__socket.accept())
            self.__clients.append(client)
            client.communicate("Welcome to Group 10's Server!")
            client.communicate("Please enter a username: ")
            # Create a thread to handle the client's requests.
            client_thread = Thread(target=self.handle_client, args=(client, ))
            client_thread.start()

    def handle_client(self, client):
        """ Process any Client requests from the client """
        # Get the Client's name, prompt them with the available
        # commands, and then introduce them to the entire chat
        # room.
        client.username = client.get_input()
        client.communicate(self.prompt(client.username))
        self.broadcast("{} has joined the chat!".format(client.username))

        # As long as the Client is active (hasn't typed 'adios'), then
        # process their requests.
        is_active = True
        while is_active:
            data = client.get_input()
            if data != "adios":
                self.broadcast("{}: {}".format(client.username, data))
            else:
                client.communicate("Adios!")
                self.__clients.remove(client)
                client.disconnect()
                self.broadcast("{} left the chat".format(client.username))
                is_active = False

    def broadcast(self, msg):
        """ Broadcasts the given message to all active Clients """
        if not isinstance(msg, bytes):
            msg = message(msg)

        for client in self.__clients:
            client.communicate(msg)


class _Client(object):
    """ Helper class to keep track of a connected clients """
    def __init__(self, socket_, host, port):
        self._socket = socket_
        self._host = host
        self._port = port
        self._message_size = _MAX_MESSAGE_SIZE
        self._username = None

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    def communicate(self, data):
        """ Send a message to the client """
        if not isinstance(data, bytes):
            # Convert the string of data to bytes
            data = message(data)
        self._socket.send(data)

    def disconnect(self):
        """ Closes the connection to Client """
        self._socket.close()

    def fileno(self):
        """
        Pass along the server's fileno() reference.
        This lets allows the Client to pretend it's
        a socket.
        """
        return self._socket.fileno()

    def get_input(self):
        """ Get input from the Client and clean the data """
        data = self._socket.recv(self._message_size)
        return data.decode("UTF8").strip()


def message(msg, prefix=""):
    """
    Helper to encode a string to bytes so that the server is able to
    communicate with the clients.

    :param msg: The message to encode (if not already done)
    :param prefix: The username or prefix to prepend to msg
    :return encoded utf8 bytes message ready to send.
    """
    if prefix and not prefix.strip().endswith(":"):
        prefix = "{}: ".format(prefix)
    full_message = "".format(prefix, msg)
    return bytes(full_message, "UTF8")
