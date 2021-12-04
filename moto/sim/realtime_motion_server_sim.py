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

from typing import List, NamedTuple, Tuple, Any

import logging
import socket
import time
from threading import Thread, Lock

from moto.sim.control_group import ControlGroup

from moto.simple_message import *

Address = Tuple[str, int]

logging.basicConfig(level=logging.DEBUG)


def open_tcp_connection(address: Address) -> Tuple[socket.socket, Any]:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.bind(address)
    server.listen()
    return server.accept()


class RealTimeMotionServerSim:

    BUFSIZE = 1024
    TCP_PORT_REALTIME_MOTION = 50243
    UDP_PORT_REALTIME_MOTION = 50244

    def __init__(
        self,
        ip_address: str = "localhost",
        rt_server_ip_address: str = "localhost",
        mode: MotoRealTimeMotionMode = MotoRealTimeMotionMode.JOINT_VELOCITY,
        control_groups: List[ControlGroup] = [ControlGroup(0, 6, [0.0] * 6)],
        update_rate: int = 250,
    ) -> None:

        self._ip_address: str = ip_address
        self._conn: socket.socket = None

        self._num_control_groups = len(control_groups)
        assert self._num_control_groups <= 4, "Max 4 control groups can be used at once"
        self._control_groups: List[ControlGroup] = control_groups

        self._mode = mode

        self._lock: Lock = Lock()
        self._sig_stop: bool = False

        self._worker_thread = Thread(target=self._worker)
        self._worker_thread.daemon = True

        self._rt_server_ip_address: str = rt_server_ip_address
        self._rt_worker_thread = Thread(target=self._rt_worker)
        self._rt_worker_thread.daemon = True

        self._sig_stop_rt: bool = False

        self._update_duration: float = 1.0 / update_rate

    def start(self) -> None:
        self._worker_thread.start()

    def stop(self) -> None:
        self._sig_stop = True

    def _worker(self) -> None:
        while not self._sig_stop:
            logging.info("Waiting for connection")
            conn, addr = open_tcp_connection(
                (self._ip_address, self.TCP_PORT_REALTIME_MOTION)
            )
            logging.info("Got connection from {}".format(addr))
            self._conn = conn

            while True:

                try:
                    bytes_ = self._conn.recv(self.BUFSIZE)
                    if not bytes_:
                        break

                    req = SimpleMessage.from_bytes(bytes_)
                    if req.header.msg_type == MsgType.MOTO_MOTION_CTRL:
                        if req.body.command == CommandType.START_REALTIME_MOTION_MODE:
                            self._rt_worker_thread.start()

                        if req.body.command == CommandType.STOP_REALTIME_MOTION_MODE:
                            self._sig_stop_rt = True

                    res = SimpleMessage(
                        Header(
                            MsgType.MOTO_MOTION_REPLY,
                            CommType.SERVICE_REQUEST,
                            ReplyType.SUCCESS,
                        ),
                        MotoMotionReply(
                            -1, -1, req.body.command, ResultType.SUCCESS, 0,
                        ),
                    )

                    self._conn.send(res.to_bytes())
                except Exception:
                    pass

    def _rt_worker(self) -> None:
        logging.debug("Starting RT motion thread")

        message_id: int = 0

        rt_server_addr: Tuple[str, int] = (
            self._rt_server_ip_address,
            self.UDP_PORT_REALTIME_MOTION,
        )
        udp_client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while not self._sig_stop_rt:

            state_msg = SimpleMessage(
                Header(
                    MsgType.MOTO_REALTIME_MOTION_JOINT_STATE_EX,
                    CommType.TOPIC,
                    ReplyType.INVALID,
                ),
                MotoRealTimeMotionJointStateEx(
                    message_id,
                    self._mode,
                    self._num_control_groups,
                    [
                        MotoRealTimeMotionJointStateExData(
                            control_group.groupno, *control_group.state
                        )
                        for control_group in self._control_groups
                    ],
                ),
            )

            udp_client.sendto(state_msg.to_bytes(), rt_server_addr)
            bytes_, _ = udp_client.recvfrom(self.BUFSIZE)
            command_msg = SimpleMessage.from_bytes(bytes_)
            command: MotoRealTimeMotionJointCommandEx = command_msg.body

            assert command_msg.body.message_id == state_msg.body.message_id

            for control_group, joint_command_data in zip(
                self._control_groups, command.joint_command_data
            ):
                assert control_group.groupno == joint_command_data.groupno

                pos, vel = control_group.state

                if self._mode == MotoRealTimeMotionMode.IDLE:
                    pass

                elif self._mode == MotoRealTimeMotionMode.JOINT_POSITION:
                    pos_cmd = joint_command_data.command[: control_group.num_joints]
                    pos = pos_cmd
                    for k in range(control_group.num_joints):
                        vel[k] = (pos[k] - pos_cmd[k]) / self._update_duration

                elif self._mode == MotoRealTimeMotionMode.JOINT_VELOCITY:
                    for k in range(control_group.num_joints):
                        vel_cmd = joint_command_data.command[k]
                        pos[k] += vel_cmd * self._update_duration
                        vel[k] = vel_cmd

                control_group.state = (pos, vel)

            message_id += 1

            time.sleep(self._update_duration)

        self._sig_stop_rt = False

