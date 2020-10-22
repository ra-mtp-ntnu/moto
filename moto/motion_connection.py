from moto.simple_message_connection import SimpleMessageConnection
from moto.simple_message import (
    Prefix,
    Header,
    MsgType,
    CommType,
    ReplyType,
    MotoMotionCtrl,
    MotoMotionReply,
    CommandType,
    ResultType,
    SimpleMessage,
)
from moto.tcp_client import TcpClient


class MotionConnection(SimpleMessageConnection):

    TCP_PORT_MOTION = 50240

    def __init__(self, ip_address):

        self._tcp_client = TcpClient((ip_address, self.TCP_PORT_MOTION))

    def _send_and_recv(self, body: MotoMotionCtrl):
        header = Header(
            MsgType.MOTO_MOTION_CTRL, CommType.SERVICE_REQUEST, ReplyType.INVALID
        )

        self._tcp_client.send(msg)
        response = self._tcp_client.recv()

        prefix = Prefix.from_bytes(response[:4])
        header = Header.from_bytes(response[4:16])
        body = MotoMotionReply.from_bytes(response[16:76])

        return body

    def _request(
        self, groupno: int, sequence: int, command: CommandType
    ) -> MotoMotionCtrl:
        return MotoMotionCtrl(groupno, sequence, command)

    def start(self):
        self._tcp_client.connect()

    def check_motion_ready(self):

        request = SimpleMessage(
            Header(
                MsgType.MOTO_MOTION_CTRL, CommType.SERVICE_REQUEST, ReplyType.INVALID
            ),
            MotoMotionCtrl(-1, -1, CommandType.CHECK_MOTION_READY),
        )
        
        self._tcp_client.send(request.to_bytes())
        response = SimpleMessage.from_bytes(self._tcp_client.recv())
        assert response.header.msg_type == MsgType.MOTO_MOTION_REPLY

        return response.body

    def check_queue_count(self, groupno: int = -1, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.CHECK_QUEUE_CNT)
        )

    def stop_motion(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.STOP_MOTION)
        )

    def start_servos(self, groupno: int = -1, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.START_SERVOS)
        )

    def stop_servos(self, groupno: int = -1, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.STOP_SERVOS)
        )

    def reset_alarm(self, groupno: int = -1, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.RESET_ALARM)
        )

    def start_traj_mode(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.START_TRAJ_MODE)
        )

    def stop_traj_mode(self, groupno: int, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.STOP_TRAJ_MODE)
        )

    def disconnect(self, groupno: int = -1, sequence: int = -1):
        return self._send_and_recv(
            self._request(groupno, sequence, CommandType.DISCONNECT)
        )
