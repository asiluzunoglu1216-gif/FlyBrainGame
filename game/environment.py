"""3D Environment: Room, Obstacle Boxes, Boundary Walls, and Moving Visual Target.

Provides both Panda3D visual scene nodes and mathematical bounding boxes
for sensor raycasting.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple
from panda3d.core import NodePath, Vec3, Vec4
from .fly_model import create_cube_geom


@dataclass
class ObstacleBox:
    name: str
    min_pt: Vec3
    max_pt: Vec3
    node: NodePath


class Environment:
    def __init__(self, render: NodePath, room_size: float = 90.0, room_height: float = 28.0):
        self.render = render
        self.room_size = room_size
        self.half_size = room_size * 0.5
        self.room_height = room_height

        self.env_root = render.attachNewNode("EnvironmentRoot")
        self.obstacles: List[ObstacleBox] = []

        # Target fruit
        self.target_node: NodePath = None
        self._target_base_pos = Vec3(18.0, 18.0, 10.0)
        self._target_time = 0.0

        self._build_room()
        self._build_obstacles()
        self._build_visual_target()

    def _build_room(self):
        hs = self.half_size
        h = self.room_height

        # Floor (Dark charcoal slate with slight checker tint)
        c_floor = Vec4(0.20, 0.22, 0.25, 1.0)
        floor_node = self.env_root.attachNewNode(create_cube_geom(self.room_size, self.room_size, 1.0, c_floor))
        floor_node.setPos(0, 0, -0.5)

        # Ceiling
        c_ceil = Vec4(0.35, 0.38, 0.42, 1.0)
        ceil_node = self.env_root.attachNewNode(create_cube_geom(self.room_size, self.room_size, 1.0, c_ceil))
        ceil_node.setPos(0, 0, h + 0.5)

        # 4 Boundary Walls
        c_wall_x = Vec4(0.40, 0.45, 0.50, 1.0)
        c_wall_y = Vec4(0.45, 0.50, 0.55, 1.0)

        # North Wall (+Y)
        w_north = self.env_root.attachNewNode(create_cube_geom(self.room_size, 1.0, h, c_wall_y))
        w_north.setPos(0, hs + 0.5, h * 0.5)

        # South Wall (-Y)
        w_south = self.env_root.attachNewNode(create_cube_geom(self.room_size, 1.0, h, c_wall_y))
        w_south.setPos(0, -hs - 0.5, h * 0.5)

        # East Wall (+X)
        w_east = self.env_root.attachNewNode(create_cube_geom(1.0, self.room_size, h, c_wall_x))
        w_east.setPos(hs + 0.5, 0, h * 0.5)

        # West Wall (-X)
        w_west = self.env_root.attachNewNode(create_cube_geom(1.0, self.room_size, h, c_wall_x))
        w_west.setPos(-hs - 0.5, 0, h * 0.5)

    def _build_obstacles(self):
        """Places obstacles (crates / pillars) with distinct colors inside the room."""
        boxes_spec = [
            ("Crate_A", Vec3(-18.0, 15.0, 6.0), Vec3(8.0, 8.0, 12.0), Vec4(0.65, 0.48, 0.28, 1.0)),
            ("Crate_B", Vec3(16.0, -14.0, 7.0), Vec3(10.0, 10.0, 14.0), Vec4(0.55, 0.42, 0.25, 1.0)),
            ("Crate_C", Vec3(-12.0, -18.0, 5.0), Vec3(7.0, 7.0, 10.0), Vec4(0.58, 0.45, 0.27, 1.0)),
            ("Pillar_Center", Vec3(0.0, 0.0, 9.0), Vec3(6.0, 6.0, 18.0), Vec4(0.70, 0.35, 0.20, 1.0)),
            ("Crate_D", Vec3(22.0, 18.0, 5.0), Vec3(9.0, 9.0, 10.0), Vec4(0.50, 0.40, 0.30, 1.0)),
        ]

        for name, pos, size, color in boxes_spec:
            node = self.env_root.attachNewNode(create_cube_geom(size.x, size.y, size.z, color))
            node.setPos(pos)
            hx, hy, hz = size.x * 0.5, size.y * 0.5, size.z * 0.5
            min_pt = Vec3(pos.x - hx, pos.y - hy, pos.z - hz)
            max_pt = Vec3(pos.x + hx, pos.y + hy, pos.z + hz)
            self.obstacles.append(ObstacleBox(name=name, min_pt=min_pt, max_pt=max_pt, node=node))

    def _build_visual_target(self):
        """Creates a bright orange/red fruit target (apple/berry) with a green stem."""
        self.target_node = self.env_root.attachNewNode("VisualTarget")
        self.target_node.setPos(self._target_base_pos)

        # Fruit body (bright red-orange)
        c_fruit = Vec4(0.95, 0.32, 0.12, 1.0)
        body = self.target_node.attachNewNode(create_cube_geom(2.2, 2.2, 2.0, c_fruit))
        body.setPos(0, 0, 0)

        # Stem / Leaf (green)
        c_stem = Vec4(0.15, 0.75, 0.20, 1.0)
        stem = self.target_node.attachNewNode(create_cube_geom(0.4, 0.4, 1.0, c_stem))
        stem.setPos(0, 0, 1.2)
        leaf = self.target_node.attachNewNode(create_cube_geom(1.0, 0.6, 0.2, c_stem))
        leaf.setPos(0.5, 0, 1.4)
        leaf.setR(25)

    def update(self, dt: float):
        """Animates gentle floating/patrol of the visual target."""
        self._target_time += dt * 0.5
        # Circular / elliptical hover motion
        radius_x = 22.0
        radius_y = 18.0
        x = math.cos(self._target_time) * radius_x
        y = math.sin(self._target_time * 1.3) * radius_y
        z = 9.0 + math.sin(self._target_time * 2.0) * 2.5
        self.target_node.setPos(x, y, z)

    def get_target_pos(self) -> Vec3:
        return self.target_node.getPos()

    def raycast(self, origin: Vec3, direction: Vec3, max_dist: float = 40.0) -> float:
        """Calculates distance from origin along direction to nearest obstacle or wall."""
        dir_norm = Vec3(direction)
        dir_norm.normalize()

        closest_dist = max_dist
        hs = self.half_size
        h = self.room_height

        # 1. Intersect 6 room boundary planes
        # X boundaries (-hs, +hs)
        if abs(dir_norm.x) > 1e-6:
            tx1 = (-hs - origin.x) / dir_norm.x
            tx2 = (hs - origin.x) / dir_norm.x
            for t in (tx1, tx2):
                if t > 0 and t < closest_dist:
                    hit_y = origin.y + t * dir_norm.y
                    hit_z = origin.z + t * dir_norm.z
                    if -hs <= hit_y <= hs and 0 <= hit_z <= h:
                        closest_dist = t

        # Y boundaries (-hs, +hs)
        if abs(dir_norm.y) > 1e-6:
            ty1 = (-hs - origin.y) / dir_norm.y
            ty2 = (hs - origin.y) / dir_norm.y
            for t in (ty1, ty2):
                if t > 0 and t < closest_dist:
                    hit_x = origin.x + t * dir_norm.x
                    hit_z = origin.z + t * dir_norm.z
                    if -hs <= hit_x <= hs and 0 <= hit_z <= h:
                        closest_dist = t

        # Z boundaries (floor 0, ceil h)
        if abs(dir_norm.z) > 1e-6:
            tz1 = (0.0 - origin.z) / dir_norm.z
            tz2 = (h - origin.z) / dir_norm.z
            for t in (tz1, tz2):
                if t > 0 and t < closest_dist:
                    hit_x = origin.x + t * dir_norm.x
                    hit_y = origin.y + t * dir_norm.y
                    if -hs <= hit_x <= hs and -hs <= hit_y <= hs:
                        closest_dist = t

        # 2. Intersect obstacle boxes (AABB ray-box intersection slab method)
        for box in self.obstacles:
            tmin = -1e9
            tmax = 1e9

            # X
            if abs(dir_norm.x) > 1e-6:
                tx1 = (box.min_pt.x - origin.x) / dir_norm.x
                tx2 = (box.max_pt.x - origin.x) / dir_norm.x
                tmin = max(tmin, min(tx1, tx2))
                tmax = min(tmax, max(tx1, tx2))
            elif origin.x < box.min_pt.x or origin.x > box.max_pt.x:
                continue

            # Y
            if abs(dir_norm.y) > 1e-6:
                ty1 = (box.min_pt.y - origin.y) / dir_norm.y
                ty2 = (box.max_pt.y - origin.y) / dir_norm.y
                tmin = max(tmin, min(ty1, ty2))
                tmax = min(tmax, max(ty1, ty2))
            elif origin.y < box.min_pt.y or origin.y > box.max_pt.y:
                continue

            # Z
            if abs(dir_norm.z) > 1e-6:
                tz1 = (box.min_pt.z - origin.z) / dir_norm.z
                tz2 = (box.max_pt.z - origin.z) / dir_norm.z
                tmin = max(tmin, min(tz1, tz2))
                tmax = min(tmax, max(tz1, tz2))
            elif origin.z < box.min_pt.z or origin.z > box.max_pt.z:
                continue

            if tmax >= max(0.0, tmin) and tmin > 0 and tmin < closest_dist:
                closest_dist = tmin

        return closest_dist
