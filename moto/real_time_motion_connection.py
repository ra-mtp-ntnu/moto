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

from moto.simple_message_connection import SimpleMessageConnection
from moto.simple_message import (
    Header,
    MsgType,
    CommType,
    ReplyType,
    MotoMotionCtrl,
    CommandType,
    SimpleMessage,
)


class RealTimeMotionConnection(SimpleMessageConnection):

    TCP_PORT_REALTIME_MOTION = 50243

    def __init__(self, ip_address):
        super().__init__((ip_address, self.TCP_PORT_REALTIME_MOTION))

    def _send_and_recv_request(
        self, command: CommandType, groupno=-1
    ) -> SimpleMessage:
        request = SimpleMessage(
            Header(
                MsgType.MOTO_MOTION_CTRL, CommType.SERVICE_REQUEST, ReplyType.INVALID
            ),
            MotoMotionCtrl(groupno, -1, command),
        )
        response = self.send_and_recv(request)
        return response

    def start_rt_mode(self):
        return self._send_and_recv_request(CommandType.START_REALTIME_MOTION_MODE)

    def stop_rt_mode(self):
        return self._send_and_recv_request(CommandType.STOP_REALTIME_MOTION_MODE)


