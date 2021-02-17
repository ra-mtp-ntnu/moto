from moto import motion_connection
from moto import Moto, ControlGroupDefinition
from moto.simple_message import (
    JointFeedbackEx,
    JointTrajPtExData,
    JointTrajPtFull,
    JointTrajPtFullEx,
    ValidFields,
)

import time
import numpy as np
import copy

m = Moto(
    "192.168.255.200",
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
            joint_names=["joint_1", "joint_2",],
        ),
    ],
    start_motion_connection=True,
    start_state_connection=True,
)


robot = m.control_groups["robot"]
positioner = m.control_groups["positioner"]

time.sleep(1)


robot_joint_feedback: JointFeedbackEx = m.state.joint_feedback_ex()

p0 = JointTrajPtFullEx(
    number_of_valid_groups=2,
    sequence=0,
    joint_traj_pt_data=[
        JointTrajPtExData(
            groupno=0,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=0.0,
            pos=robot_joint_feedback.joint_feedback_data[0].pos,
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
        JointTrajPtExData(
            groupno=1,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=0.0,
            pos=robot_joint_feedback.joint_feedback_data[1].pos,
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
    ],
)

p1 = JointTrajPtFullEx(
    number_of_valid_groups=2,
    sequence=1,
    joint_traj_pt_data=[
        JointTrajPtExData(
            groupno=0,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=5.0,
            pos=np.deg2rad([10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
        JointTrajPtExData(
            groupno=1,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=10.0,
            pos=np.deg2rad([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
    ],
)

