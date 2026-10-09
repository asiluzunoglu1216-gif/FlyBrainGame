import unittest
from game.motor_decoder import MotorDecoder
from game.internal_state import InternalPhysiologicalState

class TestProboscisFeeding(unittest.TestCase):
    def test_feeding_pop_extends_proboscis(self):
        dec = MotorDecoder()
        motor = dec.decode(feeding_pop_hz=6.0, fwd_pop_hz=0.0)
        self.assertGreater(motor.proboscis_extension, 0.5)
        self.assertEqual(motor.decision, 'FEEDING_PROBOSCIS_ACTIVE')

    def test_feeding_recovery(self):
        st = InternalPhysiologicalState(energy=0.4)
        st.update(dt=3.0, locomotion_mode='GROUNDED', speed=0.0, feeding_activity=1.0)
        self.assertGreater(st.energy, 0.4)

if __name__ == '__main__':
    unittest.main()