import unittest

from moto.simple_message import (
    JointFeedback,
    JointTrajPtFull,
    MotoMotionCtrl,
    MotoMotionReply,
    PendantMode,
    ResultType,
    RobotStatus,
    SubCode,
    CommandType,
    Ternary,
    ValidFields,
)


class TestRobotStatus(unittest.TestCase):
    def test_to_and_from_bytes(self):
        robot_status = RobotStatus(
            drives_powered=Ternary.TRUE,
            e_stopped=Ternary.TRUE,
            error_code=42,
            in_error=Ternary.TRUE,
            in_motion=Ternary.TRUE,
            mode=PendantMode.MANUAL,
            motion_possible=Ternary.TRUE,
        )

        robot_status_from_bytes = RobotStatus.from_bytes(robot_status.to_bytes())

        self.assertEqual(
            robot_status.drives_powered, robot_status_from_bytes.drives_powered
        )
        self.assertEqual(robot_status.e_stopped, robot_status_from_bytes.e_stopped)
        self.assertEqual(robot_status.error_code, robot_status_from_bytes.error_code)
        self.assertEqual(robot_status.in_error, robot_status_from_bytes.in_error)
        self.assertEqual(robot_status.in_motion, robot_status_from_bytes.in_motion)
        self.assertEqual(robot_status.mode, robot_status_from_bytes.mode)
        self.assertEqual(
            robot_status.motion_possible, robot_status_from_bytes.motion_possible
        )


class TestJointTrajPtFull(unittest.TestCase):
    def test_to_and_from_bytes(self):
        joint_traj_pt_full = JointTrajPtFull(
            groupno=0,
            sequence=42,
            valid_fields=ValidFields.TIME
            | ValidFields.POSITION
            | ValidFields.VELOCITY
            | ValidFields.ACCELERATION,
            time=1.5,
            pos=[1.0, 2.0, 3.0123, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        )

        joint_traj_pt_full_from_bytes = JointTrajPtFull.from_bytes(
            joint_traj_pt_full.to_bytes()
        )

        self.assertEqual(
            joint_traj_pt_full.groupno, joint_traj_pt_full_from_bytes.groupno
        )
        self.assertEqual(
            joint_traj_pt_full.sequence, joint_traj_pt_full_from_bytes.sequence
        )
        self.assertEqual(
            joint_traj_pt_full.valid_fields, joint_traj_pt_full_from_bytes.valid_fields
        )
        self.assertAlmostEqual(
            joint_traj_pt_full.time, joint_traj_pt_full_from_bytes.time
        )
        for p, p_from_bytes in zip(
            joint_traj_pt_full.pos, joint_traj_pt_full_from_bytes.pos
        ):
            self.assertAlmostEqual(p, p_from_bytes)

        for v, v_from_bytes in zip(
            joint_traj_pt_full.vel, joint_traj_pt_full_from_bytes.vel
        ):
            self.assertAlmostEqual(v, v_from_bytes)

        for a, a_from_bytes in zip(
            joint_traj_pt_full.acc, joint_traj_pt_full_from_bytes.acc
        ):
            self.assertAlmostEqual(a, a_from_bytes)


class TestJointFeedback(unittest.TestCase):
    def test_to_and_from_bytes(self):
        joint_feedback = JointFeedback(
            groupno=0,
            valid_fields=ValidFields.TIME
            | ValidFields.POSITION
            | ValidFields.VELOCITY
            | ValidFields.ACCELERATION,
            time=42.1,
            pos=[0.0] * 10,
            vel=[0.0] * 10,
            acc=[0.0] * 10,
        )

        joint_feedback_from_bytes = JointFeedback.from_bytes(joint_feedback.to_bytes())

        self.assertEqual(joint_feedback.groupno, joint_feedback_from_bytes.groupno)
        self.assertEqual(
            joint_feedback.valid_fields, joint_feedback_from_bytes.valid_fields
        )
        self.assertAlmostEqual(
            joint_feedback.time, joint_feedback_from_bytes.time, places=4
        )

        for p, p_from_bytes in zip(joint_feedback.pos, joint_feedback_from_bytes.pos):
            self.assertAlmostEqual(p, p_from_bytes)

        for v, v_from_bytes in zip(joint_feedback.vel, joint_feedback_from_bytes.vel):
            self.assertAlmostEqual(v, v_from_bytes)

        for a, a_from_bytes in zip(joint_feedback.acc, joint_feedback_from_bytes.acc):
            self.assertAlmostEqual(a, a_from_bytes)


class TestMotoMotionCtrl(unittest.TestCase):
    def test_to_and_from_bytes(self):
        moto_motion_ctrl = MotoMotionCtrl(
            groupno=1, sequence=42, command=CommandType.START_SERVOS, data=[0.0] * 10
        )

        moto_motion_ctrl_from_bytes = MotoMotionCtrl.from_bytes(
            moto_motion_ctrl.to_bytes()
        )

        self.assertEqual(moto_motion_ctrl.groupno, moto_motion_ctrl_from_bytes.groupno)
        self.assertEqual(
            moto_motion_ctrl.sequence, moto_motion_ctrl_from_bytes.sequence
        )
        self.assertEqual(moto_motion_ctrl.command, moto_motion_ctrl_from_bytes.command)
        for d, d_from_bytes in zip(moto_motion_ctrl.data, moto_motion_ctrl.data):
            self.assertAlmostEqual(d, d_from_bytes)


class TestMotoMotionReply(unittest.TestCase):
    def test_to_and_from_bytes(self):
        moto_motion_reply = MotoMotionReply(
            groupno=1,
            sequence=42,
            command=CommandType.START_SERVOS,
            result=ResultType.ALARM,
            subcode=SubCode.NOT_READY_HOLD,
            data=[0.0] * 10,
        )

        moto_motion_reply_from_bytes = MotoMotionReply.from_bytes(
            moto_motion_reply.to_bytes()
        )

        self.assertEqual(
            moto_motion_reply.groupno, moto_motion_reply_from_bytes.groupno
        )
        self.assertEqual(
            moto_motion_reply.sequence, moto_motion_reply_from_bytes.sequence
        )
        self.assertEqual(
            moto_motion_reply.command, moto_motion_reply_from_bytes.command
        )
        self.assertEqual(moto_motion_reply.result, moto_motion_reply_from_bytes.result)
        self.assertEqual(
            moto_motion_reply.subcode, moto_motion_reply_from_bytes.subcode
        )
        for d, d_from_bytes in zip(moto_motion_reply.data, moto_motion_reply.data):
            self.assertAlmostEqual(d, d_from_bytes)


if __name__ == "__main__":
    unittest.main()
