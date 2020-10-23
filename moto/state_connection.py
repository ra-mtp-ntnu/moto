from typing import List
from copy import copy
from threading import Thread, Lock

from moto.simple_message_connection import SimpleMessageConnection
from moto.tcp_client import TcpClient
from moto.simple_message import Prefix, Header, JointFeedback, MsgType, SimpleMessage
from moto.control_group import ControlGroup


class StateConnection(SimpleMessageConnection):

    TCP_PORT_STATE = 50241

    def __init__(self, ip_address: str):
        self._tcp_client: TcpClient = TcpClient((ip_address, self.TCP_PORT_STATE))

        self._joint_feedback: List[JointFeedback] = [
            None
        ] * ControlGroup.MAX_CONTROLLABLE_GROUPS
        self._lock: Lock = Lock()

        self._run_thread: Thread = Thread(target=self._run)
        self._run_thread.daemon = True

    def joint_feedback(self, groupno: int) -> JointFeedback:
        with self._lock:
            return copy(self._joint_feedback[groupno])

    def start(self) -> None:
        self._tcp_client.connect()
        self._run_thread.start()

    def stop(self) -> None:
        pass

    def _run(self) -> None:
        while True:
            msg = SimpleMessage.from_bytes(self._tcp_client.recv())
            if msg.header.msg_type == MsgType.JOINT_FEEDBACK:
                with self._lock:
                    self._joint_feedback[msg.body.groupno] = msg.body

