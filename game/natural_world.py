"""Large Living Natural Environment.

Generates an expansive natural ecosystem (240 x 240 units):
- Rolling grassy ground
- Blue reflective pond/puddles
- Low-poly trees with perchable branches and foliage
- Flat rocks and boulders
- Bushes and natural obstacles

Includes fast raycasting and surface height detection for landing mechanics.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Tuple
from panda3d.core import NodePath, Vec3, Vec4
from .fly_model import create_cube_geom
from .environment import ObstacleBox


@dataclass
class PerchSurface:
    name: str
    center: Vec3
    half_extents: Vec3
    surface_type: str  # "GROUND", "ROCK", "BRANCH", "FOOD"


class NaturalWorld:
    def __init__(self, render: NodePath, world_size: float = 240.0, world_height: float = 45.0):
        self.render = render
        self.world_size = world_size
        self.half_size = world_size * 0.5
        self.world_height = world_height

        self.root = render.attachNewNode("NaturalWorldRoot")
        self.obstacles: List[ObstacleBox] = []
        self.surfaces: List[PerchSurface] = []

        self._build_terrain()
        self._build_pond()
        self._build_trees()
        self._build_rocks()
        self._build_bushes()

    def _build_terrain(self):
        ws = self.world_size
        # Rich meadow green ground
        c_grass = Vec4(0.24, 0.48, 0.20, 1.0)
        c_hill = Vec4(0.28, 0.52, 0.22, 1.0)

        # Base flat meadow
        ground = self.root.attachNewNode(create_cube_geom(ws, ws, 1.0, c_grass))
        ground.setPos(0, 0, -0.5)

        # Rolling hills (gentle low-poly elevation mounds)
        hill_positions = [
            (Vec3(-65, 55, 3.0), (45.0, 40.0, 6.0)),
            (Vec3(60, 65, 4.0), (50.0, 45.0, 8.0)),
            (Vec3(75, -55, 3.5), (42.0, 42.0, 7.0)),
            (Vec3(-70, -60, 2.5), (38.0, 38.0, 5.0)),
        ]

        for pos, size in hill_positions:
            hill = self.root.attachNewNode(create_cube_geom(size[0], size[1], size[2], c_hill))
            hill.setPos(pos)
            hx, hy, hz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
            min_pt = Vec3(pos.x - hx, pos.y - hy, pos.z - hz)
            max_pt = Vec3(pos.x + hx, pos.y + hy, pos.z + hz)
            self.obstacles.append(ObstacleBox(name="Hill", min_pt=min_pt, max_pt=max_pt, node=hill))
            self.surfaces.append(PerchSurface("HillTop", Vec3(pos.x, pos.y, pos.z + hz), Vec3(hx, hy, 0.5), "GROUND"))

        # Base ground perch surface (top_z = 0.0)
        self.surfaces.append(PerchSurface("Ground", Vec3(0, 0, -0.1), Vec3(self.half_size, self.half_size, 0.1), "GROUND"))

    def _build_pond(self):
        # Tranquil blue pond at (-25, -40)
        c_water = Vec4(0.22, 0.55, 0.85, 0.95)
        pond = self.root.attachNewNode(create_cube_geom(38.0, 28.0, 0.4, c_water))
        pond.setPos(-25.0, -40.0, 0.05)

    def _build_trees(self):
        """Builds low-poly trees with perchable branches and canopies."""
        c_trunk = Vec4(0.42, 0.28, 0.16, 1.0)
        c_foliage = Vec4(0.18, 0.58, 0.18, 1.0)
        c_foliage_light = Vec4(0.25, 0.65, 0.22, 1.0)

        tree_specs = [
            (Vec3(15.0, -25.0, 0.0), 14.0, 1.8),
            (Vec3(-40.0, 35.0, 0.0), 16.0, 2.0),
            (Vec3(45.0, 35.0, 0.0), 12.0, 1.6),
            (Vec3(-10.0, 35.0, 0.0), 15.0, 1.9),
            (Vec3(35.0, -45.0, 0.0), 13.0, 1.7),
            (Vec3(-55.0, -20.0, 0.0), 15.0, 1.8),
        ]

        for i, (pos, trunk_h, trunk_r) in enumerate(tree_specs):
            tree_root = self.root.attachNewNode(f"Tree_{i}")
            tree_root.setPos(pos)

            # Trunk
            trunk = tree_root.attachNewNode(create_cube_geom(trunk_r * 2, trunk_r * 2, trunk_h, c_trunk))
            trunk.setPos(0, 0, trunk_h * 0.5)

            # Horizontal Branch (Perchable surface!)
            b_len = 6.0
            branch = tree_root.attachNewNode(create_cube_geom(b_len, 0.9, 0.7, c_trunk))
            branch.setPos(b_len * 0.45, 0, trunk_h * 0.55)
            # Register branch perch surface
            branch_world = pos + Vec3(b_len * 0.45, 0, trunk_h * 0.55 + 0.35)
            self.surfaces.append(PerchSurface(f"Branch_{i}", branch_world, Vec3(b_len * 0.5, 0.6, 0.35), "BRANCH"))

            # Canopy (2 tiers of foliage)
            tier1 = tree_root.attachNewNode(create_cube_geom(10.0, 10.0, 6.0, c_foliage))
            tier1.setPos(0, 0, trunk_h + 2.0)

            tier2 = tree_root.attachNewNode(create_cube_geom(6.5, 6.5, 5.0, c_foliage_light))
            tier2.setPos(0, 0, trunk_h + 6.0)

            # Obstacles for collision & raycasting
            hx, hy = 4.0, 4.0
            min_pt = Vec3(pos.x - hx, pos.y - hy, pos.z)
            max_pt = Vec3(pos.x + hx, pos.y + hy, pos.z + trunk_h + 9.0)
            self.obstacles.append(ObstacleBox(f"Tree_{i}", min_pt, max_pt, tree_root))

    def _build_rocks(self):
        c_rock = Vec4(0.55, 0.58, 0.60, 1.0)
        c_rock_dark = Vec4(0.45, 0.48, 0.50, 1.0)

        rock_specs = [
            (Vec3(-35.0, 15.0, 1.6), Vec3(7.0, 6.0, 3.2), c_rock),
            (Vec3(-50.0, -10.0, 2.0), Vec3(9.0, 8.0, 4.0), c_rock_dark),
            (Vec3(25.0, -12.0, 1.2), Vec3(6.0, 5.0, 2.4), c_rock),
            (Vec3(-18.0, -28.0, 1.5), Vec3(5.5, 5.0, 3.0), c_rock_dark),
            (Vec3(55.0, 10.0, 2.5), Vec3(10.0, 8.0, 5.0), c_rock),
        ]

        for i, (pos, size, col) in enumerate(rock_specs):
            rock = self.root.attachNewNode(create_cube_geom(size.x, size.y, size.z, col))
            rock.setPos(pos)
            hx, hy, hz = size.x * 0.5, size.y * 0.5, size.z * 0.5
            min_pt = Vec3(pos.x - hx, pos.y - hy, pos.z - hz)
            max_pt = Vec3(pos.x + hx, pos.y + hy, pos.z + hz)
            self.obstacles.append(ObstacleBox(f"Rock_{i}", min_pt, max_pt, rock))
            # Rock top is perchable!
            self.surfaces.append(PerchSurface(f"RockTop_{i}", Vec3(pos.x, pos.y, pos.z + hz), Vec3(hx, hy, 0.4), "ROCK"))

    def _build_bushes(self):
        c_bush = Vec4(0.20, 0.50, 0.16, 1.0)
        bush_locs = [
            Vec3(5.0, 12.0, 1.0), Vec3(-22.0, 5.0, 1.2), Vec3(18.0, -5.0, 1.0),
            Vec3(-12.0, -15.0, 1.1), Vec3(28.0, 22.0, 1.3), Vec3(-32.0, -52.0, 1.0)
        ]
        for i, pos in enumerate(bush_locs):
            b = self.root.attachNewNode(create_cube_geom(3.5, 3.5, 2.2, c_bush))
            b.setPos(pos)
            hx, hy, hz = 1.75, 1.75, 1.1
            min_pt = Vec3(pos.x - hx, pos.y - hy, pos.z - hz)
            max_pt = Vec3(pos.x + hx, pos.y + hy, pos.z + hz)
            self.obstacles.append(ObstacleBox(f"Bush_{i}", min_pt, max_pt, b))

    def raycast(self, origin: Vec3, direction: Vec3, max_dist: float = 40.0) -> float:
        """Fast raycast against natural obstacles, ground, and outer boundaries."""
        dir_norm = Vec3(direction)
        dir_norm.normalize()

        closest = max_dist
        hs = self.half_size

        # 1. Ground collision
        if dir_norm.z < -1e-6:
            t_ground = (0.0 - origin.z) / dir_norm.z
            if 0.0 < t_ground < closest:
                hit_x = origin.x + t_ground * dir_norm.x
                hit_y = origin.y + t_ground * dir_norm.y
                if -hs <= hit_x <= hs and -hs <= hit_y <= hs:
                    closest = t_ground

        # 2. Outer forest boundary walls
        if abs(dir_norm.x) > 1e-6:
            for bx in (-hs, hs):
                t = (bx - origin.x) / dir_norm.x
                if 0.0 < t < closest:
                    closest = t

        if abs(dir_norm.y) > 1e-6:
            for by in (-hs, hs):
                t = (by - origin.y) / dir_norm.y
                if 0.0 < t < closest:
                    closest = t

        # 3. Obstacle boxes (Trees, Rocks, Hills)
        for box in self.obstacles:
            tmin, tmax = -1e9, 1e9

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

            if tmax >= max(0.0, tmin) and tmin > 0.0 and tmin < closest:
                closest = tmin

        return closest

    def get_surface_below(self, pos: Vec3) -> Tuple[float, str]:
        """Returns (surface_z, surface_type) directly under the fly position."""
        best_z = 0.0  # default ground level
        best_type = "GROUND"

        for s in self.surfaces:
            if abs(pos.x - s.center.x) <= s.half_extents.x and abs(pos.y - s.center.y) <= s.half_extents.y:
                top_z = s.center.z + s.half_extents.z
                if top_z > best_z and top_z <= pos.z + 0.8:
                    best_z = top_z
                    best_type = s.surface_type

        return best_z, best_type
