from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection
from moto.io_connection import IoConnection


class ControlGroup:

    MAX_CONTROLLABLE_GROUPS: int = 4

    def __init__(
        self,
        groupno: int,
        motion_connection: MotionConnection,
        state_connection: StateConnection,
        io_connection: IoConnection,
    ):
        self._groupno: int = groupno
        self._motion_connection: MotionConnection = motion_connection
        self._state_connection: StateConnection = state_connection
        self._io_connection: IoConnection = io_connection

    @property
    def position(self):
        self._state_connection.joint_feedback_for_group(self._groupno).position

    @property
    def velocity(self):
        self._state_connection.joint_feedback_for_group(self._groupno).velocity

    @property
    def acceleration(self):
        self._state_connection.joint_feedback_for_group(self._groupno).acceleration

    


