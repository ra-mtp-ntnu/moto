
class ControlGroup:

    MAX_CONTROLLABLE_GROUPS: int = 4

    def __init__(
        self,
        groupno: int,
        motion_connection: "MotionConnection",
        state_connection: "StateConnection",
        io_connection: "IoConnection",
    ):
        self._groupno: int = groupno
        self._motion_connection: "MotionConnection" = motion_connection
        self._state_connection: "StateConnection" = state_connection
        self._io_connection: "IoConnection" = io_connection

    @property
    def position(self):
        return self._state_connection.joint_feedback_for_group(self._groupno).pos

    @property
    def velocity(self):
        return self._state_connection.joint_feedback_for_group(self._groupno).vel

    @property
    def acceleration(self):
        return self._state_connection.joint_feedback_for_group(self._groupno).acc

    


