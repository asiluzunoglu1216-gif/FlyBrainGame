import unittest
from panda3d.core import Vec3, NodePath
from game.frog_entity import FrogEntity

class TestFrogTongueCollision(unittest.TestCase):
    def test_physical_tip_collider(self):
        root = NodePath('FrogTest')
        frog = FrogEntity(root, 'Kermit', Vec3(0,0,0))
        frog.state = 'TONGUE_STRIKE'
        frog.tongue_target = Vec3(0, 3.5, 0.8)
        frog.tongue_timer = 0.20

        caught_out = frog.update(0.02, Vec3(18, 0, 0))
        self.assertFalse(caught_out)

        fly_pos = Vec3(0, 3.5, 0.8)
        frog.update(0.02, fly_pos)
        self.assertTrue(frog.physical_hit, "Physical hit must be registered on collision")

        # Advance through pull animation until consumption
        consumed = False
        for _ in range(40):
            if frog.update(0.02, fly_pos):
                consumed = True
                break
        self.assertTrue(consumed, "Fly must be consumed after capture pull")

if __name__ == '__main__':
    unittest.main()