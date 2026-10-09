import unittest
from game.motor_decoder import MotorDecoder

class TestLandingContact(unittest.TestCase):
    def test_dnp02_landing_readiness(self):
        dec = MotorDecoder()
        motor = dec.decode(landing_pop_hz=5.0)
        self.assertGreater(motor.landing_readiness, 0.5)

if __name__ == '__main__':
    unittest.main()