from dataclasses import dataclass
from enum import Enum

from typing import List


@dataclass
class Prefix:
    length: int


class MsgType(Enum):
    GET_VERSION = 2
    ROBOT_STATUS = 13

    JOINT_TRAJ_PT_FULL = 14
    JOINT_FEEDBACK = 15

    MOTO_MOTION_CTRL = 2001
    MOTO_MOTION_REPLY = 2002

    MOTO_READ_IO_BIT = 2003
    MOTO_READ_IO_BIT_REPLY = 2004
    MOTO_WRITE_IO_BIT = 2005
    MOTO_WRITE_IO_BIT_REPLY = 2006
    MOTO_READ_IO_GROUP = 2007
    MOTO_READ_IO_GROUP_REPLY = 2008
    MOTO_WRITE_IO_GROUP = 2009
    MOTO_WRITE_IO_GROUP_REPLY = 2010
    MOTO_IOCTRL_REPLY = 2011

    MOTO_JOINT_TRAJ_PT_FULL_EX = 2016
    MOTO_JOINT_FEEDBACK_EX = 2017
    MOTO_SELECT_TOOL = 2018

    MOTO_GET_DH_PARAMETERS = 2020


class CommType(Enum):
    INVALID = 0
    TOPIC = 1
    SERVICE_REQUEST = 2
    SERVICE_REPLY = 3


class ReplyType(Enum):
    INVALID = 0
    SUCCESS = 1
    FAILURE = 2


class CommandType(Enum):
    CHECK_MOTION_READY = 200101
    CHECK_QUEUE_CNT = 200102
    STOP_MOTION = 200111
    START_SERVOS = 200112  # starts the servo motors
    STOP_SERVOS = 200113  # stops the servo motors and motion
    RESET_ALARM = 200114  # clears the error in the current controller
    START_TRAJ_MODE = 200121
    STOP_TRAJ_MODE = 200122
    DISCONNECT = 200130


class ResultType(Enum):
    SUCCESS = 0
    TRUE = 0
    BUSY = 1
    FAILURE = 2
    FALSE = 2
    INVALID = 3
    ALARM = 4
    NOT_READY = 5
    MP_FAILURE = 6


class InvalidSubCode(Enum):
    INVALID_UNSPECIFIED = 3000
    INVALID_MSGSIZE = 3001
    INVALID_MSGHEADER = 3002
    INVALID_MSGTYPE = 3003
    INVALID_GROUPNO = 3004
    INVALID_SEQUENCE = 3005
    INVALID_COMMAND = 3006
    INVALID_DATA = 3010
    INVALID_DATA_START_POS = 3011
    INVALID_DATA_POSITION = 3011
    INVALID_DATA_SPEED = 3012
    INVALID_DATA_ACCEL = 3013
    INVALID_DATA_INSUFFICIENT = 3014
    INVALID_DATA_TIME = 3015
    INVALID_DATA_TOOLNO = 3016


class NotReadySubcode(Enum):
    NOT_READY_UNSPECIFIED = 5000
    NOT_READY_ALARM = 5001
    NOT_READY_ERROR = 5002
    NOT_READY_ESTOP = 5003
    NOT_READY_NOT_PLAY = 5004
    NOT_READY_NOT_REMOTE = 5005
    NOT_READY_SERVO_OFF = 5006
    NOT_READY_HOLD = 5007
    NOT_READY_NOT_STARTED = 5008
    NOT_READY_WAITING_ROS = 5009
    NOT_READY_SKILLSEND = 5010
    NOT_READY_PFL_ACTIVE = 5011


@dataclass
class Header:
    msg_type: MsgType
    comm_type: CommType
    reply_type: ReplyType


class FlagsValidFields(Enum):
    TIME = 1
    POSITION = 2
    VELOCITY = 4
    ACCELERATION = 6


@dataclass
class RobotStatus:
    drives_powered: int  # Servo Power: -1=Unknown, 1=ON, 0=OFF
    e_stopped: int  # Controller E-Stop state: -1=Unknown, 1=True(ON), 0=False(OFF)
    error_code: int  # Alarm code
    in_error: int  # Is there an alarm:   -1=Unknown, 1=True, 0=False
    in_motion: int  # Is currently executing a motion command:  -1=Unknown, 1=True, 0=False
    mode: int  # Controller/Pendant mode: -1=Unknown, 1=Manual(TEACH), 2=Auto(PLAY)
    motion_possible: int  # Is the controller ready to receive motion: -1=Unknown, 1=ENABLED, 0=DISABLED


@dataclass
class JointTrajPtFull:
    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Index of point in trajectory; 0 = Initial trajectory point,
    # which should match the robot current position.
    sequence: int
    # Bit-mask indicating which “optional” fields are filled with data.
    # 1=time, 2=position, 4=velocity, 8=acceleration
    valid_fields: FlagsValidFields
    # Timestamp associated with this trajectory point; Units: in seconds
    time: float
    pos: List[float]  # Desired joint positions in radian.  Base to Tool joint order
    vel: List[float]  # Desired joint velocities in radian/sec.
    acc: List[float]  # Desired joint accelerations in radian/sec^2.


@dataclass
class JointFeedback:
    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Bit-mask indicating which “optional” fields are filled with data.
    # 1=time, 2=position, 4=velocity, 8=acceleration
    valid_fields: FlagsValidFields
    # Timestamp associated with this trajectory point; Units: in seconds
    time: float
    pos: List[float]  # Feedback joint positions in radian.  Base to Tool joint order
    vel: List[float]  # Feedback joint velocities in radian/sec.
    acc: List[float]  # Feedback joint accelerations in radian/sec^2.


@dataclass
class MotoMotionCtrl:
    groupno: int  # Robot/group ID;  0 = 1st robot
    sequence: int  # Optional message tracking number that will be echoed back in the response.
    command: CommandType  # Desired command
    data: List[float]  # Command data - for future use


@dataclass
class MotoMotionReply:
    groupno: int  # Robot/group ID;  0 = 1st robot
    sequence: int  # Optional message tracking number that will be echoed back in the response.
    command: int  # Reference to the received message command or type
    result: ResultType  # High level result code
    subcode: int  # More detailed result code (optional)
    data: List[float]  # Reply data - for future use


@dataclass
class JointTrajPtExData:
    groupno: int  # Robot/group ID;  0 = 1st robot
    valid_fields: FlagsValidFields  # Bit-mask indicating which “optional” fields are filled with data. 1=time, 2=position, 4=velocity, 8=acceleration
    time: float  # Timestamp associated with this trajectory point; Units: in seconds
    pos: List[float]  # Desired joint positions in radian.  Base to Tool joint order
    vel: List[float]  # Desired joint velocities in radian/sec.
    acc: List[float]  # Desired joint accelerations in radian/sec^2.


@dataclass
class JointTrajPtFullEx:
    number_of_valid_groups: int
    sequence: int
    joint_traj_pt_data: List[JointTrajPtExData]


@dataclass
class JointFeedbackEx:
    number_of_valid_groups: int
    joint_traj_pt_data: List[JointFeedback]


@dataclass
class SelectTool:
    groupno: int
    tool: int
    sequence: int

