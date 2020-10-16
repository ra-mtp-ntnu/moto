from typing import List

from moto.tcp_client import TcpClient
from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection
from moto.io_connection import IoConnection
from moto.control_group import ControlGroup


class Moto:
    def __init__(self, robot_ip: str, control_group_ids: List[str] = ["R1"]):
        self._robot_ip: str = robot_ip
        self._control_group_ids: List[str] = control_group_ids # TODO(Lars): Should probably be a dict

        self._motion_connection: MotionConnection = MotionConnection(self._robot_ip)
        self._state_connection: StateConnection = StateConnection(self._robot_ip)
        self._io_connection: IoConnection = IoConnection(self._robot_ip)

        self._control_groups: List[ControlGroup] = [
            ControlGroup(
                groupno,
                self._motion_connection,
                self._state_connection,
                self._io_connection,
            )
            for groupno in range(len(self._control_group_ids))
        ]

        self._motion_connection.start()
        self._state_connection.start()
        self._io_connection.start()

    @property
    def control_group(groupno:int) -> ControlGroup:
        return self._control_groups[groupno]
