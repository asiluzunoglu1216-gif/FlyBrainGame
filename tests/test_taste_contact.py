import unittest
from panda3d.core import Vec3
from game.ecosystem_sensory import EcosystemSensoryManager
from game.odor_system import OdorEcosystemManager

class TestTasteContact(unittest.TestCase):
    def test_tarsal_and_labellar_taste(self):
        eco = EcosystemSensoryManager()
        odor = OdorEcosystemManager()
        f = odor.foods[0]
        sensory, _, _ = eco.compute_sensory_input(
            fly_pos=f.pos + Vec3(0,0,0.1), fly_yaw=0,
            terrain_dist_l=40, terrain_dist_c=40, terrain_dist_r=40,
            foods=[(f.name, f.pos)], frogs=[], odor_manager=odor
        )
        self.assertGreater(sensory.taste_sugar, 0.0)
        self.assertGreater(sensory.leg_taste, 0.0)

    def test_6leg_contacts_on_ground(self):
        eco = EcosystemSensoryManager()
        sensory, _, _ = eco.compute_sensory_input(
            fly_pos=Vec3(0,0,0.3), fly_yaw=0,
            terrain_dist_l=40, terrain_dist_c=40, terrain_dist_r=40,
            foods=[], frogs=[], surface_z=0.0, surface_type='GROUND', locomotion_mode='GROUNDED'
        )
        self.assertEqual(len(sensory.leg_contacts), 6)
        self.assertTrue(all(sensory.leg_contacts))

if __name__ == '__main__':
    unittest.main()