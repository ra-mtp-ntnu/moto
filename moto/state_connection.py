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
from copy import deepcopy
from threading import Thread, Lock

from moto.simple_message_connection import SimpleMessageConnection
from moto.simple_message import JointFeedback, MsgType, SimpleMessage
from moto.control_group import ControlGroup


class StateConnection(SimpleMessageConnection):

    TCP_PORT_STATE = 50241

    def __init__(self, ip_address: str):
        super().__init__((ip_address, self.TCP_PORT_STATE))

        self._joint_feedback: List[JointFeedback] = [
            None
        ] * ControlGroup.MAX_CONTROLLABLE_GROUPS
        self._lock: Lock = Lock()

        self._worker_thread: Thread = Thread(target=self._worker)
        self._worker_thread.daemon = True

    def joint_feedback(self, groupno: int) -> JointFeedback:
        with self._lock:
            return deepcopy(self._joint_feedback[groupno])

    def start(self) -> None:
        self._tcp_client.connect()
        self._worker_thread.start()

    def stop(self) -> None:
        pass

    def _worker(self) -> None:
        while True:
            msg: SimpleMessage = self.recv()
            if msg.header.msg_type == MsgType.JOINT_FEEDBACK:
                with self._lock:
                    self._joint_feedback[msg.body.groupno] = msg.body