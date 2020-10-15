import socket


class TcpClient:
    def __init__(self, address):
        self._address = address
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self._socket.connect(self._address)

    def send(self, data):
        self._socket.sendall(data)

    def recv(self, bufsize: int = 1024):
        return self._socket.recv(bufsize)
