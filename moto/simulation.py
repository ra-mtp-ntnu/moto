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

import socket
import threading
import time
import numpy as np

from moto.simple_message import (
    JointFeedback,
    JointTrajPtFull,
    Prefix,
    Header,
    MsgType,
    CommType,
    ReplyType,
    ResultType,
    SimpleMessage,
    MotoMotionCtrl,
    MotoMotionReply,
)


class MotoSimulation:

    TCP_PORT_MOTION: int = 50240
    TCP_PORT_STATE: int = 50241
    TCP_PORT_IO: int = 50242

    MAX_IO_CONNECTIONS: int = 1
    MAX_MOTION_CONNECTIONS: int = 1
    MAX_STATE_CONNECTIONS: int = 4

    def __init__(self, ip_address: str = "localhost"):
        self._ip_address: str = ip_address

        self._motion_connection = None
        self._state_connection = None
        self._io_connection = None

        self._motion_server_thread = threading.Thread(target=self._run_motion_server)
        self._motion_server_thread.daemon = True

        self._state_server_thread = threading.Thread(target=self._run_state_server)
        self._state_server_thread.daemon = True

        self._io_server_thread = threading.Thread(target=self._run_io_server)
        self._io_server_thread.daemon = True

        self._groupno: int = 0
        self._valid_fields = int("1111", 2)
        self._time = 0.0
        self._rate = 25.0
        # Hz
        self._pos = np.zeros(10)
        self._vel = np.zeros(10)
        self._acc = np.zeros(10)
        self._state_lock = threading.Lock()

        self._stop = False

    def start(self):
        self._motion_server_thread.start()
        self._state_server_thread.start()

    def stop(self):
        self._stop = True

    def _open_tcp_connection(self, address):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.bind(address)
        server.listen()
        return server.accept()

    def _run_motion_server(self):
        print("Waiting for motion connection")
        conn, addr = self._open_tcp_connection((self._ip_address, self.TCP_PORT_MOTION))
        print("Got connection from {}".format(addr))
        self._motion_connection = conn
        while not self._stop:
            data = self._motion_connection.recv(1024)
            prefix = Prefix.from_bytes(data[:4])
            header = Header.from_bytes(data[4:16])
            if header.msg_type == MsgType.MOTO_MOTION_CTRL:
                request = MotoMotionCtrl.from_bytes(data[16 : 16 + MotoMotionCtrl.size])
                prefix = Prefix(Header.size + MotoMotionReply.size)
                header = Header(
                    MsgType.MOTO_MOTION_REPLY, CommType.SERVICE_REPLY, ReplyType.SUCCESS
                )
                body = MotoMotionReply(-1, -1, request.command, ResultType.SUCCESS, 0)
                msg = SimpleMessage(prefix, header, body)
                self._motion_connection.send(msg.to_bytes())

        print("stopping motion connection")

    def _run_state_server(self):
        print("Waiting for state connection")
        conn, addr = self._open_tcp_connection((self._ip_address, self.TCP_PORT_STATE))
        print("Got connection from {}".format(addr))
        self._state_connection = conn
        while not self._stop:
            with self._state_lock:
                prefix = Prefix(Header.size + JointFeedback.size)
                header = Header(
                    MsgType.JOINT_FEEDBACK, CommType.TOPIC, ReplyType.INVALID
                )
                body = JointFeedback(
                    self._groupno,
                    self._valid_fields,
                    self._time,
                    self._pos,
                    self._vel,
                    self._acc,
                )
                msg = SimpleMessage(prefix, header, body)
                self._state_connection.sendall(msg.to_bytes())
                time.sleep(1.0 / self._rate)

        print("stopping state server")

    def _run_io_server(self):
        pass

    def _connection_server_run(self):
        while True:
            pass