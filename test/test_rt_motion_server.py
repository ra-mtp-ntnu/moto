import logging
import socket

from moto.simple_message import *

logging.basicConfig(level=logging.DEBUG)


def start_udp_server(address):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    return server


def main():
    server = start_udp_server(("localhost", 50244))
    started = False
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
                        MotoRealTimeMotionJointCommandExData(joint_state.groupno, [0.1] * 6)
                        for joint_state in state.joint_state_data
                    ],
                ),
            )

            server.sendto(command_msg.to_bytes(), addr)
        except socket.timeout as e:
            logging.error("Timed out!")
            break


if __name__ == "__main__":
    main()
