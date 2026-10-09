import unittest
import numpy as np
from pathlib import Path
from game.memory_system import MushroomBodyMemorySystem

class TestMemoryPersistenceRetry(unittest.TestCase):
    def test_persistence_across_death_and_retry(self):
        p = Path('memory/test_death_retry.npz')
        if p.exists(): p.unlink()

        kc = np.arange(40, dtype=np.int32)
        mbon = np.arange(8, dtype=np.int32)
        pam = np.array([80], dtype=np.int32)
        ppl1 = np.array([90], dtype=np.int32)

        mem1 = MushroomBodyMemorySystem(kc, mbon, pam, ppl1, memory_path=p)
        mem1.update_activity_trace({0, 5}, dt=0.02)
        mem1.apply_reinforcement(pam_reward=1.0)
        mem1.save()

        self.assertTrue(p.exists())
        self.assertLess(p.stat().st_size, 2 * 1024 * 1024 * 1024)

        mem2 = MushroomBodyMemorySystem(kc, mbon, pam, ppl1, memory_path=p)
        self.assertEqual(mem2.associations_count, mem1.associations_count)
        self.assertTrue(np.allclose(mem2.weights, mem1.weights))
        p.unlink()

if __name__ == '__main__':
    unittest.main()