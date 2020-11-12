from copy import copy
import time
import socket

import numpy as np

from moto.simple_message import (
    CommType,
    CommandType,
    MotoMotionReply,
    SimpleMessage,
    Header,
    MotoMotionCtrl,
    MsgType,
    ReplyType,
)


def start_udp_server(address):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    return server


def main():

    server = start_udp_server(("192.168.255.3", 50244))

    pos0 = None

    setpoint = np.deg2rad(30)
    kp = 0.01

    while True:

        bytes_, addr = server.recvfrom(1024)
        msg = SimpleMessage.from_bytes(bytes_)
        state: MotoMotionReply = msg.body

        # print(state.sequence)

        velcmd = [0.0] * 10
        velcmd[0] = kp * (setpoint - state.data[0])
        print(velcmd)

        cmd = SimpleMessage(
            Header(MsgType.MOTO_MOTION_CTRL, CommType.TOPIC, ReplyType.INVALID),
            MotoMotionCtrl(-1, state.sequence, CommandType.REALTIME_MOTION_CMD, velcmd),
        )

        server.sendto(cmd.to_bytes(), addr)


if __name__ == "__main__":
    main()
