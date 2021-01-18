from moto import motion_connection
from moto import Moto, ControlGroupDefinition
from moto.simple_message import JointTrajPtFull

import time
import numpy as np
import copy

m = Moto(
    "localhost",
    [
        ControlGroupDefinition(
            groupid="robot",
            groupno=0,
            num_joints=6,
            joint_names=[
                "joint_1_s",
                "joint_2_l",
                "joint_3_u",
                "joint_4_r",
                "joint_5_b",
                "joint_6_t",
            ],
        ),
        ControlGroupDefinition(
            groupid="positioner",
            groupno=1,
            num_joints=2,
            joint_names=[
                "joint_1",
                "joint_2",
            ],
        ),
    ],
)


r = m.control_groups["robot"]
# s = m.control_groups["S1"]


def send_pts(seq, p, t):
    x = copy.deepcopy(list(r.joint_feedback.pos))
    x[0] += np.deg2rad(p)
    pt1 = JointTrajPtFull(
        0, seq, int("1111", 2), t, copy.deepcopy(x), [0.0] * 10, [0.0] * 10
    )

    # m._motion_connection.send_joint_traj_pt_full(pt1)
    # m._motion_connection.send_joint_traj_pt_full(pt2)
    m._motion_connection.send_joint_traj_pt_full(pt1)
    time.sleep(0.01)


# time.sleep(1.0)

# send_pts(0, 0.0, 0.0)
# send_pts(1, 45.0, 10.0)
# send_pts(2, 20.0, 20.0)