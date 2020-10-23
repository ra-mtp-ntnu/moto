from moto.simple_message import (
    JointTrajPtFull,
    Header,
    MsgType,
    CommType,
    ReplyType,
    SimpleMessage,
)


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
    def groupno(self):
        return self._groupno

    @property
    def joint_feedback(self):
        return self._state_connection.joint_feedback(self._groupno)

    def send_joint_traj_pt_full(self, joint_traj_pt_full: JointTrajPtFull) -> None:
        msg = SimpleMessage(
            header=Header(
                msg_type=MsgType.JOINT_TRAJ_PT_FULL,
                comm_type=CommType.TOPIC,
                reply_type=ReplyType.INVALID,
            ),
            body=joint_traj_pt_full,
        )
        self._motion_connection.send(msg)

