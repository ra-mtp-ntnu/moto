# moto
A Python library for controlling Yaskawa MOTOMAN robots.

## Installation

```bash
pip3 install git+https://github.com/tingelst/moto.git --upgrade
```

On the robot side, the `moto` library employs the ROS-Industrial robot driver found here: https://github.com/ros-industrial/motoman. Follow the official [tutorial](http://wiki.ros.org/motoman_driver/Tutorials/indigo/InstallServer) for installing the necessary files on the robot controller. 

## Example

The highest level API is defined in `Moto` class.

```python
from moto import Moto
```

Connect to the robot controller with the defined ip address `<robot_ip>` and define the `R1` control group with two degrees of freedom.

```python
m = Moto("<robot_ip>", [("R1", 6)]) 
```

If your robot system has multiple control groups, e.g. a positioner with two degrees of freedom, these can be defined as follows: 
```python
m = Moto("<robot_ip>", [("R1", 6), ("S1", 2)]) 
```
Note that these tuples must be in the same order as those on the controller. Here, this means that "R1" is the name control group 0 and "S1" is the name of control group 1. The system supports up to 4 control groups.

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
def send_trajectory_point(seq: int, pos_increment: float, time_from_start: float):
    x = copy.copy(list(r1.joint_feedback.pos))
    x[0] += np.deg2rad(pos_increment)
    pt = JointTrajPtFull(
        0, seq, int("0011", 2), time_from_start, copy.deepcopy(x), [0.0] * 10, [0.0] * 10
    )
    m._motion_connection.send_joint_traj_pt_full(pt)

# The trajectory must always start at the current position
send_trajectory_point(m, 0, 0.0, 0.0) 
# Move the joint 1 by 45 degrees in 10 seconds
send_trajectory_point(m, 1, 45.0, 10.0)
```

### IO

You can read and write bits:
```python
m.io.read_bit(27010)
m.io.write_bit(27010, 0)
```
as well as bytes:
```python
m.io.read_group(27010)
m.io.write_group(27010, 42)
```

As per the [documentation](https://github.com/ros-industrial/motoman/blob/591a09c5cb95378aafd02e77e45514cfac3a009d/motoman_msgs/srv/WriteSingleIO.srv#L9-L12), only the following addresses can be written to:
- 27010 and up : Network Inputs (25010 and up on DX100 and FS100)
- 10010 and up : Universal/General Outputs

### ROS2 and Real-time control

An extension of the current robot side driver with support for real-time control, and an accompanying ROS2 Control hardware interface is under development [here](https://github.com/tingelst/motoman) and [here](https://github.com/tingelst/motoman_hardware), respectively.

# Acknowledgements

This work is supported by the Norwegian Research Council infrastructure project MANULAB: Norwegian Manufacturing Research Laboratory under grant 269898.


