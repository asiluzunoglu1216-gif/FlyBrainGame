import unittest
from panda3d.core import Vec3
from game.odor_system import OdorEcosystemManager

class TestFoodOlfaction(unittest.TestCase):
    def setUp(self):
        self.mgr = OdorEcosystemManager()

    def test_spatial_gradient(self):
        f = self.mgr.foods[0]
        p_close = f.pos + Vec3(2, 0, 0)
        p_far = f.pos + Vec3(15, 0, 0)
        c_close, _, _, _ = self.mgr.compute_odor_at_point(p_close, 90, Vec3(0,0,0), 0)
        c_far, _, _, _ = self.mgr.compute_odor_at_point(p_far, 90, Vec3(0,0,0), 0)
        self.assertGreater(c_close, c_far)

    def test_wind_advection(self):
        f = self.mgr.foods[0]
        c_down, _, _, _ = self.mgr.compute_odor_at_point(f.pos + Vec3(8,0,0), 90, Vec3(1,0,0), 3.0)
        c_up, _, _, _ = self.mgr.compute_odor_at_point(f.pos - Vec3(8,0,0), 90, Vec3(1,0,0), 3.0)
        self.assertGreater(c_down, c_up)

    def test_bilateral_differential(self):
        f = self.mgr.foods[0]
        # Fly facing North (+Y), food to the left (-X)
        _, l_c, r_c, _ = self.mgr.compute_odor_at_point(f.pos + Vec3(4,0,0), 90, Vec3(0,0,0), 0)
        self.assertGreater(l_c, r_c)

if __name__ == '__main__':
    unittest.main()