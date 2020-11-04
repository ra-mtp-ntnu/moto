from moto import Moto
from moto.simple_message import JointTrajPtFull

import time
import numpy as np
import copy


# m = Moto("192.168.255.200", [("R1", 6)])
m = Moto("localhost", [("R1", 6), ("S1", 2)]) # Sim with two groups

r = m.control_groups["R1"]


def send_pts(seq, p, t):
    x = copy.deepcopy(list(r.joint_feedback.pos))
    x[0] = np.deg2rad(p)
    pt1 = JointTrajPtFull(
        0, 2, int("1111", 2), t, copy.deepcopy(x), [0.0] * 10, [0.0] * 10
    )

    # m._motion_connection.send_joint_traj_pt_full(pt1)
    # m._motion_connection.send_joint_traj_pt_full(pt2)
    m._motion_connection.send_joint_traj_pt_full(pt1)
    time.sleep(0.01)

time.sleep(1.0)

send_pts(0, 0.0, 0.0)
send_pts(1, 45.0, 10.0)
send_pts(2, 20.0, 20.0)