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

from typing import List, Tuple, Any, Mapping

import socket
from threading import Thread, Lock
import time
import copy

Vector = List[float]
Address = Tuple[str, int]

from moto.simple_message import (
    JointFeedback,
    JointTrajPtFull,
    Header,
    MsgType,
    CommType,
    ReplyType,
    ResultType,
    SimpleMessage,
    MotoMotionCtrl,
    MotoMotionReply,
)

from moto.sim.motion_controller_simulator import (
    MotionControllerSimulator,
    JointTrajectoryPoint,
)


def open_tcp_connection(address: Address) -> Tuple[socket.socket, Any]:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.bind(address)
    server.listen()
    return server.accept()


class ControlGroupSim:
    def __init__(
        self, groupno, num_joints, initial_joint_state, update_rate=100.0
    ) -> None:
        self._groupno = groupno
        self._num_joints = num_joints
        self._initial_joint_state = initial_joint_state
        self._update_rate = update_rate
        self._motion_controller_simulator = MotionControllerSimulator(
            self._num_joints, self._initial_joint_state, self._update_rate
        )

    @property
    def groupno(self):
        return self._groupno

    @property
    def num_joints(self):
        return self._num_joints

    def add_motion_waypoint(self, waypoint: JointTrajectoryPoint):
        self._motion_controller_simulator.add_motion_waypoint(waypoint)

    @property
    def position(self):
        return self._motion_controller_simulator.get_joint_positions()


class MotionServer:

    MAX_MOTION_CONNECTIONS: int = 1
    TCP_PORT_MOTION: int = 50240

    def __init__(self, ip_address: str, control_groups: List[ControlGroupSim]):
        self._ip_address: str = ip_address
        self._conn = None

        self._control_groups: Mapping[str, ControlGroupSim] = {}
        for control_group in control_groups:
            self._control_groups[control_group.groupno] = control_group

        self._lock: Lock = Lock()
        self._sig_stop: bool = False

        self._worker_thread = Thread(target=self._worker)
        self._worker_thread.daemon = True

    def start(self) -> None:
        self._worker_thread.start()

    def stop(self) -> None:
        self._sig_stop = True

    def _worker(self) -> None:
        print("[motion_server]: Waiting for connection")
        conn, addr = open_tcp_connection((self._ip_address, self.TCP_PORT_MOTION))
        print("[motion_server]: Got connection from {}".format(addr))
        self._conn = conn
        while not self._sig_stop:
            msg = SimpleMessage.from_bytes(self._conn.recv(1024))
            if msg.header.msg_type == MsgType.MOTO_MOTION_CTRL:
                reply = SimpleMessage(
                    Header(
                        MsgType.MOTO_MOTION_REPLY,
                        CommType.SERVICE_REPLY,
                        ReplyType.SUCCESS,
                    ),
                    MotoMotionReply(
                        -1,
                        -1,
                        msg.header.msg_type,
                        ResultType.SUCCESS,
                        msg.body.command.value,
                    ),
                )
                self._conn.send(reply.to_bytes())

            elif msg.header.msg_type == MsgType.JOINT_TRAJ_PT_FULL:
                groupno = msg.body.groupno
                pt = JointTrajectoryPoint()
                pt.time_from_start = copy.deepcopy(msg.body.time)
                pt.positions = copy.deepcopy(
                    msg.body.pos[: self._control_groups[groupno].num_joints]
                )
                self._control_groups[msg.body.groupno].add_motion_waypoint(pt)


class StateServer:

    MAX_STATE_CONNECTIONS: int = 4
    TCP_PORT_STATE: int = 50241

    def __init__(
        self, ip_address: str, control_groups: List[ControlGroupSim], rate: float = 25
    ):
        self._ip_address: str = ip_address
        self._conn = None

        self._control_groups = control_groups
        self._rate = rate

        self._position = [0.0] * 10

        self._lock: Lock = Lock()
        self._sig_stop: bool = False

        self._worker_thread = Thread(target=self._worker)
        self._worker_thread.daemon = True

    def start(self) -> None:
        self._worker_thread.start()

    def stop(self) -> None:
        self._sig_stop = True

    def _worker(self) -> None:
        print("[state_server]: Waiting for connection")
        conn, addr = open_tcp_connection((self._ip_address, self.TCP_PORT_STATE))
        print("[state_server]: Got connection from {}".format(addr))
        self._conn = conn
        while not self._sig_stop:
            for control_group in self._control_groups:
                msg = SimpleMessage(
                    Header(MsgType.JOINT_FEEDBACK, CommType.TOPIC, ReplyType.INVALID),
                    JointFeedback(
                        control_group.groupno,
                        int("0011", 2),
                        0.0,
                        list(control_group.position)
                        + [0.0] * (10 - control_group.num_joints),
                        [0.0] * 10,
                        [0.0] * 10,
                    ),
                )
                self._conn.sendall(msg.to_bytes())
            time.sleep(1.0 / self._rate)


class IoServer:

    MAX_IO_CONNECTIONS: int = 1
    TCP_PORT_IO: int = 50242

    def __init__(self, ip_address: str) -> None:
        self._ip_address: str = ip_address
        self._conn = None

        self._lock: Lock = Lock()
        self._sig_stop: bool = False

        self._worker_thread = Thread(target=self._worker)
        self._worker_thread.daemon = True

    def start(self) -> None:
        self._worker_thread.start()

    def stop(self) -> None:
        self._sig_stop = True

    def _worker(self) -> None:
        print("[io_server]: Waiting for connection")
        conn, addr = open_tcp_connection((self._ip_address, self.TCP_PORT_IO))
        print("[io_server]: Got connection from {}".format(addr))
        self._conn = conn
        while not self._sig_stop:
            pass


class MotoSim:
    def __init__(self, ip_address: str, control_groups: List[ControlGroupSim]):
        self._ip_address: str = ip_address
        self._control_groups: List[ControlGroupSim] = control_groups

        self._motion_server: MotionServer = MotionServer(
            self._ip_address, self._control_groups
        )

        self._state_server: StateServer = StateServer(
            self._ip_address, self._control_groups
        )

        self._io_server: IoServer = IoServer(self._ip_address)

        self._sig_stop: bool = False

    def start(self) -> None:
        self._motion_server.start()
        self._state_server.start()
        self._io_server.start()

    def stop(self) -> None:
        self._motion_server.stop()
        self._state_server.stop()
        self._io_server.stop()
