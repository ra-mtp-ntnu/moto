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
from moto.control_group import ControlGroup

ControlGroupDefinition = Tuple[str, int]


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
                self._io_connection,
            )

        self._motion_connection.start()
        self._state_connection.start()
        self._io_connection.start()

    def control_group(self, groupid: str) -> ControlGroup:
        return self._control_groups[groupid]

    @property
    def motion(self):
        return self._motion_connection

    @property
    def state(self):
        return self._state_connection

    @property
    def io(self):
        return self._io_connection

    def check_motion_ready(self):
        return self._motion_connection.check_motion_ready()

    def check_queue_count(self, groupno: int):
        return self._motion_connection.check_queue_count(groupno)

    def stop_motion(self):
        return self._motion_connection.stop_motion()

    def start_servos(self):
        return self._motion_connection.start_servos()

    def stop_servos(self):
        return self._motion_connection.stop_servos()

    def reset_alarm(self):
        return self._motion_connection.reset_alarm()

    def start_traj_mode(self):
        return self._motion_connection.start_traj_mode()

    def stop_traj_mode(self):
        return self._motion_connection.stop_traj_mode()

    def add_joint_feedback_callback(self, callback):
        self._state_connection.add_joint_feedback_callback(callback)

    def add_joint_feedback_ex_callback(self, callback):
        self._state_connection.add_joint_feedback_ex_callback(callback)
