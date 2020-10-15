from copy import copy
from threading import Thread, Lock

from moto.tcp_client import TcpClient
from moto.simple_message import Prefix, Header, JointFeedback, MsgType


class StateConnection:

    TCP_PORT_STATE = 50241

    def __init__(self, ip_address):
        self._tcp_client = TcpClient((ip_address, self.TCP_PORT_STATE))

        self._joint_feedback = None
        self._lock = Lock()

        self._run_thread = Thread(target=self._run)
        self._run_thread.daemon = True

    @property
    def joint_feedback(self):
        with self._lock:
            return copy(self._joint_feedback)

    def start(self):
        self._tcp_client.connect()
        self._run_thread.start()

    def stop(self):
        pass

    def _run(self):
        while True:
            data = self._tcp_client.recv()

            prefix = Prefix.from_bytes(data[:4])
            header = Header.from_bytes(data[4:16])
            if header.msg_type == MsgType.JOINT_FEEDBACK:
                with self._lock:
                    self._joint_feedback = JointFeedback.from_bytes(
                        data[16 : prefix.length - 12]
                    )

