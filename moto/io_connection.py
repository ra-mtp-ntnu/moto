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

from moto.simple_message import (
    Header,
    MsgType,
    CommType,
    ReplyType,
    MSG_TYPE_CLS,
    SimpleMessage,
)
from moto.simple_message_connection import SimpleMessageConnection


class IoConnection(SimpleMessageConnection):

    TCP_PORT_IO = 50242

    def __init__(self, ip_address):
        super().__init__((ip_address, self.TCP_PORT_IO))

    def _send_and_recv_request(self, msg_type: MsgType, *args: int) -> SimpleMessage:
        request: SimpleMessage = SimpleMessage(
            Header(msg_type, CommType.SERVICE_REQUEST, ReplyType.INVALID),
            MSG_TYPE_CLS[msg_type](*args),
        )
        response: SimpleMessage = self.send_and_recv(request)
        return response

    def start(self):
        self._tcp_client.connect()

    def read_io_bit(self, address: int):
        return self._send_and_recv_request(MsgType.MOTO_READ_IO_BIT, address)

    def write_io_bit(self, address: int, value: int):
        return self._send_and_recv_request(MsgType.MOTO_WRITE_IO_BIT, address, value)

    def read_io_group(self, address: int):
        return self._send_and_recv_request(MsgType.MOTO_READ_IO_GROUP, address)

    def write_io_group(self, address: int, value: int):
        return self._send_and_recv_request(MsgType.MOTO_WRITE_IO_GROUP, address, value)
