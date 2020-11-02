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

from typing import List, Mapping, Tuple

from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection
from moto.io_connection import IoConnection

ControlGroupDefinition = Tuple[str, int]


class Motion:
    def __init__(self, motion_connection: MotionConnection) -> None:
        self._motion_connection: MotionConnection = motion_connection

    def check_motion_ready(self):
        return self._motion_connection.check_motion_ready()

    def stop_motion(self):
        return self._motion_connection.stop_motion()

    def start_servos(self):
        return self._motion_connection.start_servos()

    def stop_servos(self):
        return self._motion_connection.stop_servos()

    def start_trajectory_mode(self):
        return self._motion_connection.start_traj_mode()

    def stop_trajectory_mode(self):
        return self._motion_connection.stop_traj_mode()


class State:
    def __init__(self, state_connection: StateConnection) -> None:
        self._state_connection: StateConnection = state_connection

    def joint_feedback(self, groupno: int):
        return self._state_connection.joint_feedback(groupno)

    def joint_feedback_ex(self):
        return self._state_connection.joint_feedback_ex()

    def add_joint_feedback_msg_callback(self, callback):
        self._state_connection.add_joint_feedback_msg_callback(callback)

    def add_joint_feedback_ex_msg_callback(self, callback):
        self._state_connection.add_joint_feedback_ex_msg_callback(callback)


class IO:
    def __init__(self, io_connection: IoConnection) -> None:
        self._io_connection: IoConnection = io_connection

    def read_bit(self, address: int):
        return self._io_connection.read_io_bit(address)

    def write_bit(self, address: int, value: int):
        return self._io_connection.write_io_bit(address, value)

    def read_group(self, address: int):
        return self._io_connection.read_io_group(address)

    def write_group(self, address: int, value: int):
        return self._io_connection.write_io_group(address, value)


class ControlGroup:
    def __init__(
        self,
        groupid: str,
        groupno: int,
        num_joints: int,
        motion_connection: MotionConnection,
        state_connection: StateConnection,
    ):
        self._groupid: str = groupid
        self._groupno: int = groupno
        self._num_joints = num_joints
        self._motion_connection: MotionConnection = motion_connection
        self._state_connection: StateConnection = state_connection

    @property
    def groupid(self) -> str:
        return self._groupid

    @property
    def groupno(self) -> int:
        return self._groupno

    @property
    def num_joints(self) -> int:
        return self._num_joints

    @property
    def position(self):
        return self.joint_feedback.pos[: self.num_joints]

    @property
    def velocity(self):
        return self.joint_feedback.vel[: self.num_joints]

    @property
    def acceleration(self):
        return self.joint_feedback.acc[: self.num_joints]

    @property
    def joint_feedback(self):
        return self._state_connection.joint_feedback(self._groupno)

    @property
    def queue_count(self) -> int:
        return self._motion_connection.check_queue_count(self.groupno)

    def send_trajectory(self, trajectory):
        pass


class Moto:
    def __init__(self, robot_ip: str, control_group_defs: List[ControlGroupDefinition]):
        self._robot_ip: str = robot_ip
        self._control_group_defs: List[ControlGroupDefinition] = control_group_defs

        self._motion_connection: MotionConnection = MotionConnection(self._robot_ip)
        self._state_connection: StateConnection = StateConnection(self._robot_ip)
        self._io_connection: IoConnection = IoConnection(self._robot_ip)

        self._control_groups: Mapping[str, ControlGroup] = {}
        for groupno, control_group_def in enumerate(self._control_group_defs):
            groupid, num_joints = control_group_def
            self._control_groups[groupid] = ControlGroup(
                groupid,
                groupno,
                num_joints,
                self._motion_connection,
                self._state_connection,
            )

        self._motion_connection.start()
        self._state_connection.start()
        self._io_connection.start()

    @property
    def control_groups(self):
        return self._control_groups

    @property
    def motion(self):
        return Motion(self._motion_connection)

    @property
    def state(self):
        return State(self._state_connection)

    @property
    def io(self):
        return IO(self._io_connection)
