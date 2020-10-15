from moto.tcp_client import TcpClient


class MotionConnection(TcpClient):

    TCP_PORT_MOTION = 50240

    def __init__(self, ip_address):
        super().__init__((ip_address, MotionConnection.TCP_PORT_MOTION))




