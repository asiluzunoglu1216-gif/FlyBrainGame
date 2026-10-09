import unittest
from panda3d.core import Vec3, NodePath
from game.frog_entity import FrogEntity

class TestFrogEncounterCounter(unittest.TestCase):
    def test_hysteresis_single_encounter(self):
        root = NodePath('FrogRoot')
        frog = FrogEntity(root, 'Frog1', Vec3(0,0,0))

        # Enter zone
        self.assertTrue(frog.check_encounter(Vec3(12, 0, 0)))

        # Hover in zone for 30 steps -> must not increment
        for _ in range(30):
            self.assertFalse(frog.check_encounter(Vec3(12, 0, 0)))

        # Exit zone
        self.assertFalse(frog.check_encounter(Vec3(35, 0, 0)))

        # Re-enter zone -> new encounter
        self.assertTrue(frog.check_encounter(Vec3(12, 0, 0)))

if __name__ == '__main__':
    unittest.main()