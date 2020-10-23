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
        super().__init__((ip_address, self.TCP_PORT_MOTION))

    def _send_and_recv_command_request(self, command: CommandType) -> SimpleMessage:
        request = SimpleMessage(
            Header(
                MsgType.MOTO_MOTION_CTRL, CommType.SERVICE_REQUEST, ReplyType.INVALID
            ),
            MotoMotionCtrl(-1, -1, command),
        )
        response = self.send_and_recv(request)
        return response

    def check_motion_ready(self):
        return self._send_and_recv_command_request(CommandType.CHECK_MOTION_READY)

    def check_queue_count(self):
        return self._send_and_recv_command_request(CommandType.CHECK_QUEUE_CNT)

    def stop_motion(self):
        return self._send_and_recv_command_request(CommandType.STOP_MOTION)

    def start_servos(self):
        self._send_and_recv_command_request(CommandType.START_SERVOS)

    def stop_servos(self):
        return self._send_and_recv_command_request(CommandType.STOP_SERVOS)

    def reset_alarm(self):
        self._send_and_recv_command_request(CommandType.RESET_ALARM)

    def start_traj_mode(self):
        self._send_and_recv_command_request(CommandType.START_TRAJ_MODE)

    def stop_traj_mode(self):
        self._send_and_recv_command_request(CommandType.STOP_TRAJ_MODE)

    def disconnect(self):
        self._send_and_recv_command_request(CommandType.DISCONNECT)
