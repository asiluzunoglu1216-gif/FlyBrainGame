"""Free Spectator & Chase Camera Controller.

Supports:
- Minecraft Spectator Mode:
  - W/S: Forward / Backward
  - A/D: Strafe Left / Right
  - Space: Ascend (+Z)
  - Shift / Ctrl: Descend (-Z)
  - Mouse: Free Look (Pitch & Yaw)
  - Mouse Wheel: Adjust movement speed
- Chase Mode:
  - Smooth 3rd-person tracking behind the fruit fly
- Key F:
  - Teleport to fly / Toggle between Chase & Free Spectator modes
"""
from __future__ import annotations

import math
from panda3d.core import NodePath, Vec3, WindowProperties


class CameraController:
    def __init__(self, base, fly_node: NodePath):
        self.base = base
        self.camera = base.camera
        self.fly_node = fly_node

        # Modes: "CHASE" or "SPECTATOR"
        self.mode = "CHASE"

        # Spectator flight variables
        self.cam_pos = Vec3(0, -35, 12)
        self.cam_yaw = 0.0
        self.cam_pitch = -15.0
        self.move_speed = 22.0  # units/s

        # Chase follow smoothing
        self.chase_dist = 13.0
        self.chase_height = 4.5
        self._chase_smooth_pos = Vec3(0, -35, 12)

        # Key state tracking
        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "space": False, "lshift": False, "lcontrol": False
        }

        self._mouse_active = False
        self._setup_inputs()

    def _setup_inputs(self):
        # Keyboard movement keys
        for k in ("w", "s", "a", "d", "space", "lshift", "lcontrol"):
            self.base.accept(k, self._set_key, [k, True])
            self.base.accept(f"{k}-up", self._set_key, [k, False])

        # Mouse wheel speed adjustment
        self.base.accept("wheel_up", self._on_wheel, [1])
        self.base.accept("wheel_down", self._on_wheel, [-1])

        # F key to toggle / teleport
        self.base.accept("f", self.toggle_mode)

    def _set_key(self, key: str, val: bool):
        self.keys[key] = val

    def _on_wheel(self, direction: int):
        # Scale speed between 5 and 70 units/s
        self.move_speed = max(5.0, min(70.0, self.move_speed + direction * 4.0))

    def toggle_mode(self):
        """Toggles between CHASE and SPECTATOR modes."""
        if self.mode == "CHASE":
            self.mode = "SPECTATOR"
            # Start spectator from current camera position
            self.cam_pos = Vec3(self.camera.getPos())
            self.cam_yaw = self.camera.getH()
            self.cam_pitch = self.camera.getP()
        else:
            self.mode = "CHASE"

    def update(self, dt: float, fly_pos: Vec3, fly_yaw: float):
        if self.mode == "CHASE":
            self._update_chase(dt, fly_pos, fly_yaw)
        else:
            self._update_spectator(dt)

    def _update_chase(self, dt: float, fly_pos: Vec3, fly_yaw: float):
        # 3rd-person chase camera
        rad = math.radians(fly_yaw)
        fwd = Vec3(math.cos(rad), math.sin(rad), 0.0)

        target_cam_pos = fly_pos - fwd * self.chase_dist + Vec3(0, 0, self.chase_height)
        self._chase_smooth_pos += (target_cam_pos - self._chase_smooth_pos) * min(1.0, dt * 7.0)

        self.camera.setPos(self._chase_smooth_pos)
        look_target = fly_pos + Vec3(0, 0, 1.2)
        self.camera.lookAt(look_target)

    def _update_spectator(self, dt: float):
        # 1. Mouse Look
        mw = self.base.mouseWatcherNode
        if mw.hasMouse():
            md = self.base.win.getPointer(0)
            x, y = md.getX(), md.getY()

            win_w = self.base.win.getXSize()
            win_h = self.base.win.getYSize()
            cx, cy = win_w // 2, win_h // 2

            dx = x - cx
            dy = y - cy

            sensitivity = 0.22
            self.cam_yaw -= dx * sensitivity
            self.cam_pitch = max(-85.0, min(85.0, self.cam_pitch - dy * sensitivity))

            # Re-center mouse pointer
            self.base.win.movePointer(0, cx, cy)

        # 2. Movement vectors based on camera yaw & pitch
        yaw_rad = math.radians(self.cam_yaw)
        pitch_rad = math.radians(self.cam_pitch)

        fwd = Vec3(
            -math.sin(yaw_rad) * math.cos(pitch_rad),
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad)
        )
        right = Vec3(math.cos(yaw_rad), math.sin(yaw_rad), 0.0)
        up = Vec3(0, 0, 1)

        move = Vec3(0, 0, 0)
        if self.keys["w"]:
            move += fwd
        if self.keys["s"]:
            move -= fwd
        if self.keys["d"]:
            move += right
        if self.keys["a"]:
            move -= right
        if self.keys["space"]:
            move += up
        if self.keys["lshift"] or self.keys["lcontrol"]:
            move -= up

        if move.lengthSquared() > 0:
            move.normalize()
            self.cam_pos += move * self.move_speed * dt

        self.camera.setPos(self.cam_pos)
        self.camera.setHpr(self.cam_yaw, self.cam_pitch, 0)
