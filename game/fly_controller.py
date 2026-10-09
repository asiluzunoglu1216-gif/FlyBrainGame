"""Fly Controller: Sensory Raycasting, Flight Dynamics, Landing, and A/B Control Modes.

Modes:
- F1: CONNECTOME - Pure connectome-driven flight. Sensory inputs inject into LC4/LPLC2/LC10a;
                  flight is steered purely by DNa02, DNp01, DNg100, MDN readouts.
- F2: SCRIPTED_BOT - Algorithmic rule-based baseline bot for A/B comparison.

Emergent Landing & Perching Physics:
- Physical contact + DNp02 landing readiness triggers natural landing on ground, rocks, branches, foods.
- Wings fold during perching; tripod walking gait is animated; take-off occurs when connectome generates forward drive or escape.
"""
from __future__ import annotations

import math
from typing import Optional, List, Tuple
from panda3d.core import NodePath, Vec3
from .fly_model import FlyModel
from .brain_worker import BrainWorker
from .sensory_encoder import SensoryInput
from .motor_decoder import MotorState
from .internal_state import InternalPhysiologicalState


class FlyController:
    def __init__(self, render: NodePath, env, brain_worker: BrainWorker):
        self.render = render
        self.env = env
        self.brain = brain_worker

        # Flight Node & Model
        self.node = render.attachNewNode("FlyEntity")
        self.model = FlyModel(self.node, scale=1.0)

        # Internal physiological state (energy, hunger, hydration)
        self.internal_state = InternalPhysiologicalState()

        # Initial pose (PRESENTATION_MODE: Open meadow clearing, meadow flight layer)
        self.pos = Vec3(0.0, 0.0, 3.0)
        self.yaw = 50.0     # Heading towards open meadow and visible food
        self.pitch = 0.0
        self.roll = 0.0
        self.node.setPos(self.pos)
        self.node.setHpr(self.yaw - 90.0, 0, 0)

        # Control mode: "CONNECTOME" (F1) or "SCRIPTED_BOT" (F2)
        self.control_mode = "CONNECTOME"

        # Fallback safeguard status
        self.fallback_active = False

        # Locomotion & Landing state
        self.locomotion_mode = "AIRBORNE"  # "AIRBORNE" or "GROUNDED"
        self.current_surface = "AIR"
        self.landing_state_label = "AIRBORNE"

        # Life statistics
        self.alive_time = 0.0
        self.food_eaten = 0
        self.distance_travelled = 0.0
        self.total_landings = 0
        self.frog_encounters = 0
        self.frog_escapes = 0

        # Internal motion smoothing
        self._current_speed = 0.0
        self._current_turn_rate = 0.0
        self._vertical_vel = 0.0
        self._prev_pos = Vec3(self.pos)

    @property
    def is_landed(self) -> bool:
        return self.locomotion_mode == "GROUNDED"

    @is_landed.setter
    def is_landed(self, value: bool):
        self.locomotion_mode = "GROUNDED" if value else "AIRBORNE"
        self.landing_state_label = "PHYSICS-ASSISTED LANDING (Surface Contact)" if value else "AIRBORNE"

    def reset_position(self):
        """Resets fly to safe center starting location (PRESENTATION_MODE)."""
        self.pos = Vec3(0.0, 0.0, 3.0)
        self.yaw = 50.0
        self.pitch = 0.0
        self.roll = 0.0
        self._vertical_vel = 0.0
        self._current_speed = 0.0
        self._current_turn_rate = 0.0
        self.locomotion_mode = "AIRBORNE"
        self.current_surface = "AIR"
        self.landing_state_label = "AIRBORNE"
        self._prev_pos = Vec3(self.pos)
        self.node.setPos(self.pos)
        self.node.setHpr(self.yaw - 90.0, 0, 0)

    def reset_life_stats(self):
        """Resets life telemetry and internal physiological state for reincarnated run."""
        self.alive_time = 0.0
        self.food_eaten = 0
        self.distance_travelled = 0.0
        self.total_landings = 0
        self.frog_encounters = 0
        self.frog_escapes = 0
        self.internal_state.reset_for_retry()
        self.reset_position()

    def set_mode(self, mode: str):
        """Switches between CONNECTOME (F1) and SCRIPTED_BOT (F2)."""
        if mode in ("CONNECTOME", "SCRIPTED_BOT"):
            self.control_mode = mode
            self.brain.set_connectome_enabled(mode == "CONNECTOME")

    def _get_forward_vec(self, yaw_deg: float) -> Vec3:
        rad = math.radians(yaw_deg)
        return Vec3(math.cos(rad), math.sin(rad), 0.0)

    def get_proboscis_tip_pos(self) -> Vec3:
        """Returns exact world position of the proboscis tip (labellum)."""
        if self.model and hasattr(self.model, "labellum"):
            try:
                return self.model.labellum.getPos(self.render)
            except Exception:
                pass
        # Analytical forward kinematics fallback:
        rad = math.radians(self.yaw)
        fwd = Vec3(math.cos(rad), math.sin(rad), 0.0)
        ext = getattr(self.model, "proboscis_extension", 0.0)
        # Proboscis extends forward (+Y) and downward (-Z)
        tip_local_fwd = 1.169 + ext * 0.445
        tip_local_z = -0.819 - ext * 0.517
        return Vec3(
            self.pos.x + fwd.x * tip_local_fwd,
            self.pos.y + fwd.y * tip_local_fwd,
            self.pos.z + tip_local_z
        )

    def update(self, dt: float, custom_sensory: Optional[SensoryInput] = None):
        self.alive_time += dt

        # 1. Sensory Input Processing
        if custom_sensory is not None:
            sensory = custom_sensory
        else:
            # Fallback direct raycasts if no ecosystem manager provided
            fwd = self._get_forward_vec(self.yaw)
            left_dir = self._get_forward_vec(self.yaw + 35.0)
            right_dir = self._get_forward_vec(self.yaw - 35.0)

            max_sensor_range = 35.0
            dist_c = self.env.raycast(self.pos, fwd, max_dist=max_sensor_range)
            dist_l = self.env.raycast(self.pos, left_dir, max_dist=max_sensor_range)
            dist_r = self.env.raycast(self.pos, right_dir, max_dist=max_sensor_range)

            target_pos = self.env.get_target_pos() if hasattr(self.env, "get_target_pos") else Vec3(0, 0, 8)
            to_target = target_pos - self.pos
            target_dist = to_target.length()

            target_angle_deg = math.degrees(math.atan2(to_target.y, to_target.x))
            angle_diff = (target_angle_deg - self.yaw + 180.0) % 360.0 - 180.0
            target_azimuth = float(max(-1.0, min(1.0, -angle_diff / 90.0)))
            target_visible = abs(angle_diff) < 110.0

            optic_flow = (self._current_speed / max(3.0, dist_c)) if self._current_speed > 0.01 else 0.0
            sensory = SensoryInput(
                dist_left=dist_l,
                dist_center=dist_c,
                dist_right=dist_r,
                max_range=max_sensor_range,
                target_visible=target_visible,
                target_azimuth=target_azimuth,
                target_dist=target_dist,
                optic_flow=optic_flow,
                fallback_active=self.fallback_active
            )

        # Forward sensory input to brain worker
        self.brain.update_sensory(sensory)

        # 2. Motor Decoded Commands
        turn_rate = 0.0
        speed = 0.0
        escape_impulse = 0.0
        landing_readiness = 0.0
        proboscis_ext = 0.0
        flight_power_hz = 0.0
        esc_pop_hz = 0.0
        fwd_pop_hz = 0.0

        is_grooming = False
        if self.control_mode == "CONNECTOME":
            # PURE CONNECTOME: Decoded directly from descending neurons (DNa02, DNp01, DNg100, MDN, DNp02, CEM, DNg12)
            telem = self.brain.get_telemetry()
            motor = telem.motor
            turn_rate = motor.turn_rate
            speed = motor.forward_speed
            escape_impulse = motor.escape_impulse
            landing_readiness = motor.landing_readiness
            proboscis_ext = motor.proboscis_extension
            is_grooming = motor.is_grooming
            flight_power_hz = motor.flight_power_hz
            esc_pop_hz = motor.esc_pop_hz
            fwd_pop_hz = motor.fwd_pop_hz

            # Articulate 3D fly proboscis
            self.model.set_proboscis_extension(proboscis_ext)
        else:
            # SCRIPTED BASELINE BOT (F2) for A/B comparison
            dist_l = sensory.dist_left
            dist_r = sensory.dist_right
            dist_c = sensory.dist_center
            if dist_l < 14.0 and dist_l < dist_r:
                turn_rate = -75.0
            elif dist_r < 14.0 and dist_r < dist_l:
                turn_rate = 75.0
            elif dist_c < 16.0:
                turn_rate = 90.0
            elif sensory.target_visible and sensory.target_dist < 30.0:
                turn_rate = max(-60.0, min(60.0, sensory.target_azimuth * 60.0))
            speed = 8.5

        # Update Internal Physiological State (feeding active on food contact with proboscis extension)
        feeding_active = proboscis_ext if (self.is_landed and (sensory.taste_sugar > 0.0 or sensory.leg_taste > 0.15)) else 0.0
        self.internal_state.update(
            dt=dt,
            locomotion_mode=self.locomotion_mode,
            speed=self._current_speed,
            feeding_activity=feeding_active
        )

        # 3. Landing & Surface Interaction
        surface_z = 0.0
        surface_type = "GROUND"
        if hasattr(self.env, "get_surface_below"):
            surface_z, surface_type = self.env.get_surface_below(self.pos)

        # If sensory detected food substrate contact or perch surface:
        if sensory.surface_contact and sensory.surface_type.startswith("FOOD_"):
            surface_z = max(surface_z, sensory.target_pos.z)
            surface_type = sensory.surface_type

        h_above_surface = max(0.0, self.pos.z - surface_z)

        if self.locomotion_mode == "GROUNDED":
            # Pure neural takeoff: Takeoff is triggered strictly by validated neural flight/escape populations:
            # 1. DNp01 Giant Fiber escape jump (escape_impulse > 1.0 or esc_pop_hz > 6.0)
            # 2. DLMn/DVMn flight power motor neuron activation (flight_power_hz > 3.5 or strong flight initiation fwd_pop_hz > 4.5 and flight_power_hz > 1.5)
            # Generic forward speed threshold (speed > 4.8) is REMOVED.
            # Normal walking speed must NEVER automatically launch the fly.
            if self.control_mode == "CONNECTOME":
                neural_takeoff = (
                    escape_impulse > 1.0 or
                    esc_pop_hz > 6.0 or
                    flight_power_hz > 3.5 or
                    (fwd_pop_hz > 4.5 and flight_power_hz > 1.5)
                )
            else:
                neural_takeoff = (escape_impulse > 1.0 or speed > 8.0)

            if neural_takeoff:
                self.locomotion_mode = "AIRBORNE"
                self.current_surface = "AIR"
                self.landing_state_label = "AIRBORNE"
                self._vertical_vel = 3.0 + escape_impulse * 0.35
            else:
                # Grounded state: Walking / Perching
                # Biological taste arrest: feeding and proboscis extension suppress forward walking (Mann et al. 2013)
                if proboscis_ext > 0.15 or sensory.taste_sugar > 0.10:
                    walk_speed = 0.0
                else:
                    walk_speed = speed * 0.40
                self._current_speed += (walk_speed - self._current_speed) * min(1.0, dt * 10.0)

                # Ground steering: pure heading adjustment without roll
                self._current_turn_rate += (turn_rate - self._current_turn_rate) * min(1.0, dt * 12.0)
                self.yaw += self._current_turn_rate * dt
                self.yaw = (self.yaw + 360.0) % 360.0

                # Displace along ground surface
                move_dir = self._get_forward_vec(self.yaw)
                self.pos.x += move_dir.x * self._current_speed * dt
                self.pos.y += move_dir.y * self._current_speed * dt
                self.pos.z = surface_z + 0.3
                self._vertical_vel = 0.0

                # Track distance
                disp = (self.pos - self._prev_pos).length()
                self.distance_travelled += disp
                self._prev_pos = Vec3(self.pos)

                # Animate 6 articulated legs with tripod gait or grooming
                self.model.animate(dt, flying=False, speed=self._current_speed, grooming=is_grooming)
                self.node.setPos(self.pos)
                self.node.setHpr(self.yaw - 90.0, 0, 0)
                return

        # AIRBORNE mode: Check for natural touchdown
        # Triggered when close to surface and either DNp02 landing population fires or physical contact occurs
        is_touchdown = (h_above_surface <= 0.65 or sensory.surface_contact) and self._vertical_vel <= 0.50 and (
            landing_readiness > 0.12 or sensory.surface_contact or (speed < 5.0 and h_above_surface <= 0.55)
        )
        if is_touchdown:
            self.locomotion_mode = "GROUNDED"
            self.current_surface = surface_type
            if landing_readiness > 0.12:
                self.landing_state_label = "CONNECTOME LANDING (DNp02 Activated)"
            else:
                self.landing_state_label = "PHYSICS-ASSISTED LANDING (Surface Contact)"
            self.total_landings += 1
            self.pos.z = surface_z + 0.3
            self._vertical_vel = 0.0
            self._current_speed = 0.0
            self.model.animate(dt, flying=False, speed=0.0)
            self.node.setPos(self.pos)
            self.node.setHpr(self.yaw - 90.0, 0, 0)
            return

        # 4. Integrate Airborne Flight Physics with Natural Aerodynamic Balance
        self._current_turn_rate += (turn_rate - self._current_turn_rate) * min(1.0, dt * 10.0)
        self._current_speed += (speed - self._current_speed) * min(1.0, dt * 8.0)

        # Heading (yaw) update
        self.yaw += self._current_turn_rate * dt
        self.yaw = (self.yaw + 360.0) % 360.0

        room_h = getattr(self.env, "world_height", getattr(self.env, "room_height", 28.0))

        # Natural Drosophila altitude dynamics (ventral optic flow ground clearance regulation):
        # Flies naturally cruise in the meadow layer (1.5 - 2.5m above ground/perch surfaces).
        target_clearance = 2.0  # meters above surface
        clearance_err = target_clearance - h_above_surface
        # Gentle natural correction towards meadow cruising layer:
        self._vertical_vel += clearance_err * 0.75 * dt

        # Visual target downward glide: when tracking a food/perch below the fly,
        # visual alignment naturally produces gentle descent towards the target substrate
        if sensory.target_visible and sensory.target_dist < 35.0:
            target_pos = getattr(sensory, "target_pos", Vec3(0, 0, 1.0))
            target_dz = target_pos.z - self.pos.z
            if target_dz < -0.2:
                glide_bias = max(-1.8, target_dz * 0.35)
                self._vertical_vel += glide_bias * dt

        # Landing deceleration: DNp02 activation settles fly downward towards surface
        if landing_readiness > 0.08 and h_above_surface < 3.2:
            self._vertical_vel -= landing_readiness * 2.0 * dt

        # Ceiling proximity check: suppress upward escape lift and exert downward force near ceiling
        dist_to_ceil = room_h - self.pos.z
        if dist_to_ceil < 6.0:
            ceil_factor = max(0.0, min(1.0, (dist_to_ceil - 2.0) / 4.0))
            escape_impulse *= ceil_factor
            alt_err = (room_h - 3.5) - self.pos.z
            self._vertical_vel += alt_err * 2.5 * dt

        # Apply escape vertical lift (significant only on bilateral/head-on looming)
        if escape_impulse > 0.0:
            self._vertical_vel = max(self._vertical_vel, escape_impulse * 0.35)

        # Aerodynamic vertical damping
        self._vertical_vel *= 0.85

        # Forward displacement
        move_dir = self._get_forward_vec(self.yaw)
        self.pos.x += move_dir.x * self._current_speed * dt
        self.pos.y += move_dir.y * self._current_speed * dt
        self.pos.z += self._vertical_vel * dt

        # 5. Boundary Fallback Safeguard
        self.fallback_active = False
        limit = self.env.half_size - 3.0
        h_limit_low = surface_z + 0.3
        h_limit_high = room_h - 1.5

        if self.pos.x < -limit:
            self.pos.x = -limit
            self.yaw = 0.0
            self.fallback_active = True
        elif self.pos.x > limit:
            self.pos.x = limit
            self.yaw = 180.0
            self.fallback_active = True

        if self.pos.y < -limit:
            self.pos.y = -limit
            self.yaw = 90.0
            self.fallback_active = True
        elif self.pos.y > limit:
            self.pos.y = limit
            self.yaw = 270.0
            self.fallback_active = True

        if self.pos.z < h_limit_low:
            self.pos.z = h_limit_low
            self._vertical_vel = 1.0
            self.fallback_active = True
        elif self.pos.z > h_limit_high:
            self.pos.z = h_limit_high
            self._vertical_vel = -2.0
            self.fallback_active = True

        # Track trajectory distance
        disp = (self.pos - self._prev_pos).length()
        self.distance_travelled += disp
        self._prev_pos = Vec3(self.pos)

        # 6. Mesh banking and visual update
        target_roll = max(-30.0, min(30.0, -self._current_turn_rate * 0.35))
        self.roll += (target_roll - self.roll) * min(1.0, dt * 10.0)

        self.node.setPos(self.pos)
        self.node.setHpr(self.yaw - 90.0, 0, self.roll)

        # 7. Wingbeat animation
        self.model.animate(dt, flying=True)
