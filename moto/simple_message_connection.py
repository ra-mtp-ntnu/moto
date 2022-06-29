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

from typing import Tuple
import socket

from moto.simple_message import SimpleMessage


Address = Tuple[str, int]


class TcpClient:
    def __init__(self, address: Address):
        self._address: Address = address
        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def connect(self) -> None:
        try:
            self._socket.connect(self._address)
        # TODO: Write a custom exception? RobotConnectionException? 
        except ConnectionRefusedError as e: 
            # This can happen if:
            # 1. If the alarms are not reset. Then the controller refuses connection.
            # 2. If the user has multiple network interfaces and the one connecting
            #    to the robot is not configured to the same subnet as the robot.
            error = ( 
                f'{e.strerror}. Did you remember to reset the alarms? '
                'And is your computer on the correct subnet?'
            )
            e.strerror = error
            raise
        except OSError as e: 
            # This can happen if: 
            # 1. The network interface is not set to the same subnet as the robot.
            if e.errno == 113:
                error = f'{e.strerror}. Is the robot IP correct?'
            elif e.errno == 101:
                error = f'{e.strerror}. Is your computer on the correct subnet?'
            e.strerror = error
            raise


    def send(self, data: bytes) -> None:
        self._socket.sendall(data)

    def recv(self, bufsize: int = 1024) -> bytes:
        return self._socket.recv(bufsize)


class SimpleMessageConnection:
    def __init__(self, addr: Address) -> None:
        self._tcp_client = TcpClient(addr)

    def start(self) -> None:
        self._tcp_client.connect()

    def send(self, msg: SimpleMessage) -> None:
        self._tcp_client.send(msg.to_bytes())

    def recv(self) -> SimpleMessage:
        return SimpleMessage.from_bytes(self._tcp_client.recv())

    def send_and_recv(self, msg: SimpleMessage) -> SimpleMessage:
        self.send(msg)
        return self.recv()
