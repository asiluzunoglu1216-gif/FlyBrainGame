import os
import unittest
import numpy as np
from pathlib import Path
from panda3d.core import Vec3, Vec4, NodePath

from game.internal_state import InternalPhysiologicalState
from game.odor_system import OdorEcosystemManager, FoodSource
from game.sensory_encoder import SensoryInput, FeatureEncoder
from game.motor_decoder import MotorDecoder, MotorState
from game.memory_system import MushroomBodyMemorySystem
from game.frog_entity import FrogEntity
from game.ecosystem_sensory import EcosystemSensoryManager
from game.fly_model import FlyModel


class TestHungerModulation(unittest.TestCase):
    def test_metabolic_burn_rates_and_gains(self):
        state = InternalPhysiologicalState(energy=1.0)
        # Flight burn
        state.update(dt=10.0, locomotion_mode='AIRBORNE', speed=6.0)
        flight_energy = state.energy
        self.assertLess(flight_energy, 1.0)

        # Walking burn
        state2 = InternalPhysiologicalState(energy=1.0)
        state2.update(dt=10.0, locomotion_mode='GROUNDED', speed=2.0)
        walk_energy = state2.energy
        self.assertGreater(walk_energy, flight_energy, 'Flight must burn more energy than walking')

        # Gains scale with hunger
        starved_state = InternalPhysiologicalState(energy=0.1)
        starved_state.update(dt=0.01, locomotion_mode='AIRBORNE', speed=0.0)
        satiated_state = InternalPhysiologicalState(energy=0.95)
        satiated_state.update(dt=0.01, locomotion_mode='AIRBORNE', speed=0.0)

        self.assertGreater(starved_state.olfactory_gain, satiated_state.olfactory_gain)
        self.assertGreater(starved_state.gustatory_gain, satiated_state.gustatory_gain)

    def test_hunger_does_not_produce_artificial_speed(self):
        decoder = MotorDecoder()
        # High hunger but 0 motor population Hz
        motor = decoder.decode(fwd_pop_hz=0.0)
        self.assertEqual(motor.forward_speed, 0.0, 'Zero motor spike rate must strictly yield 0.0 forward speed regardless of hunger')


class TestFoodOlfaction(unittest.TestCase):
    def setUp(self):
        self.mgr = OdorEcosystemManager()

    def test_odor_diffusion_and_wind_advection(self):
        food = self.mgr.foods[0]
        wind_dir = Vec3(1, 0, 0)
        wind_speed = 3.0

        # Downwind position (east of food)
        downwind_pos = food.pos + Vec3(10.0, 0.0, 0.0)
        c_down, _, _, _ = self.mgr.compute_odor_at_point(downwind_pos, heading_deg=90.0, wind_dir=wind_dir, wind_speed=wind_speed)

        # Upwind position (west of food) at equal distance
        upwind_pos = food.pos - Vec3(10.0, 0.0, 0.0)
        c_up, _, _, _ = self.mgr.compute_odor_at_point(upwind_pos, heading_deg=90.0, wind_dir=wind_dir, wind_speed=wind_speed)

        self.assertGreater(c_down, c_up, 'Downwind concentration must exceed upwind concentration due to advection')

    def test_bilateral_antennae_differential(self):
        food = self.mgr.foods[0]
        fly_pos = food.pos + Vec3(5.0, 0.0, 0.0)
        fly_yaw = 90.0

        _, conc_l, conc_r, n_food = self.mgr.compute_odor_at_point(
            point=fly_pos, heading_deg=fly_yaw, wind_dir=Vec3(0, 0, 0), wind_speed=0.0
        )
        self.assertEqual(n_food.name, food.name)
        self.assertGreater(conc_l, conc_r, 'Left antenna must receive higher concentration when food is to the left')


class TestTasteAndLegContact(unittest.TestCase):
    def test_taste_detection_on_proximity(self):
        eco_mgr = EcosystemSensoryManager()
        odor_mgr = OdorEcosystemManager()
        internal = InternalPhysiologicalState(energy=0.5)

        food = odor_mgr.foods[0]
        fly_pos = food.pos + Vec3(0, 0, 0.2)

        sensory, _, _ = eco_mgr.compute_sensory_input(
            fly_pos=fly_pos,
            fly_yaw=0.0,
            terrain_dist_l=40.0, terrain_dist_c=40.0, terrain_dist_r=40.0,
            foods=[(food.name, food.pos)],
            frogs=[],
            odor_manager=odor_mgr,
            internal_state=internal
        )

        self.assertGreater(sensory.taste_sugar, 0.0, 'Sugar taste must be detected at food surface')
        self.assertGreater(sensory.leg_taste, 0.0, 'Leg taste must be detected near food')
        self.assertGreater(sensory.pam_reward, 0.0, 'Appetitive PAM reward must be evoked by sugar')

    def test_six_leg_contacts(self):
        eco_mgr = EcosystemSensoryManager()
        sensory, _, _ = eco_mgr.compute_sensory_input(
            fly_pos=Vec3(0, 0, 0.3),
            fly_yaw=0.0,
            terrain_dist_l=40.0, terrain_dist_c=40.0, terrain_dist_r=40.0,
            foods=[], frogs=[],
            surface_z=0.0, surface_type='GROUND',
            locomotion_mode='GROUNDED'
        )
        self.assertEqual(len(sensory.leg_contacts), 6)
        self.assertTrue(all(sensory.leg_contacts), 'All 6 legs should contact ground when grounded flat')


class TestProboscisFeeding(unittest.TestCase):
    def test_proboscis_extension_decoder(self):
        decoder = MotorDecoder()
        motor = decoder.decode(feeding_pop_hz=5.0, fwd_pop_hz=0.0)
        self.assertGreater(motor.proboscis_extension, 0.5, 'High feeding pop rate must extend proboscis')
        self.assertEqual(motor.decision, 'FEEDING_PROBOSCIS_ACTIVE')

    def test_energy_replenishment_during_feeding(self):
        state = InternalPhysiologicalState(energy=0.3)
        initial_e = state.energy
        state.update(dt=2.0, locomotion_mode='GROUNDED', speed=0.0, feeding_activity=1.0)
        self.assertGreater(state.energy, initial_e, 'Energy must increase during active feeding')


class TestMemoryPlasticity(unittest.TestCase):
    def setUp(self):
        self.kc_idx = np.arange(100, dtype=np.int32)
        self.mbon_idx = np.arange(10, dtype=np.int32)
        self.pam_idx = np.array([200, 201], dtype=np.int32)
        self.ppl1_idx = np.array([300, 301], dtype=np.int32)
        self.mem = MushroomBodyMemorySystem(
            self.kc_idx, self.mbon_idx, self.pam_idx, self.ppl1_idx,
            memory_path='memory/test_synapses.npz'
        )

    def tearDown(self):
        p = Path('memory/test_synapses.npz')
        if p.exists():
            p.unlink()

    def test_3factor_learning_rule(self):
        active_kc = np.array([0, 1, 2], dtype=np.int32)
        self.mem.update_activity_trace(set(active_kc), dt=0.02)
        base_app, base_av = self.mem.compute_learned_mbon_drive(active_kc)

        self.mem.apply_reinforcement(pam_reward=1.0, ppl1_punishment=0.0)
        app_drive, _ = self.mem.compute_learned_mbon_drive(active_kc)

        self.assertGreater(app_drive, base_app, 'PAM reward must strengthen KC->appetitive MBON synapses')
        self.assertGreater(self.mem.associations_count, 0)

        threat_kc = np.array([10, 11], dtype=np.int32)
        self.mem.update_activity_trace(set(threat_kc), dt=0.02)
        _, base_av2 = self.mem.compute_learned_mbon_drive(threat_kc)

        self.mem.apply_reinforcement(pam_reward=0.0, ppl1_punishment=1.0)
        _, av_drive2 = self.mem.compute_learned_mbon_drive(threat_kc)

        self.assertGreater(av_drive2, base_av2, 'PPL1 punishment must strengthen KC->aversive MBON synapses')


class TestMemoryPersistenceRetry(unittest.TestCase):
    def test_save_and_load_persistence(self):
        test_path = Path('memory/test_persist.npz')
        if test_path.exists():
            test_path.unlink()

        kc_idx = np.arange(50, dtype=np.int32)
        mbon_idx = np.arange(8, dtype=np.int32)
        pam_idx = np.array([100], dtype=np.int32)
        ppl1_idx = np.array([200], dtype=np.int32)

        mem1 = MushroomBodyMemorySystem(kc_idx, mbon_idx, pam_idx, ppl1_idx, memory_path=test_path)
        mem1.update_activity_trace({0, 1, 2}, dt=0.02)
        mem1.apply_reinforcement(pam_reward=1.0, ppl1_punishment=0.0)
        mem1.save()

        self.assertTrue(test_path.exists())
        size_bytes = test_path.stat().st_size
        self.assertLess(size_bytes, 2 * 1024 * 1024 * 1024, 'Storage limit must be strictly under 2 GB')

        mem2 = MushroomBodyMemorySystem(kc_idx, mbon_idx, pam_idx, ppl1_idx, memory_path=test_path)
        self.assertEqual(mem2.associations_count, mem1.associations_count)
        self.assertTrue(np.allclose(mem2.weights, mem1.weights))

        test_path.unlink()


class TestFrogPredatorAndHysteresis(unittest.TestCase):
    def test_frog_encounter_hysteresis(self):
        root = NodePath('FrogTestRoot')
        frog = FrogEntity(root, 'TestFrog', Vec3(0, 0, 0), scale=1.0)

        fly_pos_close = Vec3(10.0, 0, 0)
        fly_pos_far = Vec3(35.0, 0, 0)

        self.assertTrue(frog.check_encounter(fly_pos_close), 'First entry into proximity must count encounter')

        for _ in range(50):
            self.assertFalse(frog.check_encounter(fly_pos_close), 'Continuous proximity must NOT recount encounter')

        self.assertFalse(frog.check_encounter(fly_pos_far))
        self.assertTrue(frog.check_encounter(fly_pos_close), 'Re-entering proximity after leaving must count new encounter')

    def test_frog_physical_tongue_collision(self):
        root = NodePath('FrogTestRoot2')
        frog = FrogEntity(root, 'TestFrog2', Vec3(0, 0, 0), scale=1.0)

        frog.state = 'TONGUE_STRIKE'
        frog.tongue_timer = 0.20

        far_fly = Vec3(15.0, 0, 0)
        caught_far = frog.update(dt=0.02, fly_pos=far_fly)
        self.assertFalse(caught_far, 'Fly out of reach must not be caught')

        close_fly = Vec3(0.0, 3.0, 0.8)
        frog.tongue_target = Vec3(close_fly)
        caught_close = frog.update(dt=0.02, fly_pos=close_fly)
        self.assertTrue(caught_close or frog.physical_hit, 'Fly at tongue tip during strike must be caught')


class TestLandingAndWalking(unittest.TestCase):
    def test_dnp02_landing_readiness_decoder(self):
        decoder = MotorDecoder()
        motor = decoder.decode(landing_pop_hz=4.5)
        self.assertGreater(motor.landing_readiness, 0.5, 'DNp02 population firing must yield landing readiness')

    def test_tripod_walking_animation(self):
        root = NodePath('FlyModelRoot')
        model = FlyModel(root, scale=1.0)
        model.animate(dt=0.1, flying=False, speed=2.0)
        pitches = [p.getP() for p, _ in model.legs]
        self.assertNotEqual(pitches[0], pitches[1], 'Opposing tripod leg sets must swing with opposite phase')


if __name__ == '__main__':
    unittest.main()