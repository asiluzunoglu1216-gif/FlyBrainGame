import unittest
from game.internal_state import InternalPhysiologicalState
from game.motor_decoder import MotorDecoder

class TestHungerModulation(unittest.TestCase):
    def test_energy_burn_rates(self):
        s_flight = InternalPhysiologicalState(energy=1.0)
        s_flight.update(10.0, 'AIRBORNE', 6.0)
        s_walk = InternalPhysiologicalState(energy=1.0)
        s_walk.update(10.0, 'GROUNDED', 2.0)
        s_rest = InternalPhysiologicalState(energy=1.0)
        s_rest.update(10.0, 'GROUNDED', 0.0)
        self.assertLess(s_flight.energy, s_walk.energy)
        self.assertLess(s_walk.energy, s_rest.energy)

    def test_hunger_modulates_sensory_gains(self):
        s_hungry = InternalPhysiologicalState(energy=0.2)
        s_satiated = InternalPhysiologicalState(energy=0.9)
        self.assertGreater(s_hungry.olfactory_gain, s_satiated.olfactory_gain)
        self.assertGreater(s_hungry.gustatory_gain, s_satiated.gustatory_gain)

    def test_zero_spike_zero_propulsion(self):
        dec = MotorDecoder()
        motor = dec.decode(fwd_pop_hz=0.0)
        self.assertEqual(motor.forward_speed, 0.0)

if __name__ == '__main__':
    unittest.main()