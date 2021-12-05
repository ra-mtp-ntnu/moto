
from moto import Moto, ControlGroupDefinition
from moto.simple_message import (
    JointFeedbackEx,
    JointTrajPtExData,
    JointTrajPtFullEx,
    ValidFields,
)

import time
import numpy as np

m = Moto(
    "172.16.0.1", #"192.168.255.201",
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
            time=2.0,
            pos=np.deg2rad([10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
        JointTrajPtExData(
            groupno=1,
            valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
            time=2.5,
            pos=np.deg2rad([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
    ],
)

WARN = '\033[5;1;31;1;44m' # blinking red on blue
HIGHLIGHT = '\033[37;1;44m' # White on blue
UNDERLINE = '\033[4;37;1;44m' # Underlined white on blue 
CLEAR = '\033[0m' # clear formatting

print(f'{WARN}        Warning!        {CLEAR}')
print(f'{HIGHLIGHT}Will now try to move the robot to its home position. '\
+ f'Make sure this operation is safe!{CLEAR}')
print(f'{HIGHLIGHT}Are you ready? Type \'{UNDERLINE}sure{CLEAR}{HIGHLIGHT}\' '\
+ f'to start. Any other text will abort.{CLEAR}')
response = input(f'>')

if response == 'sure':
    for i in range(5, 0, -1): 
        print(f'{i}...', end=' ')
        time.sleep(1);
    
    # m.motion.start_trajectory_mode()
    print("Waiting for robot to be ready...", end=' ')
    while not m.state.robot_status().motion_possible and \
        not m.state.robot_status().drives_powered:
        time.sleep(0.1)

    print("Robot ready. Sending trajectory.")  
    m.motion.send_joint_trajectory_point(p0) # Current position at time t=0.0
    m.motion.send_joint_trajectory_point(p1) # Desired position at time t=5.0

    input("Press enter when robot has stopped.")

    print("Disabling trajectory mode, and turning off servos.") 
    m.motion.stop_trajectory_mode()
    m.motion.stop_servos()

    print("Done.")

else: 
    print("Aborting... Good bye.")


