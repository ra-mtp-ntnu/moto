from moto.simple_message_connection import SimpleMessageConnection
from moto.tcp_client import TcpClient


class IoConnection(SimpleMessageConnection):

    TCP_PORT_IO = 50242

    def __init__(self, ip_address):
        pass
