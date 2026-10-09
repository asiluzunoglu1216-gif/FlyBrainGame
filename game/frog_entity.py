"""Frog Predator Entity and AI with Human-Visible Tongue Strike & Physical Collision.

Lifecycle:
  IDLE: Resting near water/rocks
  WATCH: Turns towards fly, tracks with eyes if within awareness range (35m)
  AIM: Lowers posture, opens mouth, telegraphs impending strike (0.35s)
  TONGUE_STRIKE: Rapid, human-visible pink tongue shoots towards fly (0.30s)
  CATCH_PULL: If physical tongue tip touches fly, retracts carrying fly into mouth (0.45s)
  COOLDOWN: Pauses after strike/miss before next cycle (1.8s)

Rules:
- Proximity alone MUST NOT kill.
- JUMP body collision MUST NOT kill.
- ONLY physical tongue-tip collider intersection (< 1.2 units) can catch the fly.
- Tongue misses retract safely without harm.
- If caught, fly is visibly pulled into frog's mouth before FLY EATEN Game Over triggers.
"""
from __future__ import annotations

import math
import random
from typing import Optional, Tuple
from panda3d.core import NodePath, Vec3, Vec4
from .fly_model import create_cube_geom


class FrogEntity:
    def __init__(self, render: NodePath, name: str, home_pos: Vec3, scale: float = 1.6):
        self.render = render
        self.name = name
        self.home_pos = Vec3(home_pos)
        self.pos = Vec3(home_pos)
        self.yaw = random.uniform(0, 360)
        self.velocity = Vec3(0, 0, 0)
        self.scale = scale

        # State machine: IDLE, WATCH, AIM, TONGUE_STRIKE, CATCH_PULL, COOLDOWN
        self.state = "IDLE"
        self.state_timer = 0.0

        # Tongue attack parameters
        self.tongue_timer = 0.0
        self.tongue_strike_duration = 0.30  # Extension time (fast but human-visible)
        self.tongue_pull_duration = 0.45    # Visible retraction carrying fly
        self.tongue_retract_duration = 0.25 # Miss retraction
        self.max_tongue_length = 12.0
        self.tongue_target = Vec3(0, 0, 0)
        self.tongue_tip_pos = Vec3(home_pos)
        self.tongue_current_length = 0.0
        self.tongue_visible = False
        self.physical_hit = False

        # Caught fly position tracking for pull animation
        self.caught_fly_offset = Vec3(0, 0, 0)

        # Encounter tracking with hysteresis
        self.is_engaged = False
        self.encounter_registered = False

        # Build 3D mesh
        self._build_frog_mesh()

    def _build_frog_mesh(self):
        self.root = self.render.attachNewNode(f"Frog_{self.name}")
        self.root.setPos(self.pos)
        self.root.setScale(self.scale)

        c_skin = Vec4(0.22, 0.62, 0.18, 1.0)      # Bright amphibian green
        c_belly = Vec4(0.78, 0.88, 0.48, 1.0)     # Pale yellow-green belly
        c_eye = Vec4(0.95, 0.85, 0.10, 1.0)       # Golden frog eyes
        c_pupil = Vec4(0.05, 0.05, 0.05, 1.0)
        c_tongue = Vec4(0.96, 0.22, 0.38, 1.0)    # Vibrant fleshy pink tongue
        c_tip = Vec4(1.0, 0.10, 0.25, 1.0)        # Deep red sticky tip

        # 1. Body / Torso
        self.body = self.root.attachNewNode(create_cube_geom(2.2, 2.6, 1.4, c_skin))
        self.body.setPos(0, 0, 0.7)

        # Belly underbody
        self.belly = self.root.attachNewNode(create_cube_geom(1.8, 2.2, 0.3, c_belly))
        self.belly.setPos(0, 0, 0.2)

        # 2. Large Bulbous Eyes
        for sx in [-0.8, 0.8]:
            eye = self.root.attachNewNode(create_cube_geom(0.6, 0.6, 0.6, c_eye))
            eye.setPos(sx, 0.8, 1.5)
            pupil = eye.attachNewNode(create_cube_geom(0.2, 0.62, 0.4, c_pupil))
            pupil.setPos(0, 0.02, 0)

        # 3. Hind Legs (Bent frog legs)
        for side, sx in [(-1, -1.3), (1, 1.3)]:
            thigh = self.root.attachNewNode(create_cube_geom(0.7, 1.4, 0.9, c_skin))
            thigh.setPos(sx, -0.6, 0.6)
            thigh.setR(side * 20)

        # 4. Extendable Tongue Mesh (Human-visible pink beam + bulbous sticky tip)
        self.tongue_root = self.render.attachNewNode(f"FrogTongue_{self.name}")
        self.tongue_stem = self.tongue_root.attachNewNode(create_cube_geom(0.5, 1.0, 0.4, c_tongue))
        self.tongue_stem.setPos(0, 0.5, 0)

        # Sticky tip bulb (prominent round tip)
        self.tongue_tip_node = self.tongue_root.attachNewNode(create_cube_geom(0.7, 0.7, 0.6, c_tip))
        self.tongue_tip_node.setPos(0, 1.0, 0)

        self.tongue_root.hide()

    def check_encounter(self, fly_pos: Vec3) -> bool:
        """Hysteresis encounter check. Triggers +1 when frog engages fly."""
        dist = (fly_pos - self.pos).length()
        if not self.is_engaged:
            if dist < 25.0 or self.state in ("WATCH", "AIM", "TONGUE_STRIKE", "CATCH_PULL"):
                self.is_engaged = True
                self.encounter_registered = True
                return True
        else:
            if dist > 35.0 and self.state == "IDLE":
                self.is_engaged = False
                self.encounter_registered = False
        return False

    def update(self, dt: float, fly_pos: Vec3) -> bool:
        """Updates frog AI, visible tongue mechanics, and physical capture animation.

        Returns:
            True ONLY when the fly is physically captured and pulled into the mouth (Game Over).
        """
        self.state_timer += dt
        to_fly = fly_pos - self.pos
        dist_to_fly = to_fly.length()
        frog_mouth_world = self.pos + Vec3(0, 0, 0.9)

        # Smoothly track fly with body yaw if within awareness (35 units)
        if dist_to_fly < 35.0 and self.state != "CATCH_PULL":
            target_yaw = math.degrees(math.atan2(to_fly.y, to_fly.x)) - 90.0
            diff = (target_yaw - self.yaw + 180.0) % 360.0 - 180.0
            self.yaw += diff * min(1.0, dt * 6.0)

        fly_consumed = False

        # ============================================================
        # STATE MACHINE
        # ============================================================
        if self.state == "IDLE":
            self.velocity = Vec3(0, 0, 0)
            self.tongue_visible = False
            self.tongue_root.hide()
            self.physical_hit = False

            if dist_to_fly < 30.0:
                self.state = "WATCH"
                self.state_timer = 0.0
                self.is_engaged = True
            elif self.state_timer > 5.0:
                # Occasional small repositioning hop
                self.state = "PATROL"
                self.state_timer = 0.0
                self.yaw += random.uniform(-45, 45)

        elif self.state == "PATROL":
            if self.state_timer < 0.35:
                rad = math.radians(self.yaw + 90.0)
                self.velocity = Vec3(math.cos(rad), math.sin(rad), 0.0) * 2.5 + Vec3(0, 0, 1.5)
            else:
                self.velocity = Vec3(0, 0, 0)
                self.state = "IDLE"
                self.state_timer = 0.0

        elif self.state == "WATCH":
            self.velocity = Vec3(0, 0, 0)
            if dist_to_fly > 32.0:
                self.state = "IDLE"
                self.state_timer = 0.0
            elif dist_to_fly < 11.0 and self.state_timer > 0.6:
                # Enter AIM to visibly telegraph impending tongue strike
                self.state = "AIM"
                self.state_timer = 0.0

        elif self.state == "AIM":
            # Telegraph: frog lowers body slightly and stares intently
            self.velocity = Vec3(0, 0, 0)
            if self.state_timer > 0.35:
                # Launch visible tongue strike!
                self.state = "TONGUE_STRIKE"
                self.state_timer = 0.0
                self.tongue_timer = 0.0
                self.tongue_target = Vec3(fly_pos)
                self.tongue_visible = True
                self.physical_hit = False

        elif self.state == "TONGUE_STRIKE":
            self.tongue_timer += dt
            self.tongue_visible = True
            self.tongue_root.show()

            if self.tongue_target == Vec3(0, 0, 0):
                self.tongue_target = Vec3(fly_pos)

            # Aim tongue from mouth towards target
            strike_vector = self.tongue_target - frog_mouth_world
            total_strike_dist = min(self.max_tongue_length, strike_vector.length())
            strike_dir = strike_vector.normalized() if strike_vector.length() > 0.01 else Vec3(0, 1, 0)

            self.tongue_root.setPos(frog_mouth_world)
            self.tongue_root.lookAt(self.render, self.tongue_target)

            ext_time = self.tongue_strike_duration
            if self.tongue_timer < ext_time:
                # Phase 1: Rapid extension towards fly
                progress = self.tongue_timer / ext_time
                cur_len = progress * total_strike_dist
                self.tongue_current_length = cur_len
                self.tongue_stem.setScale(1.0, max(0.05, cur_len), 1.0)
                self.tongue_tip_node.setPos(0, cur_len, 0)

                # World position of sticky tip
                self.tongue_tip_pos = frog_mouth_world + strike_dir * cur_len

                # Physical collider check: ONLY physical tip intersection can catch fly
                dist_to_tip = (self.tongue_tip_pos - fly_pos).length()
                if dist_to_tip < 1.2:
                    self.physical_hit = True
                    self.state = "CATCH_PULL"
                    self.state_timer = 0.0
                    self.tongue_timer = 0.0
                    # Lock initial pull length
                    self.pull_start_len = cur_len
            else:
                # Phase 2: Missed - retract tongue without carrying fly
                retract_t = self.tongue_timer - ext_time
                if retract_t < self.tongue_retract_duration:
                    progress = 1.0 - (retract_t / self.tongue_retract_duration)
                    cur_len = max(0.1, progress * total_strike_dist)
                    self.tongue_stem.setScale(1.0, cur_len, 1.0)
                    self.tongue_tip_node.setPos(0, cur_len, 0)
                else:
                    self.tongue_root.hide()
                    self.tongue_visible = False
                    self.state = "COOLDOWN"
                    self.state_timer = 0.0

        elif self.state == "CATCH_PULL":
            # Visible capture animation: Tongue retracts, dragging fly into frog mouth!
            self.tongue_timer += dt
            pull_progress = min(1.0, self.tongue_timer / self.tongue_pull_duration)
            remaining_len = (1.0 - pull_progress) * self.pull_start_len

            strike_dir = (self.tongue_target - frog_mouth_world).normalized()
            self.tongue_tip_pos = frog_mouth_world + strike_dir * remaining_len

            self.tongue_stem.setScale(1.0, max(0.1, remaining_len), 1.0)
            self.tongue_tip_node.setPos(0, remaining_len, 0)

            # Move fly visually along with the tongue tip
            fly_pos.x = self.tongue_tip_pos.x
            fly_pos.y = self.tongue_tip_pos.y
            fly_pos.z = self.tongue_tip_pos.z

            if pull_progress >= 1.0:
                # Fly has arrived at frog's mouth -> EATEN!
                self.tongue_root.hide()
                self.tongue_visible = False
                self.state = "IDLE"
                self.state_timer = 0.0
                fly_consumed = True

        elif self.state == "COOLDOWN":
            self.velocity = Vec3(0, 0, 0)
            self.tongue_visible = False
            self.tongue_root.hide()
            if self.state_timer > 1.8:
                self.state = "IDLE"
                self.state_timer = 0.0

        # Update root node transform
        self.pos.z = self.home_pos.z
        self.root.setPos(self.pos)
        self.root.setHpr(self.yaw, 0, 0)

        return fly_consumed

    def reset(self):
        """Resets frog to initial home position and idle state."""
        self.pos = Vec3(self.home_pos)
        self.velocity = Vec3(0, 0, 0)
        self.state = "IDLE"
        self.state_timer = 0.0
        self.tongue_timer = 0.0
        self.tongue_visible = False
        self.physical_hit = False
        self.is_engaged = False
        self.encounter_registered = False
        if hasattr(self, "tongue_root"):
            self.tongue_root.hide()
        self.root.setPos(self.pos)

    def check_encounter(self, fly_pos: Vec3) -> bool:
        """Checks if fly entered proximity (< 22.0 units) with hysteresis (> 28.0 units to exit)."""
        dist = (fly_pos - self.pos).length()
        if dist < 22.0:
            if not self.is_engaged:
                self.is_engaged = True
                self.encounter_registered = True
                return True
            return False
        elif dist > 28.0:
            self.is_engaged = False
            return False
        return False
