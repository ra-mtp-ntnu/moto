from moto.simple_message import JointTrajPtExData, JointTrajPtFullEx, ValidFields

p0 = JointTrajPtExData(
    groupno=0,
    valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
    time=0.0,
    pos=[0.0] * 10,
    vel=[0.0] * 10,
    acc=[0.0] * 10,
)

p1 = JointTrajPtExData(
    groupno=1,
    valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
    time=0.0,
    pos=[0.0] * 10,
    vel=[0.0] * 10,
    acc=[0.0] * 10,
)

t = JointTrajPtFullEx(
    number_of_valid_groups=2,
    sequence=0,
    joint_traj_pt_data=
    [ JointTrajPtExData(
        groupno=0,
        valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
        time=0.0,
        pos=[0.0] * 10,
        vel=[0.0] * 10,
        acc=[0.0] * 10,
    ), 
 JointTrajPtExData(
    groupno=1,
    valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
    time=0.0,
    pos=[0.0] * 10,
    vel=[0.0] * 10,
    acc=[0.0] * 10,
)
    ]
)


