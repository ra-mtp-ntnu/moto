import unittest
from moto.simple_message import JointTrajPtFull, ValidFields


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


if __name__ == "__main__":
    unittest.main()
