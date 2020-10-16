from moto.tcp_client import TcpClient
from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection
from moto.io_connection import IoConnection


class Moto:
    def __init__(self, robot_ip: str):
        self._robot_ip: str = robot_ip

        self._motion_connection: MotionConnection = MotionConnection(self._robot_ip)
        self._state_connection: StateConnection = StateConnection(self._robot_ip)
        # self._io_connection: IoConnection = IoConnection(self._robot_ip)

        self._motion_connection.start()
        self._state_connection.start()

    @property
    def motion_connection(self):
        return self._motion_connection

    @property
    def state_connection(self):
        return self._state_connection

    @property
    def io_connection(self):
        pass

    @property
    def position(self):
        return self._state_connection.joint_feedback.pos

    @property
    def velocity(self):
        return self._state_connection.joint_feedback.pos

    @property
    def acceleration(self):
        return self._state_connection.joint_feedback.pos

    def joint_feedback(self):
        return self._state_connection.joint_feedback

