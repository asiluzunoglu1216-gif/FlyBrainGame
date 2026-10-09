"""Main Game Application for FlyBrainGame: "Bir Sineğin Günü".

Powered by Panda3D and the 166,700-neuron Drosophila MaleCNS v1.0 connectome.
Features:
- Large 240x240 living natural ecosystem (meadow, hills, pond, trees, rocks)
- Moving frog predators (Kermit, Bullfrog, Treefrog) with AI state machine
- Food system with floating 3D labels and 60-second respawns
- Emergent perching and landing on ground, rocks, and branches
- Minecraft spectator camera (WASD, Space, Shift, Mouse look) & Chase camera ([F] toggle)
- Dynamic biological sensory injection into LC4/LPLC2 (looming) and LC10a (target tracking)
- Game Over screen with Life Summary and Reincarnation / Retry ([R])
"""
from __future__ import annotations

import sys
import math
import random
from typing import List
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    loadPrcFileData, AmbientLight, DirectionalLight, Vec3, Vec4,
    ClockObject
)

from .brain_worker import BrainWorker
from .natural_world import NaturalWorld
from .food_system import FoodSystem
from .frog_entity import FrogEntity
from .ecosystem_sensory import EcosystemSensoryManager
from .camera_controller import CameraController
from .fly_controller import FlyController
from .hud import DebugHUD
from .game_over_ui import GameOverUI
from .odor_system import OdorEcosystemManager


class FlyBrainApp(ShowBase):
    def __init__(self, headless: bool = False, max_test_frames: int = 0, synchronous_brain: bool = False):
        if headless:
            loadPrcFileData("", "window-type none")
            loadPrcFileData("", "audio-library-name null")
        else:
            loadPrcFileData("", "window-title FlyBrainGame: Bir Sinegin Gunu - Drosophila Connectome 3D")
            loadPrcFileData("", "win-size 1280 720")
            loadPrcFileData("", "sync-video true")

        super().__init__()

        self.headless = headless
        self.max_test_frames = max_test_frames
        self.synchronous_brain = synchronous_brain
        self.frame_count = 0
        self.game_time = 0.0
        self.game_over = False

        # Natural daylight sky background
        self.setBackgroundColor(0.48, 0.68, 0.88, 1.0)

        # 1. Setup Natural Sunlight and Sky Ambience
        self._setup_lighting()

        # 2. Initialize Decoupled Connectome Brain Worker
        if self.synchronous_brain:
            print("[FlyBrainApp] Initializing synchronous unthreaded BrainWorker for accelerated simulation...")
            self.brain_worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=True, threaded=False, paced=False)
        else:
            print("[FlyBrainApp] Starting BrainWorker background thread...")
            self.brain_worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=True, threaded=True, paced=True)
        self.brain_worker.start()

        # 3. Build Large Living Natural World (240x240 units)
        self.world = NaturalWorld(self.render, world_size=240.0, world_height=45.0)

        # 4. Build Food System (active fruits with floating 3D labels)
        self.food_system = FoodSystem(self.render, max_active=5)

        # 5. Build 3D Spatial Odor Dispersion System
        self.odor_system = OdorEcosystemManager(self.render)

        # 6. Build Frog Predators around water / rocks
        # PRESENTATION_MODE: Frogs start at safe distance (40+ units) from fly spawn
        self.frogs: List[FrogEntity] = [
            FrogEntity(self.render, "Kermit_Pond", Vec3(-45.0, -50.0, 0.5), scale=1.7),
            FrogEntity(self.render, "Bullfrog_Marsh", Vec3(-55.0, -60.0, 0.5), scale=1.9),
            FrogEntity(self.render, "Treefrog_Rock", Vec3(45.0, -55.0, 0.5), scale=1.5),
        ]

        # 7. Build Ecosystem Sensory Manager
        self.sensory_mgr = EcosystemSensoryManager(max_sensor_range=45.0)

        # 8. Build Fly Entity and Controller
        self.fly = FlyController(self.render, self.world, self.brain_worker)

        # 9. Camera Controller (Chase + Minecraft-style Spectator)
        self.disableMouse()
        self.cam_ctrl = CameraController(self, self.fly.node) if not headless else None

        # 10. Game Over UI
        self.game_over_ui = GameOverUI(self._on_retry) if not headless else None

        # 11. Neurobiological Debug HUD
        self.hud = DebugHUD() if not headless else None

        # 12. Register Keybindings
        self.accept("f1", self._on_key_f1)
        self.accept("f2", self._on_key_f2)
        self.accept("f3", self._on_key_f3)
        self.accept("f4", self._on_key_f4)
        self.accept("space", self._on_key_space)
        self.accept("r", self._on_key_r)
        self.accept("escape", self.cleanup_and_exit)

        # 13. Add Main Simulation Loop Task
        self.taskMgr.add(self.update_game, "FlyGameUpdateTask")

        print("[FlyBrainApp] Living Ecosystem initialized successfully!")

    def _setup_lighting(self):
        ambient = AmbientLight("ambient_light")
        ambient.setColor(Vec4(0.45, 0.48, 0.52, 1.0))
        amb_np = self.render.attachNewNode(ambient)
        self.render.setLight(amb_np)

        sun = DirectionalLight("sun_light")
        sun.setColor(Vec4(0.92, 0.90, 0.82, 1.0))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-40, -50, 0)
        self.render.setLight(sun_np)

    def _on_key_f1(self):
        print("[Mode] Switched to F1: CONNECTOME CONTROL (166,700-neuron MaleCNS)")
        self.fly.set_mode("CONNECTOME")

    def _on_key_f2(self):
        print("[Mode] Switched to F2: SCRIPTED BASELINE BOT")
        self.fly.set_mode("SCRIPTED_BOT")

    def _on_key_f3(self):
        cur = self.brain_worker.sensory_mode
        nxt = "EYE_MODE" if cur == "FEATURE_MODE" else "FEATURE_MODE"
        print(f"[Sensory] Toggled mode to: {nxt}")
        self.brain_worker.set_sensory_mode(nxt)

    def _on_key_f4(self):
        if self.hud:
            self.hud.toggle_detailed_mode()

    def _on_key_space(self):
        if self.cam_ctrl and self.cam_ctrl.mode == "SPECTATOR":
            return
        print("[Fly] Repositioning fly to safe clearing...")
        self.fly.reset_position()

    def _on_key_r(self):
        if self.game_over:
            self._on_retry()

    def _on_retry(self):
        print("[FlyBrainApp] REINCARNATION: Saving memory, resetting world, fly, frogs, and connectome...")
        self.game_over = False
        if self.game_over_ui:
            self.game_over_ui.hide()

        # Save and retain learned associative plasticity in plastic_synapses.npz
        self.brain_worker.save_memory()
        self.brain_worker.load_memory()

        self.fly.reset_life_stats()
        for frog in self.frogs:
            frog.reset()
        self.food_system.reset_all()

        # Cleanly reset connectome activation states with new seed
        self.brain_worker.reset_brain(seed=random.randint(1, 100000))
        self.brain_worker.set_paused(False)

    def update_game(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        dt = min(0.05, max(0.001, dt))
        self.game_time += dt

        if self.game_over:
            if self.cam_ctrl and not self.headless:
                self.cam_ctrl.update(dt, self.fly.pos, self.fly.yaw)
            return task.cont

        # 1. Update Food System & 3D Spatial Odor Dispersion
        self.food_system.update(dt, self.game_time)
        self.odor_system.sync_from_food_system(self.food_system.foods)
        self.odor_system.update(dt)
        active_foods = self.food_system.get_active_foods()

        # 2. Update Frog Predators AI & Attacks with Hysteresis Encounters
        frogs_data = []
        fly_caught = False
        cause_of_death = "NONE"

        for frog in self.frogs:
            # Hysteresis: count once when frog begins engagement (WATCH/AIM/STRIKE)
            if frog.check_encounter(self.fly.pos):
                self.fly.frog_encounters += 1

            caught = frog.update(dt, self.fly.pos)
            frogs_data.append((frog.name, frog.pos, frog.velocity))
            if caught:
                fly_caught = True
                cause_of_death = "FROG"
                # Invariant: If caught by frog, frog_encounters MUST be >= 1
                self.fly.frog_encounters = max(1, self.fly.frog_encounters)

        # Check starvation
        if self.fly.internal_state.energy <= 0.0 and not fly_caught:
            fly_caught = True
            cause_of_death = "STARVATION"
            print("[Game] [*] FLY STARVED TO DEATH (Energy reached 0.0)!")

        if fly_caught:
            print(f"[Game] [*] FLY LIFE CYCLE ENDED ({cause_of_death})! Saving memory and showing Life Summary...")
            self.game_over = True
            self.brain_worker.save_memory()
            self.brain_worker.set_paused(True)
            telem = self.brain_worker.get_telemetry()
            if self.game_over_ui:
                self.game_over_ui.show(
                    cause=cause_of_death,
                    alive_time=self.fly.alive_time,
                    food_eaten=self.fly.food_eaten,
                    distance=self.fly.distance_travelled,
                    landings=self.fly.total_landings,
                    encounters=self.fly.frog_encounters,
                    escapes=self.fly.frog_escapes,
                    associations=telem.memory_associations
                )
            return task.cont

        # 3. Raycasts against Natural Terrain & Obstacles
        rad = math.radians(self.fly.yaw)
        fwd = Vec3(math.cos(rad), math.sin(rad), 0.0)
        left_rad = math.radians(self.fly.yaw + 35.0)
        l_fwd = Vec3(math.cos(left_rad), math.sin(left_rad), 0.0)
        right_rad = math.radians(self.fly.yaw - 35.0)
        r_fwd = Vec3(math.cos(right_rad), math.sin(right_rad), 0.0)

        max_sensor_range = 40.0
        dist_c = self.world.raycast(self.fly.pos, fwd, max_sensor_range)
        dist_l = self.world.raycast(self.fly.pos, l_fwd, max_sensor_range)
        dist_r = self.world.raycast(self.fly.pos, r_fwd, max_sensor_range)

        # 4. Ecosystem Sensory Manager -> Multisensory Connectome Inputs
        surface_z, surface_type = self.world.get_surface_below(self.fly.pos)
        sensory, nearest_food_name, frog_threat = self.sensory_mgr.compute_sensory_input(
            fly_pos=self.fly.pos,
            fly_yaw=self.fly.yaw,
            terrain_dist_l=dist_l,
            terrain_dist_c=dist_c,
            terrain_dist_r=dist_r,
            foods=active_foods,
            frogs=frogs_data,
            fallback_active=self.fly.fallback_active,
            fly_speed=self.fly._current_speed,
            current_time=self.game_time,
            surface_z=surface_z,
            surface_type=surface_type,
            locomotion_mode=self.fly.locomotion_mode,
            odor_manager=self.odor_system,
            internal_state=self.fly.internal_state,
            pitch=self.fly.pitch,
            roll=self.fly.roll
        )

        # Track successful escape when threat active and fly accelerating away
        if frog_threat and self.fly._vertical_vel > 2.0:
            self.fly.frog_escapes += 1

        # 5. Update Fly Controller (passes sensory to brain, updates physics & landing)
        if self.synchronous_brain:
            self.brain_worker.step_once(sensory)
        self.fly.update(dt, custom_sensory=sensory)

        # 6. Check Feeding Interaction (proboscis tip collider overlapping food collider)
        prob_extended = (self.fly.model.proboscis_extension > 0.15 or self.fly.control_mode != "CONNECTOME")
        tip_pos = self.fly.get_proboscis_tip_pos()
        food_eaten = self.food_system.check_feeding(
            self.fly.pos,
            self.fly.is_landed,
            self.game_time,
            proboscis_tip_pos=tip_pos,
            proboscis_extended=prob_extended,
            proboscis_extension=self.fly.model.proboscis_extension
        )
        if food_eaten:
            self.fly.food_eaten += 1
            self.fly.internal_state.energy = min(1.0, self.fly.internal_state.energy + 0.35)
            self.fly.internal_state.total_energy_consumed += 0.35
            print(f"[FoodSystem] [*] Fly completed feeding on {food_eaten}! Total eaten: {self.fly.food_eaten}, Energy: {self.fly.internal_state.energy:.2f}")
            if self.hud:
                self.hud.trigger_food_eaten_banner(food_eaten)

        # 7. Update Camera
        if self.cam_ctrl and not self.headless:
            self.cam_ctrl.update(dt, self.fly.pos, self.fly.yaw)

        # 8. Update HUD
        if self.hud:
            fps = ClockObject.getGlobalClock().getAverageFrameRate()
            telem = self.brain_worker.get_telemetry()
            cam_mode = self.cam_ctrl.mode if self.cam_ctrl else "HEADLESS"
            self.hud.update(
                fps=fps,
                telem=telem,
                control_mode=self.fly.control_mode,
                fallback_active=self.fly.fallback_active,
                fly_controller=self.fly,
                cam_mode=cam_mode,
                nearest_food=nearest_food_name
            )

        self.frame_count += 1
        if self.max_test_frames > 0 and self.frame_count >= self.max_test_frames:
            print(f"[FlyBrainApp] Reached max test frames ({self.frame_count}). Exiting.")
            self.cleanup_and_exit()
            return task.done

        return task.cont

    def cleanup_and_exit(self):
        print("[FlyBrainApp] Shutting down connectome worker...")
        self.brain_worker.stop()
        sys.exit(0)


def main():
    headless = "--headless" in sys.argv
    max_frames = 0
    for i, arg in enumerate(sys.argv):
        if arg == "--test-frames" and i + 1 < len(sys.argv):
            max_frames = int(sys.argv[i + 1])

    app = FlyBrainApp(headless=headless, max_test_frames=max_frames)
    app.run()


if __name__ == "__main__":
    main()
