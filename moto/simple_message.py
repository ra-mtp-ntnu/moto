# Copyright 2020 Norwegian University of Science and Technology.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Union, ClassVar
from dataclasses import dataclass
from enum import Enum

import struct
from struct import Struct

ROS_MAX_JOINT: int = 10
MOT_MAX_GR: int = 4


@dataclass
class Prefix:
    struct_: ClassVar[Struct] = Struct("i")
    size: ClassVar[int] = struct_.size

    length: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        return cls(*cls.struct_.unpack(bytes_))

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.length)


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
    REALTIME_MOTION_CMD = 200140


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


class SubCode(Enum):
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
    struct_: ClassVar[Struct] = Struct("3i")
    size: ClassVar[int] = struct_.size

    msg_type: MsgType
    comm_type: CommType
    reply_type: ReplyType

    def __init__(
        self,
        msg_type: Union[int, MsgType],
        comm_type: Union[int, CommType],
        reply_type: Union[int, ReplyType],
    ):
        self.msg_type = MsgType(msg_type)
        self.comm_type = CommType(comm_type)
        self.reply_type = ReplyType(reply_type)

    @classmethod
    def from_bytes(cls, bytes_):
        return cls(*cls.struct_.unpack(bytes_))

    def to_bytes(self):
        return self.struct_.pack(
            self.msg_type.value, self.comm_type.value, self.reply_type.value
        )


class FlagsValidFields(Enum):
    TIME = 1
    POSITION = 2
    VELOCITY = 4
    ACCELERATION = 8


@dataclass
class RobotStatus:
    struct_: ClassVar[Struct] = Struct("7f")
    size = struct_.size

    drives_powered: int  # Servo Power: -1=Unknown, 1=ON, 0=OFF
    # Controller E-Stop state: -1=Unknown, 1=True(ON), 0=False(OFF)
    e_stopped: int
    error_code: int  # Alarm code
    in_error: int  # Is there an alarm:   -1=Unknown, 1=True, 0=False
    in_motion: int  # Is currently executing a motion command:  -1=Unknown, 1=True, 0=False
    # Controller/Pendant mode: -1=Unknown, 1=Manual(TEACH), 2=Auto(PLAY)
    mode: int
    # Is the controller ready to receive motion: -1=Unknown, 1=ENABLED, 0=DISABLED
    motion_possible: int

    @classmethod
    def from_bytes(cls, bytes_):
        return cls(*cls.struct_.unpack(bytes_[: cls.size]))

    def to_bytes(self):
        packed = self.struct_.pack(
            self.drives_powered,
            self.e_stopped,
            self.error_code,
            self.in_error,
            self.in_motion,
            self.mode,
            self.motion_possible,
        )
        return packed


@dataclass
class JointTrajPtFull:
    struct_: ClassVar[Struct] = Struct("3i31f")
    size: ClassVar[int] = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Index of point in trajectory; 0 = Initial trajectory point,
    # which should match the robot current position.
    sequence: int
    # Bit-mask indicating which “optional” fields are filled with data.
    # 1=time, 2=position, 4=velocity, 8=acceleration
    valid_fields: int
    # Timestamp associated with this trajectory point; Units: in seconds
    time: float
    # Desired joint positions in radian.  Base to Tool joint order
    pos: List[float]
    vel: List[float]  # Desired joint velocities in radian/sec.
    acc: List[float]  # Desired joint accelerations in radian/sec^2.

    def __init__(
        self,
        groupno: int,
        sequence: int,
        valid_fields: int,
        time: float,
        pos: List[float],
        vel: List[float],
        acc: List[float],
    ):
        self.groupno: int = groupno
        self.sequence: int = sequence
        self.valid_fields: int = valid_fields
        self.time: float = time
        self.pos: List[float] = pos
        self.vel: List[float] = vel
        self.acc: List[float] = acc

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        sequence = unpacked[1]
        valid_fields = unpacked[2]
        time = unpacked[3]
        pos = unpacked[4:14]
        vel = unpacked[14:24]
        acc = unpacked[24:34]
        return cls(groupno, sequence, valid_fields, time, pos, vel, acc)

    def to_bytes(self):
        packed = self.struct_.pack(
            self.groupno,
            self.sequence,
            self.valid_fields,
            self.time,
            *self.pos,
            *self.vel,
            *self.acc,
        )
        return packed


@dataclass
class JointFeedback:
    struct_: ClassVar[Struct] = Struct("iif10f10f10f")
    size: ClassVar[int] = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Bit-mask indicating which “optional” fields are filled with data.
    # 1=time, 2=position, 4=velocity, 8=acceleration
    valid_fields: int
    # Timestamp associated with this trajectory point; Units: in seconds
    time: float
    # Feedback joint positions in radian.  Base to Tool joint order
    pos: List[float]
    vel: List[float]  # Feedback joint velocities in radian/sec.
    acc: List[float]  # Feedback joint accelerations in radian/sec^2.

    def __init__(
        self,
        groupno: int,
        valid_fields: int,
        time: float,
        pos: List[float],
        vel: List[float],
        acc: List[float],
    ):
        self.groupno: int = groupno
        self.valid_fields: int = valid_fields
        self.time: float = time
        self.pos: List[float] = pos
        self.vel: List[float] = vel
        self.acc: List[float] = acc

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        valid_fields = unpacked[1]
        time = unpacked[2]
        pos = unpacked[3 : 3 + ROS_MAX_JOINT]
        vel = unpacked[13 : 13 + ROS_MAX_JOINT]
        acc = unpacked[23 : 23 + ROS_MAX_JOINT]
        return cls(groupno, valid_fields, time, pos, vel, acc)

    def to_bytes(self):
        packed = self.struct_.pack(
            self.groupno, self.valid_fields, self.time, *self.pos, *self.vel, *self.acc
        )
        return packed


@dataclass
class MotoMotionCtrl:
    struct_: ClassVar[Struct] = Struct("3i{}f".format(ROS_MAX_JOINT))
    size: ClassVar[int] = struct_.size

    groupno: int  # Robot/group ID;  0 = 1st robot
    # Optional message tracking number that will be echoed back in the response.
    sequence: int
    command: CommandType  # Desired command
    data: List[float]  # Command data - for future use

    def __init__(
        self,
        groupno: int,
        sequence: int,
        command: CommandType,
        data: List[float] = [0.0] * ROS_MAX_JOINT,
    ):
        self.groupno: int = groupno
        self.sequence: int = sequence
        self.command: CommandType = CommandType(command)
        self.data: List[float] = data

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_)
        groupno = unpacked[0]
        sequence = unpacked[1]
        command = CommandType(unpacked[2])
        data = unpacked[3:13]
        return cls(groupno, sequence, command, data)

    def to_bytes(self):
        packed = self.struct_.pack(
            self.groupno, self.sequence, self.command.value, *self.data
        )
        return packed


@dataclass
class MotoMotionReply:
    struct_: ClassVar[Struct] = Struct("5i{}f".format(ROS_MAX_JOINT))
    size = struct_.size

    groupno: int  # Robot/group ID;  0 = 1st robot
    # Optional message tracking number that will be echoed back in the response.
    sequence: int
    command: CommandType  # Reference to the received message command or type
    result: ResultType  # High level result code
    subcode: SubCode  # More detailed result code (optional)
    data: List[float]  # Reply data - for future use

    def __init__(
        self,
        groupno: int,
        sequence: int,
        command: Union[int, CommandType],
        result: Union[int, ResultType],
        subcode: Union[int, SubCode],
        data: List[float] = [0] * ROS_MAX_JOINT,
    ):
        self.groupno: int = groupno
        self.sequence: int = sequence
        try:
            self.command: MsgType = MsgType(command)
        except:
            self.command = command
        try:
            self.result: ResultType = ResultType(result)
        except:
            self.result = result
        try:
            self.subcode: SubCode = SubCode(subcode)
        except:
            self.subcode = subcode
        self.data: List[float] = data

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        sequence = unpacked[1]
        command = unpacked[2]
        result = unpacked[3]
        subcode = unpacked[4]
        data = unpacked[5:15]
        return cls(groupno, sequence, command, result, subcode, data)

    def to_bytes(self):
        packed = self.struct_.pack(
            self.groupno,
            self.sequence,
            self.command.value,
            self.result.value,
            self.subcode,
            *self.data,
        )
        return packed


@dataclass
class JointTrajPtExData:
    groupno: int  # Robot/group ID;  0 = 1st robot
    # Bit-mask indicating which “optional” fields are filled with data. 1=time, 2=position, 4=velocity, 8=acceleration
    valid_fields: FlagsValidFields
    time: float  # Timestamp associated with this trajectory point; Units: in seconds
    # Desired joint positions in radian.  Base to Tool joint order
    pos: List[float]
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

    @classmethod
    def from_bytes(cls, bytes_):
        number_of_valid_groups = struct.unpack("i", bytes_[:4])[0]
        bytes_ = bytes_[4:]
        joint_traj_pt_data = []
        for _ in range(number_of_valid_groups):
            joint_traj_pt_data.append(
                JointFeedback.from_bytes(bytes_[: JointFeedback.size])
            )
            bytes_ = bytes_[JointFeedback.size :]

        return cls(number_of_valid_groups, joint_traj_pt_data)

    def to_bytes(self):
        packed: bytes = struct.pack("i", self.number_of_valid_groups)
        for pt in self.joint_traj_pt_data:
            packed += pt.to_bytes()
        return packed


@dataclass
class SelectTool:
    groupno: int
    tool: int
    sequence: int


@dataclass
class MotoReadIOBit:
    struct_: ClassVar[Struct] = Struct("I")
    size = struct_.size
    address: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        address = unpacked[0]
        return cls(address)

    def to_bytes(self):
        return self.struct_.pack(self.address)


@dataclass
class MotoReadIOBitReply:
    struct_: ClassVar[Struct] = Struct("II")
    size = struct_.size
    value: int
    result_code: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        value = unpacked[0]
        result_code = unpacked[1]
        return cls(value, result_code)

    def to_bytes(self):
        return self.struct_.pack(self.value, self.result_code)


@dataclass
class MotoWriteIOBit:
    struct_: ClassVar[Struct] = Struct("II")
    size = struct_.size
    address: int
    value: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        address = unpacked[0]
        value = unpacked[1]
        return cls(address, value)

    def to_bytes(self):
        return self.struct_.pack(self.address, self.value)


@dataclass
class MotoWriteIOBitReply:
    struct_: ClassVar[Struct] = Struct("I")
    size = struct_.size
    result_code: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        result_code = unpacked[0]
        return cls(result_code)

    def to_bytes(self):
        return self.struct_.pack(self.result_code)


@dataclass
class MotoReadIOGroup:
    struct_: ClassVar[Struct] = Struct("I")
    size = struct_.size
    address: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        address = unpacked[0]
        return cls(address)

    def to_bytes(self):
        return self.struct_.pack(self.address)


@dataclass
class MotoReadIOGroupReply:
    struct_: ClassVar[Struct] = Struct("II")
    size = struct_.size
    value: int
    result_code: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        value = unpacked[0]
        result_code = unpacked[1]
        return cls(value, result_code)

    def to_bytes(self):
        return self.struct_.pack(self.value, self.result_code)


@dataclass
class MotoWriteIOGroup:
    struct_: ClassVar[Struct] = Struct("II")
    size = struct_.size
    address: int
    value: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        address = unpacked[0]
        value = unpacked[1]
        return cls(address, value)

    def to_bytes(self):
        return self.struct_.pack(self.address, self.value)


@dataclass
class MotoWriteIOGroupReply:
    struct_: ClassVar[Struct] = Struct("I")
    size = struct_.size
    result_code: int

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        result_code = unpacked[0]
        return cls(result_code)

    def to_bytes(self):
        return self.struct_.pack(self.result_code)


@dataclass
class MotoIoCtrlReply:
    struct_: ClassVar[Struct] = Struct("Ii")
    size = struct_.size
    result: ResultType  # High level result code
    subcode: Union[int, SubCode]  # More detailed result code (optional)

    @classmethod
    def from_bytes(cls, bytes_):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        result = unpacked[0]
        subcode = unpacked[1]
        return cls(result, subcode)

    def to_bytes(self):
        return self.struct_.pack(self.result.value, self.subcode)


SimpleMessageBody = Union[
    RobotStatus,
    JointTrajPtFull,
    JointFeedback,
    MotoMotionCtrl,
    MotoMotionReply,
    JointFeedbackEx,
]


MSG_TYPE_CLS = {
    MsgType.ROBOT_STATUS: RobotStatus,
    MsgType.JOINT_TRAJ_PT_FULL: JointTrajPtFull,
    MsgType.JOINT_FEEDBACK: JointFeedback,
    MsgType.MOTO_MOTION_CTRL: MotoMotionCtrl,
    MsgType.MOTO_MOTION_REPLY: MotoMotionReply,
    MsgType.MOTO_JOINT_FEEDBACK_EX: JointFeedbackEx,
    MsgType.MOTO_READ_IO_BIT: MotoReadIOBit,
    MsgType.MOTO_READ_IO_BIT_REPLY: MotoReadIOBitReply,
    MsgType.MOTO_WRITE_IO_BIT: MotoWriteIOBit,
    MsgType.MOTO_WRITE_IO_BIT_REPLY: MotoWriteIOBitReply,
    MsgType.MOTO_READ_IO_GROUP: MotoReadIOGroup,
    MsgType.MOTO_READ_IO_GROUP_REPLY: MotoReadIOGroupReply,
    MsgType.MOTO_WRITE_IO_GROUP: MotoWriteIOGroup,
    MsgType.MOTO_WRITE_IO_GROUP_REPLY: MotoWriteIOGroupReply,
    MsgType.MOTO_IOCTRL_REPLY: MotoIoCtrlReply,
}


@dataclass
class SimpleMessage:
    header: Header
    body: SimpleMessageBody

    def to_bytes(self):
        return (
            Prefix(self.header.size + self.body.size).to_bytes()
            + self.header.to_bytes()
            + self.body.to_bytes()
        )

    @classmethod
    def from_bytes(cls, bytes_):
        prefix = Prefix.from_bytes(bytes_[:4])
        header = Header.from_bytes(bytes_[4:16])

        body_cls = MSG_TYPE_CLS[header.msg_type]
        body = body_cls.from_bytes(bytes_[16:])

        return SimpleMessage(header, body)
