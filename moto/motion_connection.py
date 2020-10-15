from moto.simple_message_connection import SimpleMessageConnection
from moto.simple_message import (Prefix, Header, MsgType, CommType,
                                 ReplyType,  MotoMotionCtrl, MotoMotionReply, CommandType, ResultType)
from moto.tcp_client import TcpClient


class MotionConnection(SimpleMessageConnection):

    TCP_PORT_MOTION = 50240

    def __init__(self, ip_address):

        self._tcp_client = TcpClient((ip_address, self.TCP_PORT_MOTION))

    def _send_and_recv(self, body: MotoMotionCtrl):
        msg = Header(MsgType.MOTO_MOTION_CTRL,
                     CommType.SERVICE_REQUEST, ReplyType.INVALID).to_bytes()
        msg += body.to_bytes()
        msg = Prefix(len(msg)).to_bytes() + msg

        # TODO(Lars): Create and send message maybe in a Connection superclass?

        self._tcp_client.send(msg)
        return MotoMotionReply.from_bytes(self._tcp_client.recv())

    def _request(self, groupno: int, sequence: int, command: CommandType) -> MotoMotionCtrl:
        return MotoMotionCtrl(groupno, sequence, command)

    def check_motion_ready(self, groupno: int, sequence: int = -1):
        request = self._request(
            groupno, sequence, CommandType.CHECK_MOTION_READY.value)
        return self._send_and_recv(request)

    def check_queue_count(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.CHECK_QUEUE_CNT))

    def stop_motion(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.STOP_MOTION))

    def start_servos(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.START_SERVOS))

    def stop_servos(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.STOP_SERVOS))

    def reset_alarm(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.RESET_ALARM))

    def start_traj_mode(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.START_TRAJ_MODE))

    def stop_traj_mode(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.STOP_TRAJ_MODE))

    def disconnect(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(self._request(groupno, sequence, CommandType.DISCONNECT))
