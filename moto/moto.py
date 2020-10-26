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

from typing import List

from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection
from moto.io_connection import IoConnection
from moto.control_group import ControlGroup


class Moto:
    def __init__(self, robot_ip: str, control_group_ids: List[str] = ["R1"]):
        self._robot_ip: str = robot_ip
        self._control_group_ids: List[str] = control_group_ids

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

    def control_group(self, groupno: int) -> ControlGroup:
        return self._control_groups[groupno]

    def check_motion_ready(self):
        return self._motion_connection.check_motion_ready()

    def check_queue_count(self):
        return self._motion_connection.check_queue_count()

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
