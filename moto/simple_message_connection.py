from moto.tcp_client import TcpClient
from moto.simple_message import SimpleMessage


class SimpleMessageConnection:
    def __init__(self, addr) -> None:
        self._tcp_client = TcpClient(addr)

    def start(self):
        self._tcp_client.connect()

    def send(self, msg: SimpleMessage) -> None:
        self._tcp_client.send(msg.to_bytes())

    def recv(self) -> SimpleMessage:
        return SimpleMessage.from_bytes(self._tcp_client.recv())

    def send_and_recv(self, msg: SimpleMessage) -> SimpleMessage:
        self.send(msg)
        return self.recv()
