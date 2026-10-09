"""Virtual Compound-Eye Visual Sensory System for Drosophila.

Implements a biologically realistic compound-eye optical front end.
Drosophila eyes consist of ~750-800 ommatidia per eye, providing a ~220-270 degree
visual field with distinct left and right receptive hemispheres.

Computes for Left and Right eyes from the fly's body perspective:
- Local luminance & contrast
- Translational and rotational optic flow
- Retinal motion direction and magnitude (horizontal and vertical)
- Visual object angular size (theta)
- Angular expansion rate (d_theta / dt) -> LC4 / LPLC2 looming
- Angular velocity across retina (d_phi / dt)
- Target azimuth and elevation -> LC10 family
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from panda3d.core import Vec3, Vec4


@dataclass
class EyeRetinalState:
    luminance: float = 0.5            # 0.0 to 1.0 ambient retinal luminance
    contrast: float = 0.0             # Visual contrast of dominant object
    flow_horizontal: float = 0.0      # Retinal motion along yaw axis (rad/s)
    flow_vertical: float = 0.0        # Retinal motion along pitch axis (rad/s)
    flow_magnitude: float = 0.0       # Total optical flow magnitude
    looming_threat: float = 0.0       # LC4/LPLC2 angular expansion signal (0.0 to 1.0)
    target_visible: bool = False
    target_azimuth_deg: float = 0.0   # Horizontal angle relative to eye center
    target_elevation_deg: float = 0.0 # Vertical angle relative to eye center
    target_angular_size: float = 0.0  # Apparent visual size (radians)
    target_angular_vel: float = 0.0   # Apparent tracking speed across retina (deg/s)


@dataclass
class CompoundEyeVisualOutput:
    left_eye: EyeRetinalState
    right_eye: EyeRetinalState
    binocular_looming: float = 0.0
    ground_clearance_flow: float = 0.0
    sky_ground_polarity: float = 0.0   # Dorsal light orientation response


class VirtualCompoundEyeSystem:
    """Simulates the optical physics and retinal receptive fields of both compound eyes."""

    def __init__(self, fov_deg: float = 220.0):
        self.fov_deg = fov_deg
        self.half_fov_deg = fov_deg * 0.5

        # Memory for rate of expansion / angular velocity tracking
        self.prev_targets: dict = {}
        self.prev_frogs: dict = {}

    def compute_vision(
        self,
        fly_pos: Vec3,
        fly_yaw: float,
        fly_pitch: float,
        fly_roll: float,
        fly_velocity: Vec3,
        fly_ang_vel: Vec3,
        surface_z: float,
        foods: List[Tuple[str, Vec3, float, Vec4]],  # (name, pos, radius, color)
        frogs: List[Tuple[str, Vec3, Vec3, float]],  # (name, pos, velocity, radius)
        dt: float
    ) -> CompoundEyeVisualOutput:
        """Processes 3D scene geometry into retinal excitation signals for both eyes."""
        dt = max(0.001, dt)

        # 1. Coordinate Frame Setup
        # Body forward vector
        yaw_rad = math.radians(fly_yaw)
        pitch_rad = math.radians(fly_pitch)
        roll_rad = math.radians(fly_roll)

        fwd = Vec3(math.cos(yaw_rad) * math.cos(pitch_rad),
                   math.sin(yaw_rad) * math.cos(pitch_rad),
                   math.sin(pitch_rad)).normalized()

        # Body right vector
        right = Vec3(math.sin(yaw_rad), -math.cos(yaw_rad), 0.0).normalized()
        # Body up vector
        up = fwd.cross(right).normalized()

        fly_speed = fly_velocity.length()

        # 2. Optic Flow Computation (Translational + Rotational)
        # Ground clearance (ventral flow sensor)
        h_above_surface = max(0.2, fly_pos.z - surface_z)
        ventral_flow = (fly_speed / h_above_surface) if fly_speed > 0.01 else 0.0

        # Translational flow on lateral eyes:
        # Forward speed produces back-to-front retinal slip on lateral ommatidia
        fwd_speed = fly_velocity.dot(fwd)
        lateral_slip = fly_velocity.dot(right)

        left_trans_flow = max(0.0, fwd_speed / max(1.5, h_above_surface)) - (lateral_slip * 0.2)
        right_trans_flow = max(0.0, fwd_speed / max(1.5, h_above_surface)) + (lateral_slip * 0.2)

        # Rotational flow from body yaw rate
        yaw_rate_deg = fly_ang_vel.z
        left_rot_flow = -math.radians(yaw_rate_deg)
        right_rot_flow = math.radians(yaw_rate_deg)

        # 3. Ambient Luminance & Sky-Ground Polarity (Dorsal Light Response)
        # Sky is brighter (zenith), ground has lower albedo
        altitude_clamped = min(20.0, max(0.0, fly_pos.z))
        sky_factor = 0.5 + 0.5 * (altitude_clamped / 20.0)
        sky_ground_polarity = math.sin(pitch_rad)  # Positive looking up, negative looking down

        left_eye = EyeRetinalState(
            luminance=sky_factor * 0.75,
            contrast=0.20,
            flow_horizontal=left_trans_flow + left_rot_flow,
            flow_vertical=-math.radians(fly_ang_vel.y),
            flow_magnitude=math.sqrt(left_trans_flow**2 + left_rot_flow**2),
        )

        right_eye = EyeRetinalState(
            luminance=sky_factor * 0.75,
            contrast=0.20,
            flow_horizontal=right_trans_flow + right_rot_flow,
            flow_vertical=-math.radians(fly_ang_vel.y),
            flow_magnitude=math.sqrt(right_trans_flow**2 + right_rot_flow**2),
        )

        # 4. Predator Threat & Looming Computation (LC4 / LPLC2)
        # Angular expansion: d_theta/dt = 2 * r * v_approach / (d^2 + r^2)
        for name, f_pos, f_vel, f_radius in frogs:
            to_frog = f_pos - fly_pos
            dist = to_frog.length()
            if dist < 0.1:
                continue

            rel_vel = f_vel - fly_velocity
            approach_vel = -to_frog.normalized().dot(rel_vel)  # Positive when closing in

            # Visual bearing
            frog_angle_deg = math.degrees(math.atan2(to_frog.y, to_frog.x))
            azimuth_diff = (frog_angle_deg - fly_yaw + 180.0) % 360.0 - 180.0
            elev_diff = math.degrees(math.atan2(to_frog.z, math.sqrt(to_frog.x**2 + to_frog.y**2))) - fly_pitch

            if abs(azimuth_diff) < self.half_fov_deg:
                # Apparent angular size (radians)
                ang_size = 2.0 * math.atan2(f_radius, dist)

                # Angular expansion rate (looming)
                expansion_rate = 0.0
                if approach_vel > 0.0:
                    expansion_rate = (2.0 * f_radius * approach_vel) / (dist**2 + f_radius**2)

                # Looming stimulus threshold (~0.05 rad/s expansion or critical proximity)
                looming_stim = 0.0
                if expansion_rate > 0.04 or dist < 12.0:
                    looming_stim = min(1.0, expansion_rate * 3.5 + max(0.0, (12.0 - dist) / 12.0) * 0.6)

                # Lateral eye projection
                # azimuth_diff > 0: Threat on LEFT eye hemisphere
                # azimuth_diff < 0: Threat on RIGHT eye hemisphere
                if azimuth_diff > 10.0:
                    left_eye.looming_threat = max(left_eye.looming_threat, looming_stim)
                elif azimuth_diff < -10.0:
                    right_eye.looming_threat = max(right_eye.looming_threat, looming_stim)
                else:
                    # Bilateral head-on threat
                    left_eye.looming_threat = max(left_eye.looming_threat, looming_stim)
                    right_eye.looming_threat = max(right_eye.looming_threat, looming_stim)

        # 5. Visual Small-Object / Target Tracking (LC10a / LC10b / LC10c)
        closest_food_dist = 1e9
        nearest_food_data = None

        for name, food_pos, food_radius, color in foods:
            to_food = food_pos - fly_pos
            dist = to_food.length()
            if dist < 38.0 and dist < closest_food_dist:
                food_angle_deg = math.degrees(math.atan2(to_food.y, to_food.x))
                az_diff = (food_angle_deg - fly_yaw + 180.0) % 360.0 - 180.0
                horizontal_dist = math.sqrt(to_food.x**2 + to_food.y**2)
                el_diff = math.degrees(math.atan2(to_food.z, max(0.1, horizontal_dist))) - fly_pitch

                if abs(az_diff) < 95.0 and abs(el_diff) < 65.0:
                    closest_food_dist = dist
                    nearest_food_data = (name, dist, az_diff, el_diff, food_radius, color)

        if nearest_food_data is not None:
            name, dist, az_diff, el_diff, food_radius, color = nearest_food_data
            ang_size = 2.0 * math.atan2(food_radius, dist)

            # Compute tracking angular velocity across retina
            prev_az = self.prev_targets.get(name, az_diff)
            ang_vel = (az_diff - prev_az) / dt
            self.prev_targets[name] = az_diff

            # Visual contrast (food vs meadow background)
            food_contrast = min(1.0, 0.4 + (1.0 - dist / 38.0) * 0.5)

            # Route to appropriate eye:
            # az_diff < 0: Target on RIGHT
            # az_diff > 0: Target on LEFT
            if az_diff <= 0.0:
                right_eye.target_visible = True
                right_eye.target_azimuth_deg = az_diff
                right_eye.target_elevation_deg = el_diff
                right_eye.target_angular_size = ang_size
                right_eye.target_angular_vel = ang_vel
                right_eye.contrast = max(right_eye.contrast, food_contrast)
            if az_diff >= -15.0 and az_diff <= 15.0:
                # Binocular frontal overlap zone (~30 degrees)
                left_eye.target_visible = True
                left_eye.target_azimuth_deg = az_diff
                left_eye.target_elevation_deg = el_diff
                left_eye.target_angular_size = ang_size
                left_eye.contrast = max(left_eye.contrast, food_contrast)
            elif az_diff > 0.0:
                left_eye.target_visible = True
                left_eye.target_azimuth_deg = az_diff
                left_eye.target_elevation_deg = el_diff
                left_eye.target_angular_size = ang_size
                left_eye.target_angular_vel = ang_vel
                left_eye.contrast = max(left_eye.contrast, food_contrast)

        binocular_looming = max(left_eye.looming_threat, right_eye.looming_threat)

        return CompoundEyeVisualOutput(
            left_eye=left_eye,
            right_eye=right_eye,
            binocular_looming=binocular_looming,
            ground_clearance_flow=ventral_flow,
            sky_ground_polarity=sky_ground_polarity
        )
