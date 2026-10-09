import unittest
from panda3d.core import NodePath
from game.fly_model import FlyModel

class TestWalking(unittest.TestCase):
    def test_tripod_walking_animation(self):
        root = NodePath('Fly')
        model = FlyModel(root)
        model.animate(0.1, flying=False, speed=3.0)
        p0 = model.legs[0][0].getP()
        p1 = model.legs[1][0].getP()
        self.assertNotEqual(p0, p1)

if __name__ == '__main__':
    unittest.main()