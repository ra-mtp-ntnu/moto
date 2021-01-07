from copy import copy
import logging
import socket
import time
import numpy as np

from moto.simple_message import *

logging.basicConfig(level=logging.DEBUG)


def start_udp_server(address):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    return server


def main():
    server = start_udp_server(("192.168.255.3", 50244))
    started = False

    t0 = time.time()
    p0 = None
    while True:

        try:
            bytes_, addr = server.recvfrom(1024)
            if not bytes_:
                logging.error("Stopping!")
                break

            if not started:
                server.settimeout(1.0)
                started = True


            msg = SimpleMessage.from_bytes(bytes_)
            state: MotoRealTimeMotionJointStateEx = msg.body

            if p0 is None:
                p0 = copy(state.joint_state_data[1].pos)

            print("state:   {}".format(state.joint_state_data[1].vel[0]))

            # pd = np.deg2rad(10)
            # Kv = 0.1
            # vd = Kv * (pd - state.joint_state_data[1].pos[0])

            vd  = 0.1 * (np.sin(3.0 * time.time() - t0))

            # vd = 0.05


            print("command: {}".format(vd))

            command_msg: SimpleMessage = SimpleMessage(
                Header(
                    MsgType.MOTO_REALTIME_MOTION_JOINT_COMMAND_EX,
                    CommType.TOPIC,
                    ReplyType.INVALID,
                ),
                MotoRealTimeMotionJointCommandEx(
                    state.message_id,
                    state.number_of_valid_groups,
                    [
                        MotoRealTimeMotionJointCommandExData(
                            0, [vd, 0.0, 0.0, 0.0, 0.0, 0.0]
                        ),
                        MotoRealTimeMotionJointCommandExData(1, [vd, 0.0]),
                        
                    ],
                ),
            )

            server.sendto(command_msg.to_bytes(), addr)
        except socket.timeout as e:
            logging.error("Timed out!")
            break


if __name__ == "__main__":

    main()
