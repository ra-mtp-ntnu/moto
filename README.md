# moto
A Python library for controlling Yaskawa MOTOMAN robots with the MotoROS option.

## Installation

```bash
pip3 install git+https://github.com/tingelst/moto.git --upgrade
```

On the robot side, the `moto` library employs the ROS-Industrial robot driver found here: https://github.com/ros-industrial/motoman. Follow the official [tutorial](http://wiki.ros.org/motoman_driver/Tutorials/indigo/InstallServer) for installing the necessary files on the robot controller. 

## Example

The highest level API is defined in the `Moto` class.

```python
from moto import Moto
```

Connect to the robot controller with the defined ip address `<robot_ip>` and define the `R1` control group with six degrees of freedom.

```python
m = Moto(
    "<robot_ip>",
    [
        ControlGroupDefinition(
            groupid="R1",
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
    ],
)
```

If your robot system has multiple control groups, e.g. a positioner with two degrees of freedom, these can be defined as follows: 
```python
m = Moto(
    "<robot_ip>",
    [
        ControlGroupDefinition(
            groupid="R1",
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
            groupid="S1",
            groupno=1,
            num_joints=2,
            joint_names=[
                "joint_1",
                "joint_2",
            ],
        ),
    ],
)
```
The system supports up to 4 control groups.

Each control group can be accessed and introspected by name:
```python
r1 = m.control_groups["R1"]
print(r1.position)
``` 

### Motion

To be able to send trajectores, you must first enable the robot system:
```python
m.motion.enable_robot()
```
And then start the trajectory mode:
```python
m.motion.start_trajectory_mode()
```

The API for sending trajectories is still under development. For now, to move joint 1 you can e.g. do:
```python
robot_joint_feedback = m.state.joint_feedback_ex()

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
            time=5.0,
            pos=np.deg2rad([10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        ),
    ],
)

m.motion.send_trajectory_point(p0) # Current position at time t=0.0
m.motion.send_trajectory_point(p1) # Desired position at time t=5.0
```

### IO

You can read and write bits:
```python
m.io.read_bit(27010)
m.io.write_bit(27010, 0)
```
as well as bytes:
```python
m.io.read_group(1001)
m.io.write_group(1001, 42)
```

As per the [documentation](https://github.com/ros-industrial/motoman/blob/591a09c5cb95378aafd02e77e45514cfac3a009d/motoman_msgs/srv/WriteSingleIO.srv#L9-L12), only the following addresses can be written to:
- 27010 and up : Network Inputs (25010 and up on DX100 and FS100)
- 10010 and up : Universal/General Outputs

### ROS2 and Real-time control

An extension of the current robot side driver with support for real-time control, and an accompanying ROS2 Control hardware interface is under development [here](https://github.com/tingelst/motoman) and [here](https://github.com/tingelst/motoman_hardware), respectively.

# Acknowledgements

This work is supported by the Norwegian Research Council infrastructure project MANULAB: Norwegian Manufacturing Research Laboratory under grant 269898.


