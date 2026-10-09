"""Ecosystem Sensory Interface.

Bridges the natural living environment (moving frogs, food targets, natural terrain, 3D odor plumes)
to the FlyBrain connectome sensory inputs.

Biologically Mapped Connectome Inputs:
- LC4 / LPLC2: Looming threats from approaching predators (Frogs) and obstacles (Trees/Rocks)
- LC10a: Visual object tracking towards prominent visual items (Food / Floating Fruits)
- ORN / ALPN: Bilateral 3D odor plume sampling across antennae with wind advection
- BM_Taste: Sucrose gustatory feeding response from labellum & leg contact
- LgLG / LgAG: 6 individual leg mechanosensory contacts (FL, FR, ML, MR, RL, RR)
- DNp02: Surface approach & landing deceleration circuit
- PAM / PPL1: Dopaminergic appetitive reward and aversive punishment
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Any
from panda3d.core import Vec3

from .sensory_encoder import SensoryInput
from .visual_system import VirtualCompoundEyeSystem
from .gustatory_system import GustatorySystem
from panda3d.core import Vec4


@dataclass
class EnvironmentalTarget:
    name: str
    pos: Vec3
    is_threat: bool = False     # True if predator (frog), False if neutral/food
    radius: float = 1.0
    velocity: Vec3 = Vec3(0, 0, 0)


class EcosystemSensoryManager:
    """Manages sensory conversion from the dynamic ecosystem into Connectome SensoryInput."""

    def __init__(self, max_sensor_range: float = 40.0):
        self.max_sensor_range = max_sensor_range
        self.prev_frog_dists: dict[str, float] = {}
        self.visual_system = VirtualCompoundEyeSystem(fov_deg=220.0)
        self.gustatory_system = GustatorySystem()
        self.prev_time: float = 0.0

    def compute_sensory_input(
        self,
        fly_pos: Vec3,
        fly_yaw: float,
        terrain_dist_l: float,
        terrain_dist_c: float,
        terrain_dist_r: float,
        foods: List[Tuple[str, Vec3]],
        frogs: List[Tuple[str, Vec3, Vec3]],  # (name, pos, velocity)
        fallback_active: bool = False,
        fly_speed: float = 0.0,
        current_time: float = 0.0,
        ambient_wind: bool = True,
        surface_z: float = 0.0,
        surface_type: str = "GROUND",
        locomotion_mode: str = "AIRBORNE",
        odor_manager: Optional[Any] = None,
        internal_state: Optional[Any] = None,
        pitch: float = 0.0,
        roll: float = 0.0
    ) -> Tuple[SensoryInput, Optional[str], bool]:
        """Calculates sensory input for the connectome.

        Returns:
            (SensoryInput, nearest_food_name, frog_threat_active)
        """
        rad = math.radians(fly_yaw)
        fly_fwd = Vec3(math.cos(rad), math.sin(rad), 0.0)

        # 1. Base terrain obstacle distances
        dist_l = min(terrain_dist_l, self.max_sensor_range)
        dist_c = min(terrain_dist_c, self.max_sensor_range)
        dist_r = min(terrain_dist_r, self.max_sensor_range)

        # 2. Predator (Frog) Detection -> Generates dynamic looming on LC4 / LPLC2
        frog_threat_active = False
        frog_looming = 0.0
        ppl1_punish = 0.0

        for name, frog_pos, frog_vel in frogs:
            to_frog = frog_pos - fly_pos
            frog_dist = to_frog.length()
            if frog_dist > self.max_sensor_range:
                self.prev_frog_dists[name] = frog_dist
                continue

            frog_angle_deg = math.degrees(math.atan2(to_frog.y, to_frog.x))
            angle_diff = (frog_angle_deg - fly_yaw + 180.0) % 360.0 - 180.0

            # Only visible within fly's ~220 degree field of view
            if abs(angle_diff) < 110.0:
                frog_threat_active = True
                is_charging = frog_vel.length() > 0.5
                if frog_dist < 22.0 or is_charging:
                    f_loom = max(0.0, 1.0 - frog_dist / 22.0)
                    frog_looming = max(frog_looming, f_loom)
                    dist_scale = 0.70 if is_charging else 0.85
                    if angle_diff < -15.0:
                        dist_r = min(dist_r, frog_dist * dist_scale)
                    elif angle_diff > 15.0:
                        dist_l = min(dist_l, frog_dist * dist_scale)
                    else:
                        dist_c = min(dist_c, frog_dist * (dist_scale * 0.85))

                # If frog is within critical attack range (< 8.0), trigger aversive PPL1 punishment
                if frog_dist < 8.0 or is_charging:
                    ppl1_punish = max(ppl1_punish, max(0.2, 1.0 - frog_dist / 8.0))

            self.prev_frog_dists[name] = frog_dist

        # 3. Visual Target (Food) Tracking -> Feeds into LC10a
        nearest_food_name = None
        closest_food_dist = 1e9
        target_azimuth = 0.0
        target_visible = False
        target_dist = 50.0
        target_pos = Vec3(0, 0, 1.0)

        for food_name, food_pos in foods:
            to_food = food_pos - fly_pos
            f_dist = to_food.length()
            if f_dist < closest_food_dist and f_dist < 38.0:
                f_angle_deg = math.degrees(math.atan2(to_food.y, to_food.x))
                f_diff = (f_angle_deg - fly_yaw + 180.0) % 360.0 - 180.0

                if abs(f_diff) < 95.0:
                    closest_food_dist = f_dist
                    nearest_food_name = food_name
                    target_visible = True
                    # Target on right (f_diff < 0) -> target_azimuth > 0 (stimulates lc10a_r -> steer_pop_r)
                    # Target on left (f_diff > 0) -> target_azimuth < 0 (stimulates lc10a_l -> steer_pop_l)
                    target_azimuth = float(max(-1.0, min(1.0, -f_diff / 80.0)))
                    target_dist = f_dist
                    target_pos = Vec3(food_pos)

        # 4. Retinal Optic Flow and Antennal Airspeed Computation
        optic_flow = (fly_speed / max(3.0, dist_c)) if fly_speed > 0.01 else 0.0

        env_motion = 0.0
        for _, f_pos, f_vel in frogs:
            f_speed = f_vel.length()
            if f_speed > 0.5:
                to_frog = f_pos - fly_pos
                f_dist = to_frog.length()
                if f_dist < self.max_sensor_range:
                    f_angle_deg = math.degrees(math.atan2(to_frog.y, to_frog.x))
                    f_diff = (f_angle_deg - fly_yaw + 180.0) % 360.0 - 180.0
                    if abs(f_diff) < 90.0:
                        motion_val = f_speed / max(2.0, f_dist)
                        optic_flow += motion_val
                        env_motion += motion_val

        # Ambient meadow breeze & relative airspeed
        ambient_breeze = 0.0
        wind_dir = Vec3(0.707, 0.707, 0.0)  # Gentle North-East breeze
        if ambient_wind and current_time > 0.0:
            ambient_breeze = 1.0 + 0.35 * math.sin(0.6 * current_time) + 0.15 * math.cos(1.2 * current_time)
            ambient_breeze = max(0.0, ambient_breeze)

        airspeed = fly_speed + ambient_breeze

        # 5. Surface proximity & physical contact
        surface_dist = max(0.0, fly_pos.z - surface_z)
        surface_contact = surface_dist <= 0.45 and (locomotion_mode == "GROUNDED" or fly_speed < 5.0)

        # 6. Six Individual Leg Contact Sensors (FL, FR, ML, MR, RL, RR)
        # Approximate tarsal tip heights based on body pitch/roll:
        c_fl = surface_dist <= 0.45 and (pitch >= -10.0 and roll <= 15.0)
        c_fr = surface_dist <= 0.45 and (pitch >= -10.0 and roll >= -15.0)
        c_ml = surface_dist <= 0.45 and (roll <= 15.0)
        c_mr = surface_dist <= 0.45 and (roll >= -15.0)
        c_rl = surface_dist <= 0.45 and (pitch <= 10.0 and roll <= 15.0)
        c_rr = surface_dist <= 0.45 and (pitch <= 10.0 and roll >= -15.0)

        if surface_contact and not any([c_fl, c_fr, c_ml, c_mr, c_rl, c_rr]):
            # If landed or flat on surface, all legs make stable contact
            c_fl = c_fr = c_ml = c_mr = c_rl = c_rr = True

        leg_contacts = (c_fl, c_fr, c_ml, c_mr, c_rl, c_rr)

        # 7. 3D Spatial Odor Diffusion & Bilateral Sampling
        odor_conc = 0.0
        odor_conc_l = 0.0
        odor_conc_r = 0.0
        odor_type = "NONE"
        nearest_food_source = None

        if odor_manager is not None:
            tot, l_c, r_c, n_src = odor_manager.compute_odor_at_point(
                point=fly_pos,
                heading_deg=fly_yaw,
                wind_dir=wind_dir,
                wind_speed=ambient_breeze
            )
            odor_conc = tot
            odor_conc_l = l_c
            odor_conc_r = r_c
            if n_src is not None:
                odor_type = n_src.odor_type
                nearest_food_source = n_src

        # 8. Virtual Compound-Eye Optical Computation
        dt_est = max(0.005, min(0.05, current_time - self.prev_time)) if self.prev_time > 0.0 else 0.02
        self.prev_time = current_time

        fly_velocity = fly_fwd * fly_speed
        fly_ang_vel = Vec3(0, 0, 0)
        foods_vis = [(f[0], f[1], 1.4, Vec4(0.9, 0.2, 0.2, 1.0)) for f in foods]
        frogs_vis = [(fr[0], fr[1], fr[2], 2.0) for fr in frogs]

        vis_out = self.visual_system.compute_vision(
            fly_pos=fly_pos,
            fly_yaw=fly_yaw,
            fly_pitch=pitch,
            fly_roll=roll,
            fly_velocity=fly_velocity,
            fly_ang_vel=fly_ang_vel,
            surface_z=surface_z,
            foods=foods_vis,
            frogs=frogs_vis,
            dt=dt_est
        )

        # 9. Multi-Modal Gustatory Taste Computation (Tarsal + Labellar physical contact)
        foods_taste = [(f[0], f[1], 1.4) for f in foods]
        proboscis_ext = 0.0
        if internal_state is not None and hasattr(internal_state, "feeding_rate"):
            proboscis_ext = internal_state.feeding_rate

        gust_out = self.gustatory_system.compute_taste(
            fly_pos=fly_pos,
            fly_is_grounded=(locomotion_mode == "GROUNDED"),
            proboscis_extension=proboscis_ext,
            foods=foods_taste,
            surface_type=surface_type,
            surface_dist=surface_dist,
            leg_contacts=leg_contacts
        )

        taste_sugar = gust_out.labellar_sweet
        leg_taste = gust_out.tarsal_sweet
        pam_reward = 0.0

        if gust_out.tarsal_contact_any or gust_out.labellar_contact:
            surface_contact = True
            if taste_sugar > 0.05 or gust_out.pharyngeal_ingestion_rate > 0.0:
                pam_reward = 1.0 * max(taste_sugar, gust_out.pharyngeal_ingestion_rate)

        # Legacy fallback if nearest food source is within touching distance
        if nearest_food_source is not None and nearest_food_source.active:
            to_food = fly_pos - nearest_food_source.pos
            f_dist = to_food.length()
            if f_dist < nearest_food_source.radius + 1.2:
                leg_taste = max(leg_taste, nearest_food_source.sweetness)
                surface_contact = True
                surface_type = f"FOOD_{nearest_food_source.name}"
                if f_dist < nearest_food_source.radius + 0.6:
                    taste_sugar = max(taste_sugar, nearest_food_source.sweetness)
                    pam_reward = max(pam_reward, 1.0 * taste_sugar)

        # 10. Internal Physiological State Modulation
        energy = 0.85
        hunger = 0.15
        hydration = 0.90
        olfactory_gain = 1.0
        gustatory_gain = 1.0

        if internal_state is not None:
            energy = internal_state.energy
            hunger = internal_state.hunger
            hydration = internal_state.hydration
            olfactory_gain = internal_state.olfactory_gain
            gustatory_gain = internal_state.gustatory_gain

        sensory = SensoryInput(
            dist_left=dist_l,
            dist_center=dist_c,
            dist_right=dist_r,
            max_range=self.max_sensor_range,
            target_visible=target_visible or vis_out.left_eye.target_visible or vis_out.right_eye.target_visible,
            target_azimuth=target_azimuth,
            target_dist=target_dist,
            target_pos=target_pos,
            optic_flow=max(optic_flow, vis_out.left_eye.flow_magnitude, vis_out.right_eye.flow_magnitude),
            airspeed=airspeed,
            ambient_breeze=ambient_breeze,
            surface_dist=surface_dist,
            surface_contact=surface_contact,
            surface_type=surface_type,
            frog_looming=max(frog_looming, vis_out.binocular_looming),
            env_motion=env_motion,
            locomotion_mode=locomotion_mode,
            fallback_active=fallback_active,
            odor_conc=odor_conc,
            odor_conc_l=odor_conc_l,
            odor_conc_r=odor_conc_r,
            odor_type=odor_type,
            taste_sugar=taste_sugar,
            leg_taste=leg_taste,
            leg_contacts=leg_contacts,
            energy=energy,
            hunger=hunger,
            hydration=hydration,
            olfactory_gain=olfactory_gain,
            gustatory_gain=gustatory_gain,
            predator_attack_active=frog_threat_active,
            pam_reward=pam_reward,
            ppl1_punish=ppl1_punish,
            eye_flow_l=vis_out.left_eye.flow_magnitude,
            eye_flow_r=vis_out.right_eye.flow_magnitude,
            eye_loom_l=vis_out.left_eye.looming_threat,
            eye_loom_r=vis_out.right_eye.looming_threat,
            target_elevation=vis_out.left_eye.target_elevation_deg,
            tarsal_sweet=gust_out.tarsal_sweet,
            tarsal_bitter=gust_out.tarsal_bitter,
            tarsal_water=gust_out.tarsal_water,
            tarsal_salt=gust_out.tarsal_salt,
            labellar_sweet=gust_out.labellar_sweet,
            labellar_bitter=gust_out.labellar_bitter,
            labellar_water=gust_out.labellar_water,
            labellar_salt=gust_out.labellar_salt,
            pharyngeal_ingestion=gust_out.pharyngeal_ingestion_rate,
            fly_heading_deg=fly_yaw,
            jo_wind_airspeed=airspeed,
        )

        return sensory, nearest_food_name, frog_threat_active

