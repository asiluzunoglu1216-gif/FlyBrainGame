"""Food Spawn and Feeding System for Living Ecosystem.

Maintains 3-6 active foods across natural spawn locations (ground, rocks, branches).
Provides 3D floating billboard labels above each food.
When eaten, initiates a 60-second respawn timer.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
from panda3d.core import (
    NodePath, TextNode, Vec3, Vec4, BillboardEffect
)
from .fly_model import create_cube_geom


@dataclass
class FoodItem:
    name: str
    pos: Vec3
    root: NodePath
    text_node: NodePath
    size: Tuple[float, float, float] = (1.4, 1.4, 1.3)
    active: bool = True
    eaten_time: float = 0.0
    respawn_delay: float = 60.0


FOOD_PRESETS = [
    ("APPLE", Vec4(0.92, 0.15, 0.15, 1.0), (1.4, 1.4, 1.3)),
    ("BANANA", Vec4(0.95, 0.85, 0.12, 1.0), (0.7, 2.2, 0.7)),
    ("STRAWBERRY", Vec4(0.90, 0.10, 0.25, 1.0), (1.1, 1.1, 1.4)),
    ("GRAPES", Vec4(0.55, 0.15, 0.70, 1.0), (1.3, 1.3, 1.3)),
    ("PEACH", Vec4(0.98, 0.55, 0.28, 1.0), (1.4, 1.4, 1.4)),
]

SPAWN_LOCATIONS = [
    Vec3(14.0, 16.0, 0.8),       # Meadow Clearing (Guaranteed reachable food)
    Vec3(-18.0, 22.0, 0.8),      # Meadow North-West
    Vec3(22.0, -12.0, 0.8),      # Meadow South-East
    Vec3(-35.0, 15.0, 3.2),      # On Flat Rock
    Vec3(40.0, -30.0, 0.8),      # Near Tree Base
    Vec3(-20.0, -45.0, 0.8),     # Pond Edge
    Vec3(10.0, -25.0, 6.5),      # Low Tree Branch
    Vec3(-50.0, -10.0, 4.0),     # Boulder Top
    Vec3(30.0, 45.0, 0.8),       # Sunny Glade
    Vec3(-10.0, 35.0, 5.8),      # Mossy Branch
]


class FoodSystem:
    def __init__(self, render: NodePath, max_active: int = 5):
        self.render = render
        self.max_active = max_active
        self.system_root = render.attachNewNode("FoodSystemRoot")
        self.foods: List[FoodItem] = []

        # Track fly feeding dwell time
        self._eating_target_idx: Optional[int] = None
        self._eating_start_time: float = 0.0

        self._spawn_initial_foods()

    def _create_food_model(self, name: str, color: Vec4, size: Tuple[float, float, float], pos: Vec3) -> Tuple[NodePath, NodePath]:
        """Creates low-poly food mesh with a 3D billboard text label above it."""
        fruit_root = self.system_root.attachNewNode(f"Food_{name}")
        fruit_root.setPos(pos)

        # Fruit body
        geom = create_cube_geom(size[0], size[1], size[2], color)
        body = fruit_root.attachNewNode(geom)
        body.setPos(0, 0, 0)

        # Small green stem/leaf
        c_stem = Vec4(0.20, 0.70, 0.20, 1.0)
        stem = fruit_root.attachNewNode(create_cube_geom(0.2, 0.2, 0.6, c_stem))
        stem.setPos(0, 0, size[2] * 0.5 + 0.25)

        # Floating 3D Text Label
        text = TextNode(f"Label_{name}")
        text.setText(name)
        text.setAlign(TextNode.ACenter)
        text.setTextColor(1.0, 0.95, 0.2, 1.0)

        label_np = fruit_root.attachNewNode(text)
        label_np.setScale(0.85)
        label_np.setPos(0, 0, size[2] * 0.5 + 1.2)
        # Billboard effect so text always faces the viewer
        label_np.setEffect(BillboardEffect.makePointEye())

        return fruit_root, label_np

    def _spawn_initial_foods(self):
        # Guarantee meadow clearing food (Apple) is always active, sample remaining
        remaining = [p for p in SPAWN_LOCATIONS if p != SPAWN_LOCATIONS[0]]
        chosen_spawns = [SPAWN_LOCATIONS[0]] + random.sample(remaining, min(self.max_active - 1, len(remaining)))
        for i, pos in enumerate(chosen_spawns):
            name, color, size = FOOD_PRESETS[i % len(FOOD_PRESETS)]
            root, label = self._create_food_model(name, color, size, pos)
            self.foods.append(FoodItem(name=name, pos=pos, root=root, text_node=label, size=size, active=True))

    def update(self, dt: float, current_time: float):
        """Checks respawn timers and rotates/animates floating labels."""
        for food in self.foods:
            if not food.active:
                if current_time - food.eaten_time >= food.respawn_delay:
                    # Respawn at available spawn point
                    occupied = [f.pos for f in self.foods if f.active]
                    avail = [p for p in SPAWN_LOCATIONS if p not in occupied]
                    new_pos = random.choice(avail) if avail else food.pos

                    food.pos = new_pos
                    food.root.setPos(new_pos)
                    food.root.show()
                    food.active = True
            else:
                # Gentle floating hover animation
                hover_z = food.pos.z + 0.15 * (1.0 + random.uniform(-0.1, 0.1))
                food.root.setZ(hover_z)

    def check_feeding(
        self,
        fly_pos: Vec3,
        fly_is_landed: bool,
        current_time: float,
        proboscis_tip_pos: Optional[Vec3] = None,
        proboscis_extended: bool = True,
        proboscis_extension: float = 0.0
    ) -> Optional[str]:
        """Checks if fly is physically feeding on an active food item.

        Requirements:
        1. Food surface physical contact: Fly must be landed on or adjacent to food substrate.
        2. Neural feeding activity: Proboscis extended (PER active).
        3. Physical overlap: Actual proboscis tip collider (sphere r=0.25m) intersects
           the 3D box collider of the food item.
        4. Dwell duration: Must maintain physical contact for >= 1.2 seconds.

        Returns:
            Name of food eaten if feeding completed, else None.
        """
        labellum_radius = 0.25  # meters (proboscis tip collider radius)
        dwell_required = 1.2   # seconds

        target_idx = None
        has_neural_feeding = proboscis_extended or proboscis_extension >= 0.15

        if fly_is_landed and has_neural_feeding:
            tip = proboscis_tip_pos if proboscis_tip_pos is not None else fly_pos
            for i, food in enumerate(self.foods):
                if not food.active:
                    continue

                # Food 3D box collider extents
                hx = food.size[0] * 0.5
                hy = food.size[1] * 0.5
                hz = food.size[2] * 0.5

                # Closest point on food box surface to proboscis tip
                qx = max(food.pos.x - hx, min(food.pos.x + hx, tip.x))
                qy = max(food.pos.y - hy, min(food.pos.y + hy, tip.y))
                qz = max(food.pos.z - hz, min(food.pos.z + hz, tip.z))

                # Distance from proboscis tip collider center to food surface
                dist_to_surface = math.sqrt((tip.x - qx) ** 2 + (tip.y - qy) ** 2 + (tip.z - qz) ** 2)

                # Physical overlap: tip collider sphere touches food box collider
                if dist_to_surface <= labellum_radius:
                    target_idx = i
                    break

        if target_idx is not None:
            if self._eating_target_idx == target_idx:
                # Still physically feeding on same food item
                if current_time - self._eating_start_time >= dwell_required:
                    # Feeding successfully completed!
                    eaten_food = self.foods[target_idx]
                    eaten_food.active = False
                    eaten_food.eaten_time = current_time
                    eaten_food.root.hide()

                    self._eating_target_idx = None
                    self._eating_start_time = 0.0
                    return eaten_food.name
            else:
                # Established physical contact with a new target
                self._eating_target_idx = target_idx
                self._eating_start_time = current_time
        else:
            # Physical proboscis contact broken
            self._eating_target_idx = None
            self._eating_start_time = 0.0

        return None

    def get_active_foods(self) -> List[Tuple[str, Vec3]]:
        return [(f.name, f.pos) for f in self.foods if f.active]

    def reset_all(self):
        """Resets all foods to active."""
        for food in self.foods:
            food.active = True
            food.root.show()
        self._eating_target_idx = None
        self._eating_start_time = 0.0
