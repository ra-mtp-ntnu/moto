from moto import Moto
from moto.simple_message import JointTrajPtFull

import time
import numpy as np
import copy


m = Moto("192.168.255.200", [("R1", 6)])

r = m.control_group("R1")


def send_pts():
    x= copy.deepcopy(list(r.joint_feedback.pos))
    pt1 = JointTrajPtFull(0, 0, int("1111",2), 0.0, copy.deepcopy(x), [0.0]*10, [0.0]*10)
    x[0] -= np.deg2rad(30)
    pt2 = JointTrajPtFull(0, 1, int("1111",2), 10.0, copy.deepcopy(x), [0.0]*10, [0.0]*10)
    x[0] += np.deg2rad(5)
    pt3 = JointTrajPtFull(0, 2, int("1111",2), 20.0, copy.deepcopy(x), [0.0]*10, [0.0]*10)

    r.send_joint_traj_pt_full(pt1)
    r.send_joint_traj_pt_full(pt2)
    r.send_joint_traj_pt_full(pt3)

    print(r.check_queue_count())


# print(r.groupid)

# pt1 = JointTrajPtFull(0, 0, int("1111", 2), 10.0, [1.0] * 10, [0.0] * 10, [0.0] * 10)

# pt2 = JointTrajPtFull(0, 0, int("1111", 2), 20.0, [2.0] * 10, [0.0] * 10, [0.0] * 10)

# r.send_joint_traj_pt_full(pt1)
# r.send_joint_traj_pt_full(pt2)


# for _ in range(1000):
#     time.sleep(0.1)
#     print(r.joint_feedback)


# robot = m.control_group(0)

# # robot = cell.control_group("R1")
# # positioner = cell.control_group[1]

# pos = np.array([ 0.00438486, -0.82990497, -0.89975643, -0.59869617, -0.96005285,
#        -0.10957382,  0.        ,  0.        ,  0.        ,  0.        ])

# pos2 = pos.copy()

# pos2[0] += np.deg2rad(5)


# def sendpt(pos, time, sequence):
#     vel = np.zeros(10)
#     acc = np.zeros(10)

#     body  = JointTrajPtFull(0, sequence, int("1111",2), time, pos, vel, acc )

#     header = Header(MsgType.JOINT_TRAJ_PT_FULL, CommType.TOPIC, ReplyType.INVALID)

#     msg = header.to_bytes() + body.to_bytes()
#     msg = Prefix(len(msg)).to_bytes() + msg

#     robot.motion_connection._tcp_client.send(msg)

# servos_started = robot.motion_connection.start_servos()
# print(servos_started)

# motion_ready = robot.motion_connection.check_motion_ready()
# print(motion_ready)


# servos_stopped = robot._motion_connection.stop_servos()
# print(servos_stopped)
