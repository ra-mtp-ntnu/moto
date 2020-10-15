from moto.tcp_client import TcpClient


class IoConnection(TcpClient):

    TCP_PORT_IO = 50242

    def __init__(self, ip_address):
        self._address = (ip_address, IoConnection.TCP_PORT_IO)
        super().__init__(self._address)
