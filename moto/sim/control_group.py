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

from typing import List, Tuple

from copy import copy
from threading import Lock



class ControlGroup:
    def __init__(
        self, groupno: int, num_joints: int, initial_joint_positions: List[float]
    ) -> None:
        assert num_joints == len(initial_joint_positions)

        self._groupno: int = groupno
        self._num_joints: int = num_joints
        self._positions: List[float] = initial_joint_positions
        self._velocities: List[float] = [0.0] * self.num_joints

        self._lock: Lock = Lock()

    @property
    def groupno(self) -> int:
        return self._groupno

    @property
    def num_joints(self) -> int:
        return self._num_joints

    @property
    def state(self) -> Tuple[List[float], List[float]]:
        with self._lock:
            positions = copy(self._positions)
            velocities = copy(self._velocities)
            return positions, velocities

    @state.setter
    def state(self, state_: Tuple[List[float], List[float]]):
        positions, velocities = state_
        assert self._num_joints == len(positions)
        assert self._num_joints == len(velocities)
        with self._lock:
            self._positions = copy(positions)
            self._velocities = copy(velocities)
