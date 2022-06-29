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

from typing import List, Tuple, Union, ClassVar
from dataclasses import dataclass
from enum import Enum, IntEnum, IntFlag

import struct
from struct import Struct

ROS_MAX_JOINT: int = 10
MOT_MAX_GR: int = 4


class SimpleMessageError(Exception):
    pass


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
    INVALID = -1
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

    MOTO_REALTIME_MOTION_JOINT_STATE_EX = 2030
    MOTO_REALTIME_MOTION_JOINT_COMMAND_EX = 2031


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
    # Starts the servo motors
    START_SERVOS = 200112
    # Stops the servo motors and motion
    STOP_SERVOS = 200113
    # Clears the error in the current controller
    RESET_ALARM = 200114
    START_TRAJ_MODE = 200121
    STOP_TRAJ_MODE = 200122
    DISCONNECT = 200130
    START_REALTIME_MOTION_MODE = 200140
    STOP_REALTIME_MOTION_MODE = 200141


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


class InvalidSubCode(IntEnum):
    UNSPECIFIED = 3000
    MSGSIZE = 3001
    MSGHEADER = 3002
    MSGTYPE = 3003
    GROUPNO = 3004
    SEQUENCE = 3005
    COMMAND = 3006
    DATA = 3010
    DATA_START_POS = 3011
    DATA_POSITION = 3011
    DATA_SPEED = 3012
    DATA_ACCEL = 3013
    DATA_INSUFFICIENT = 3014
    DATA_TIME = 3015
    DATA_TOOLNO = 3016


class NotReadySubcode(IntEnum):
    UNSPECIFIED = 5000
    ALARM = 5001
    ERROR = 5002
    ESTOP = 5003
    NOT_PLAY = 5004
    NOT_REMOTE = 5005
    SERVO_OFF = 5006
    HOLD = 5007
    NOT_STARTED = 5008
    WAITING_ROS = 5009
    SKILLSEND = 5010
    PFL_ACTIVE = 5011


SubCode = Union[int, InvalidSubCode, NotReadySubcode]


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
        try:
            self.msg_type = MsgType(msg_type)
            self.comm_type = CommType(comm_type)
            self.reply_type = ReplyType(reply_type)
        except ValueError as e:
            # If any of the msg, command, or reply types isn't a type described in
            # Motoplus-ROS Incremental Motion interface - Engineering Design Specifications.
            # Then we assign it to be of type Invalid
            self.msg_type = MsgType(-1)


    @classmethod
    def from_bytes(cls, bytes_: bytes):
        return cls(*cls.struct_.unpack(bytes_))

    def to_bytes(self) -> bytes:
        return self.struct_.pack(
            self.msg_type.value, self.comm_type.value, self.reply_type.value
        )


class ValidFields(IntFlag):
    """Bit-mask indicating which 'optional' fields are filled with data."""

    TIME = 1
    POSITION = 2
    VELOCITY = 4
    ACCELERATION = 8


class Ternary(Enum):
    UNKNOWN = -1
    FALSE = 0
    TRUE = 1

    def __bool__(self):
        if self is Ternary.TRUE:
            return True
        else: 
            return False


class PendantMode(Enum):
    """Controller / Pendant mode."""

    UNKNOWN = -1
    MANUAL = 1
    AUTO = 2

@dataclass
class Invalid:
    data: bytes

    def __init__(self, data) -> None:
        self.data = data

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        return cls(bytes_)


@dataclass
class RobotStatus:
    struct_: ClassVar[Struct] = Struct("7i")
    size = struct_.size

    # Servo Power: -1=Unknown, 1=ON, 0=OFF
    drives_powered: Ternary
    # Controller E-Stop state: -1=Unknown, 1=True(ON), 0=False(OFF)
    e_stopped: Ternary
    # Alarm code
    error_code: int
    # Is there an alarm: -1=Unknown, 1=True, 0=False
    in_error: Ternary
    # Is currently executing a motion command: -1=Unknown, 1=True, 0=False
    in_motion: Ternary
    # Controller/Pendant mode: -1=Unknown, 1=Manual(TEACH), 2=Auto(PLAY)
    mode: PendantMode
    # Is the controller ready to receive motion: -1=Unknown, 1=ENABLED, 0=DISABLED
    motion_possible: Ternary

    def __init__(
        self,
        drives_powered: Union[int, Ternary],
        e_stopped: Union[int, Ternary],
        error_code: int,
        in_error: Union[int, Ternary],
        in_motion: Union[int, Ternary],
        mode: Union[int, PendantMode],
        motion_possible: Union[int, Ternary],
    ) -> None:
        self.drives_powered: Ternary = Ternary(drives_powered)
        self.e_stopped: Ternary = Ternary(e_stopped)
        self.error_code: int = error_code
        self.in_error: Ternary = Ternary(in_error)
        self.in_motion: Ternary = Ternary(in_motion)
        self.mode: PendantMode = PendantMode(mode)
        self.motion_possible: Ternary = Ternary(motion_possible)

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        return cls(*cls.struct_.unpack(bytes_[: cls.size]))

    def to_bytes(self) -> bytes:
        packed = self.struct_.pack(
            self.drives_powered.value,
            self.e_stopped.value,
            self.error_code,
            self.in_error.value,
            self.in_motion.value,
            self.mode.value,
            self.motion_possible.value,
        )
        return packed


@dataclass
class JointTrajPtFull:
    struct_: ClassVar[Struct] = Struct("iiif10f10f10f")
    size: ClassVar[int] = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Index of point in trajectory; 0 = Initial trajectory point,
    # which should match the robot current position.
    sequence: int
    # Bit-mask indicating which 'optional' fields are filled with data.
    # 1=time, 2=position, 4=velocity, 8=acceleration
    valid_fields: ValidFields
    # Timestamp associated with this trajectory point; Units: in seconds
    time: float
    # Desired joint positions in radian.  Base to Tool joint order
    pos: List[float]
    # Desired joint velocities in radian/sec.
    vel: List[float]
    # Desired joint accelerations in radian/sec^2.
    acc: List[float]

    def __init__(
        self,
        groupno: int,
        sequence: int,
        valid_fields: Union[int, ValidFields],
        time: float,
        pos: List[float],
        vel: List[float],
        acc: List[float],
    ) -> None:
        self.groupno: int = groupno
        self.sequence: int = sequence
        self.valid_fields: ValidFields = ValidFields(valid_fields)
        self.time: float = time
        self.pos: List[float] = pos
        self.vel: List[float] = vel
        self.acc: List[float] = acc

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked: Tuple = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        sequence = unpacked[1]
        valid_fields = unpacked[2]
        time = unpacked[3]
        pos = unpacked[4:14]
        vel = unpacked[14:24]
        acc = unpacked[24:34]
        return cls(groupno, sequence, valid_fields, time, pos, vel, acc)

    def to_bytes(self) -> bytes:
        packed: bytes = self.struct_.pack(
            self.groupno,
            self.sequence,
            self.valid_fields.value,
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
    valid_fields: ValidFields
    # Timestamp associated with this trajectory point; Units: in seconds
    time: float
    # Feedback joint positions in radian. Base to Tool joint order
    pos: List[float]
    # Feedback joint velocities in radian/sec.
    vel: List[float]
    # Feedback joint accelerations in radian/sec^2.
    acc: List[float]

    def __init__(
        self,
        groupno: int,
        valid_fields: Union[int, ValidFields],
        time: float,
        pos: List[float],
        vel: List[float],
        acc: List[float],
    ):
        self.groupno: int = groupno
        self.valid_fields: ValidFields = ValidFields(valid_fields)
        self.time: float = time
        self.pos: List[float] = pos
        self.vel: List[float] = vel
        self.acc: List[float] = acc

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        valid_fields = unpacked[1]
        time = unpacked[2]
        pos = unpacked[3:13]
        vel = unpacked[13:23]
        acc = unpacked[23:33]
        return cls(groupno, valid_fields, time, pos, vel, acc)

    def to_bytes(self) -> bytes:
        packed = self.struct_.pack(
            self.groupno, self.valid_fields, self.time, *self.pos, *self.vel, *self.acc
        )
        return packed


@dataclass
class MotoMotionCtrl:
    struct_: ClassVar[Struct] = Struct("3i10f")
    size: ClassVar[int] = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Optional message tracking number that will be echoed back in the response.
    sequence: int
    # Desired command
    command: CommandType
    # Command data - for future use
    data: List[float]

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
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_)
        groupno = unpacked[0]
        sequence = unpacked[1]
        command = CommandType(unpacked[2])
        data = unpacked[3:13]
        return cls(groupno, sequence, command, data)

    def to_bytes(self) -> bytes:
        packed = self.struct_.pack(
            self.groupno, self.sequence, self.command.value, *self.data
        )
        return packed


@dataclass
class MotoMotionReply:
    struct_: ClassVar[Struct] = Struct("5i10f")
    size = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Optional message tracking number that will be echoed back in the response.
    sequence: int
    # Reference to the received message command or type
    command: CommandType
    # High level result code
    result: ResultType
    # More detailed result code (optional)
    subcode: SubCode
    # Reply data - for future use
    data: List[float]

    def __init__(
        self,
        groupno: int,
        sequence: int,
        command: Union[int, CommandType, MsgType],
        result: Union[int, ResultType],
        subcode: SubCode,
        data: List[float] = [0.0] * ROS_MAX_JOINT,
    ):
        self.groupno: int = groupno
        self.sequence: int = sequence
        try:
            self.command: CommandType = CommandType(command)
        except Exception:
            try:
                self.command: MsgType = MsgType(command)
            except Exception:
                self.command: int = command
        try:
            self.result: ResultType = ResultType(result)
        except Exception:
            self.result = result
        try:
            self.subcode: InvalidSubCode = InvalidSubCode(subcode)
        except Exception:
            try:
                self.subcode: NotReadySubcode = NotReadySubcode(subcode)
            except Exception:
                self.subcode = subcode
        self.data: List[float] = data

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        sequence = unpacked[1]
        command = unpacked[2]
        result = unpacked[3]
        subcode = unpacked[4]
        data = unpacked[5:15]
        return cls(groupno, sequence, command, result, subcode, data)

    def to_bytes(self) -> bytes:
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
    struct_: ClassVar[Struct] = Struct("iif10f10f10f")
    size: ClassVar[int] = struct_.size

    groupno: int  # Robot/group ID;  0 = 1st robot
    valid_fields: ValidFields
    time: float  # Timestamp associated with this trajectory point; Units: in seconds
    # Desired joint positions in radian. Base to Tool joint order
    pos: List[float]
    vel: List[float]  # Desired joint velocities in radian/sec.
    acc: List[float]  # Desired joint accelerations in radian/sec^2.

    def __init__(
        self,
        groupno: int,
        valid_fields: Union[int, ValidFields],
        time: float,
        pos: List[float],
        vel: List[float],
        acc: List[float],
    ) -> None:
        self.groupno: int = groupno
        self.valid_fields: ValidFields = ValidFields(valid_fields)
        self.time: float = time
        self.pos: List[float] = pos
        self.vel: List[float] = vel
        self.acc: List[float] = acc

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        valid_fields = unpacked[1]
        time = unpacked[2]
        pos = unpacked[3:13]
        vel = unpacked[13:23]
        acc = unpacked[23:33]
        return cls(groupno, valid_fields, time, pos, vel, acc)

    def to_bytes(self) -> bytes:
        packed = self.struct_.pack(
            self.groupno,
            self.valid_fields.value,
            self.time,
            *self.pos,
            *self.vel,
            *self.acc,
        )
        return packed


@dataclass
class JointTrajPtFullEx:
    number_of_valid_groups: int
    sequence: int
    joint_traj_pt_data: List[JointTrajPtExData]

    @property
    def size(self):
        return 8 + JointTrajPtExData.size * self.number_of_valid_groups

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        number_of_valid_groups, sequence = struct.unpack("ii", bytes_[:8])
        bytes_ = bytes_[8:]
        joint_traj_pt_data = []
        for _ in range(number_of_valid_groups):
            joint_traj_pt_data.append(
                JointTrajPtExData.from_bytes(bytes_[: JointTrajPtExData.size])
            )
            bytes_ = bytes_[JointTrajPtExData.size :]
        return cls(number_of_valid_groups, sequence, joint_traj_pt_data)

    def to_bytes(self) -> bytes:
        packed: bytes = struct.pack("ii", self.number_of_valid_groups, self.sequence)
        for pt in self.joint_traj_pt_data:
            packed += pt.to_bytes()
        return packed


@dataclass
class JointFeedbackEx:
    number_of_valid_groups: int
    joint_feedback_data: List[JointFeedback]

    @property
    def size(self):
        return 4 + JointFeedback.size * self.number_of_valid_groups

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        number_of_valid_groups = struct.unpack("i", bytes_[:4])[0]
        bytes_ = bytes_[4:]
        joint_traj_pt_data = []
        for _ in range(number_of_valid_groups):
            joint_traj_pt_data.append(
                JointFeedback.from_bytes(bytes_[: JointFeedback.size])
            )
            bytes_ = bytes_[JointFeedback.size :]

        return cls(number_of_valid_groups, joint_traj_pt_data)

    def to_bytes(self) -> bytes:
        packed: bytes = struct.pack("i", self.number_of_valid_groups)
        for pt in self.joint_feedback_data:
            packed += pt.to_bytes()
        return packed


@dataclass
class SelectTool:
    struct_: ClassVar[Struct] = Struct("iii")
    size = struct_.size

    groupno: int
    tool: int
    sequence: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        return cls(*cls.struct_.unpack(bytes_[:, cls.size]))

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.groupno, self.tool, self.sequence)


class IoResultCodes(IntEnum):
    OK = 0
    # The ioAddress cannot be read on this controller
    READ_ADDRESS_INVALID = 1001
    # The ioAddress cannot be written to on this controller
    WRITE_ADDRESS_INVALID = 1002
    # The value supplied is not a valid value for the addressed IO element
    WRITE_VALUE_INVALID = 1003
    # mpReadIO return -1
    READ_API_ERROR = 1004
    # mpWriteIO returned -1
    WRITE_API_ERROR = 1005


@dataclass
class MotoReadIO:
    struct_: ClassVar[Struct] = Struct("I")
    size = struct_.size
    address: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        address = unpacked[0]
        return cls(address)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.address)


@dataclass
class MotoReadIOReply:
    struct_: ClassVar[Struct] = Struct("II")
    size = struct_.size
    value: int
    result_code: IoResultCodes

    def __init__(self, value: int, result_code: Union[int, IoResultCodes]):
        self.value = value
        try:
            self.result_code: IoResultCodes = IoResultCodes(result_code)
        except Exception:
            self.result_code: int = result_code

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        value = unpacked[0]
        result_code = unpacked[1]
        return cls(value, result_code)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.value, self.result_code)


@dataclass
class MotoWriteIO:
    struct_: ClassVar[Struct] = Struct("II")
    size = struct_.size
    address: int
    value: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        address = unpacked[0]
        value = unpacked[1]
        return cls(address, value)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.address, self.value)


@dataclass
class MotoWriteIOReply:
    struct_: ClassVar[Struct] = Struct("I")
    size = struct_.size
    result_code: int

    def __init__(self, result_code: Union[int, IoResultCodes]):
        try:
            self.result_code: IoResultCodes = IoResultCodes(result_code)
        except Exception:
            self.result_code: int = result_code

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        result_code = unpacked[0]
        return cls(result_code)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.result_code)


@dataclass
class MotoIoCtrlReply:
    struct_: ClassVar[Struct] = Struct("Ii")
    size = struct_.size

    # High level result code
    result: ResultType
    # More detailed result code (optional)
    subcode: SubCode

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        result = unpacked[0]
        subcode = unpacked[1]
        return cls(result, subcode)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.result.value, self.subcode)


@dataclass
class DhLink:
    struct_: ClassVar[Struct] = Struct("4f")
    size = struct_.size

    theta: float
    d: float
    a: float
    alpha: float

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        return cls(*cls.struct_.unpack(bytes_[: cls.size]))

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.theta, self.d, self.a, self.alpha)


@dataclass
class DhParameters:
    struct_: ClassVar[Struct] = Struct("32f")
    size = struct_.size

    link: List[DhLink]

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        link = []
        for _ in range(8):
            link.append(DhLink.from_bytes(bytes_))
            bytes_ = bytes_[DhLink.size :]
        return cls(link)

    def to_bytes(self) -> bytes:
        bytes_: bytes = b""
        for link in self.link:
            bytes_ += link.to_bytes()
        return bytes_


@dataclass
class MotoGetDhParameters:
    struct_: ClassVar[Struct] = Struct("128f")
    size = struct_.size

    dh_parameters: List[DhParameters]

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        dh_parameters = []
        for _ in range(MOT_MAX_GR):
            dh_parameters.append(DhParameters.from_bytes(bytes_))
            bytes_ = bytes_[DhParameters.size :]
        return cls(dh_parameters)

    def to_bytes(self) -> bytes:
        bytes_: bytes = b""
        for dh_parameters in self.dh_parameters:
            bytes_ += dh_parameters.to_bytes()
        return bytes_


class MotoRealTimeMotionMode(Enum):
    IDLE = 0
    JOINT_POSITION = 1
    JOINT_VELOCITY = 2


@dataclass
class MotoRealTimeMotionJointStateExData:
    struct_: ClassVar[Struct] = Struct("i10f10f")
    size: ClassVar[int] = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Feedback joint positions in radian. Base to Tool joint order
    pos: List[float]
    # Feedback joint velocities in radian/sec.
    vel: List[float]

    def __init__(self, groupno: int, pos: List[float], vel: List[float]) -> None:
        self.groupno = groupno
        num_joints = len(pos)
        assert num_joints == len(vel)
        padding = [0.0] * (ROS_MAX_JOINT - num_joints)
        self.pos = pos + padding
        self.vel = vel + padding

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        pos = list(unpacked[1:11])
        vel = list(unpacked[11:21])
        return cls(groupno, pos, vel)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.groupno, *self.pos, *self.vel)


@dataclass
class MotoRealTimeMotionJointStateEx:
    # Message id that the external controller must echo back in the command
    message_id: int
    # Control mode (idle, joint position, or joint velocity)
    mode: MotoRealTimeMotionMode
    number_of_valid_groups: int  # Max 4 groups
    joint_state_data: List[MotoRealTimeMotionJointStateExData]

    @property
    def size(self):
        return (
            12 + MotoRealTimeMotionJointStateExData.size * self.number_of_valid_groups
        )

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        message_id, mode, number_of_valid_groups = struct.unpack("3i", bytes_[:12])
        bytes_ = bytes_[12:]
        joint_state_data = []
        for _ in range(number_of_valid_groups):
            joint_state_data.append(
                MotoRealTimeMotionJointStateExData.from_bytes(
                    bytes_[: MotoRealTimeMotionJointStateExData.size]
                )
            )
            bytes_ = bytes_[MotoRealTimeMotionJointStateExData.size :]

        return cls(
            message_id,
            MotoRealTimeMotionMode(mode),
            number_of_valid_groups,
            joint_state_data,
        )

    def to_bytes(self) -> bytes:
        packed: bytes = struct.pack(
            "3i", self.message_id, self.mode.value, self.number_of_valid_groups
        )
        for group_joint_state_data in self.joint_state_data:
            packed += group_joint_state_data.to_bytes()
        return packed


@dataclass
class MotoRealTimeMotionJointCommandExData:
    struct_: ClassVar[Struct] = Struct("i10f")
    size: ClassVar[int] = struct_.size

    # Robot/group ID;  0 = 1st robot
    groupno: int
    # Commanded joint positions or velocities. Depends on control mode.
    command: List[float]

    def __init__(self, groupno: int, command: List[float]) -> None:
        self.groupno = groupno
        padding = [0.0] * (ROS_MAX_JOINT - len(command))
        self.command = list(command) + padding

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        unpacked = cls.struct_.unpack(bytes_[: cls.size])
        groupno = unpacked[0]
        command = unpacked[1:]
        return cls(groupno, command)

    def to_bytes(self) -> bytes:
        return self.struct_.pack(self.groupno, *self.command)


@dataclass
class MotoRealTimeMotionJointCommandEx:
    # Message id from the state message that the external controller must echo back in the command
    message_id: int
    number_of_valid_groups: int
    joint_command_data: List[MotoRealTimeMotionJointCommandExData]

    @property
    def size(self):
        return (
            8 + MotoRealTimeMotionJointCommandExData.size * self.number_of_valid_groups
        )

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        message_id, number_of_valid_groups = struct.unpack("2i", bytes_[:8])
        bytes_ = bytes_[8:]
        joint_command_data = []
        for _ in range(number_of_valid_groups):
            joint_command_data.append(
                MotoRealTimeMotionJointCommandExData.from_bytes(
                    bytes_[: MotoRealTimeMotionJointCommandExData.size]
                )
            )
            bytes_ = bytes_[MotoRealTimeMotionJointCommandExData.size :]

        return cls(message_id, number_of_valid_groups, joint_command_data,)

    def to_bytes(self) -> bytes:
        packed: bytes = struct.pack("2i", self.message_id, self.number_of_valid_groups)
        for group_joint_command_data in self.joint_command_data:
            packed += group_joint_command_data.to_bytes()
        return packed


SimpleMessageBody = Union[
    RobotStatus,
    JointTrajPtFull,
    JointFeedback,
    MotoMotionCtrl,
    MotoMotionReply,
    JointTrajPtFullEx,
    JointFeedbackEx,
    SelectTool,
    MotoReadIO,
    MotoReadIOReply,
    MotoWriteIO,
    MotoWriteIOReply,
    MotoIoCtrlReply,
    MotoGetDhParameters,
    MotoRealTimeMotionJointStateEx,
    MotoRealTimeMotionJointCommandEx,
]


MSG_TYPE_CLS = {
    MsgType.INVALID: Invalid,
    MsgType.ROBOT_STATUS: RobotStatus,
    MsgType.JOINT_TRAJ_PT_FULL: JointTrajPtFull,
    MsgType.MOTO_JOINT_TRAJ_PT_FULL_EX: JointTrajPtFullEx,
    MsgType.JOINT_FEEDBACK: JointFeedback,
    MsgType.MOTO_MOTION_CTRL: MotoMotionCtrl,
    MsgType.MOTO_MOTION_REPLY: MotoMotionReply,
    MsgType.MOTO_JOINT_FEEDBACK_EX: JointFeedbackEx,
    MsgType.MOTO_READ_IO_BIT: MotoReadIO,
    MsgType.MOTO_READ_IO_BIT_REPLY: MotoReadIOReply,
    MsgType.MOTO_WRITE_IO_BIT: MotoWriteIO,
    MsgType.MOTO_WRITE_IO_BIT_REPLY: MotoWriteIOReply,
    MsgType.MOTO_READ_IO_GROUP: MotoReadIO,
    MsgType.MOTO_READ_IO_GROUP_REPLY: MotoReadIOReply,
    MsgType.MOTO_WRITE_IO_GROUP: MotoWriteIO,
    MsgType.MOTO_WRITE_IO_GROUP_REPLY: MotoWriteIOReply,
    MsgType.MOTO_IOCTRL_REPLY: MotoIoCtrlReply,
    MsgType.MOTO_SELECT_TOOL: SelectTool,
    MsgType.MOTO_GET_DH_PARAMETERS: MotoGetDhParameters,
    MsgType.MOTO_REALTIME_MOTION_JOINT_STATE_EX: MotoRealTimeMotionJointStateEx,
    MsgType.MOTO_REALTIME_MOTION_JOINT_COMMAND_EX: MotoRealTimeMotionJointCommandEx,
}


@dataclass
class SimpleMessage:
    header: Header
    body: SimpleMessageBody

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        header = Header.from_bytes(bytes_[4:16])
        if header.msg_type is Invalid:
            body = MSG_TYPE_CLS[header.msg_type].from_bytes(bytes_)
        else:
            body = MSG_TYPE_CLS[header.msg_type].from_bytes(bytes_[16:])
        return SimpleMessage(header, body)

    def to_bytes(self) -> bytes:
        if self.body is not None:
            return (
                Prefix(self.header.size + self.body.size).to_bytes()
                + self.header.to_bytes()
                + self.body.to_bytes()
            )
        else:
            return Prefix(self.header.size).to_bytes() + self.header.to_bytes()

