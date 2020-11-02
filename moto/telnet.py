from telnetlib import Telnet
from threading import Thread, Lock
import logging


class TelnetConnection:
    def __init__(self, ip_address: str):
        self._ip_address: str = ip_address
        self._username: str = "MOTOMANrobot"
        self._password: str = "MOTOMANrobot"
        self._tn: Telnet = Telnet(self._ip_address)

        self._run_thread = Thread(target=self._run)
        self._run_thread.daemon = True

    def login(self) -> None:
        self._tn.read_until(b"login: ")
        self._tn.write(self._username.encode("ascii") + b"\n")
        self._tn.read_until(b"Password: ")
        self._tn.write(self._password.encode("ascii") + b"\n")

        self._run_thread.start()

    def _run(self) -> None:
        print(self._tn.read_all())
