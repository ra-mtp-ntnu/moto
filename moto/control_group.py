# Copyright 2021 Norwegian University of Science and Technology.
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

from typing import List
from dataclasses import dataclass

from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection


@dataclass
class ControlGroupDefinition:
    groupid: str
    groupno: int
    num_joints: int
    joint_names: List[str]

    def __init__(self, groupid: str, groupno: int, num_joints: int, joint_names: List[str]):
        self.groupid: str = groupid
        self.groupno: str = groupno
        self.num_joints: int = num_joints
        self.joint_names: List[str] = joint_names
        assert self.num_joints == len(self.joint_names)


class ControlGroup:
    def __init__(
        self,
        control_group_def: ControlGroupDefinition,
        motion_connection: MotionConnection,
        state_connection: StateConnection,
    ):
        self._control_group_def = control_group_def
        self._motion_connection: MotionConnection = motion_connection
        self._state_connection: StateConnection = state_connection

    @property
    def groupid(self) -> str:
        return self._control_group_def.groupid

    @property
    def groupno(self) -> int:
        return self._control_group_def.groupno

    @property
    def num_joints(self) -> int:
        return self._control_group_def.num_joints

    @property
    def joint_names(self) -> List[str]:
        return self._control_group_def.joint_names

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
        return self._state_connection.joint_feedback(self.groupno)

    def check_queue_count(self) -> int:
        return self._motion_connection.check_queue_count(self.groupno)