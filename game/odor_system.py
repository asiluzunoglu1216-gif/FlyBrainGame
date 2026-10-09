"""3D Spatial Odor Dispersion and Food Ecosystem System.

Simulates physical odor plumes diffusing from organic fruit and sugar sources.
Odor is carried downwind by the meadow breeze and forms a continuous 3D spatial gradient:
    C(d) = I_0 / (1.0 + 0.12 * d + 0.015 * d^2)
where d is the effective upwind distance from the food source to the antennae.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from panda3d.core import Vec3, Vec4, NodePath


@dataclass
class FoodSource:
    name: str
    pos: Vec3
    odor_type: str            # e.g. "ETHYL_ACETATE" (Apple), "ISOAMYL_ACETATE" (Banana)
    odor_intensity: float     # Plume emission strength (1.0 - 2.5)
    sweetness: float          # Taste profile (0.0 to 1.0)
    energy_capacity: float    # Total calories contained
    radius: float = 1.6
    color: Vec4 = Vec4(0.9, 0.2, 0.2, 1.0)
    eaten_progress: float = 0.0  # 0.0 = intact, 1.0 = fully consumed
    active: bool = True
    respawn_timer: float = 0.0
    node: Optional[NodePath] = None


class OdorEcosystemManager:
    """Manages food sources and calculates 3D odor concentration gradients at the antennae."""

    def __init__(self, render: Optional[NodePath] = None):
        self.render = render
        self.foods: List[FoodSource] = []
        self._init_default_foods()

    def _init_default_foods(self):
        """Initializes diverse fruit and sugar food sources scattered across the ecosystem."""
        food_specs = [
            ("APPLE", Vec3(14.0, 16.0, 0.8), "ETHYL_ACETATE", 2.2, 0.85, 25.0, 1.8, Vec4(0.92, 0.15, 0.15, 1.0)),
            ("BANANA", Vec3(-18.0, 22.0, 0.8), "ISOAMYL_ACETATE", 2.5, 0.90, 30.0, 1.9, Vec4(0.95, 0.88, 0.15, 1.0)),
            ("STRAWBERRY", Vec3(-12.0, -14.0, 0.8), "ETHYL_BUTYRATE", 2.0, 0.80, 20.0, 1.5, Vec4(0.95, 0.20, 0.35, 1.0)),
            ("GRAPE", Vec3(22.0, -12.0, 0.8), "METHYL_ANTHRANILATE", 1.8, 0.75, 18.0, 1.4, Vec4(0.55, 0.15, 0.75, 1.0)),
            ("PEACH", Vec3(4.0, 32.0, 0.8), "LACTONE_ESTER", 2.1, 0.85, 24.0, 1.8, Vec4(0.95, 0.55, 0.35, 1.0)),
            ("SUGAR_DROP", Vec3(-22.0, -5.0, 0.6), "SUCROSE_SWEET", 1.5, 1.00, 35.0, 1.2, Vec4(0.95, 0.95, 0.95, 1.0)),
        ]

        for name, pos, o_type, intensity, sweet, energy, rad, col in food_specs:
            self.foods.append(FoodSource(
                name=name,
                pos=pos,
                odor_type=o_type,
                odor_intensity=intensity,
                sweetness=sweet,
                energy_capacity=energy,
                radius=rad,
                color=col
            ))

    def sync_from_food_system(self, food_items: List[Any]):
        """Synchronizes active food positions and states from FoodSystem."""
        name_map = {f.name: f for f in self.foods}
        for item in food_items:
            if item.name in name_map:
                name_map[item.name].pos = Vec3(item.pos)
                name_map[item.name].active = item.active

    def update(self, dt: float):
        """Updates food respawn timers and visual shrinking during feeding."""
        for food in self.foods:
            if not food.active:
                food.respawn_timer -= dt
                if food.respawn_timer <= 0.0:
                    # Respawn food at its location with full capacity
                    food.active = True
                    food.eaten_progress = 0.0
                    food.respawn_timer = 0.0
                    if food.node:
                        food.node.show()
                        food.node.setScale(1.0)

    def compute_odor_at_point(
        self,
        point: Vec3,
        heading_deg: float,
        wind_dir: Vec3,
        wind_speed: float
    ) -> Tuple[float, float, float, Optional[FoodSource]]:
        """Calculates bilateral odor concentration (total, left_antenna, right_antenna) and nearest source.

        Takes wind advection into account: points downwind from a food source experience
        stronger odor plumes than upwind points.
        """
        rad = math.radians(heading_deg)
        fwd = Vec3(math.cos(rad), math.sin(rad), 0.0)
        right = Vec3(math.sin(rad), -math.cos(rad), 0.0)

        # Antenna positions (~0.3 units left/right of head)
        ant_l = point + fwd * 0.4 - right * 0.25
        ant_r = point + fwd * 0.4 + right * 0.25

        total_conc = 0.0
        conc_l = 0.0
        conc_r = 0.0
        nearest_food: Optional[FoodSource] = None
        min_dist = 1e9

        for food in self.foods:
            if not food.active:
                continue

            to_fly = point - food.pos
            dist = to_fly.length()

            if dist < min_dist:
                min_dist = dist
                nearest_food = food

            # Wind advection: food plume drifts downwind
            # Effective distance is reduced if fly is downwind of the food
            wind_dot = to_fly.dot(wind_dir) / max(0.001, dist)
            advection_factor = 1.0 + max(0.0, wind_dot * wind_speed * 0.35)

            # Spatial concentration gradient
            c_center = (food.odor_intensity * advection_factor) / (1.0 + 0.12 * dist + 0.015 * (dist ** 2))
            total_conc += c_center

            dist_l = (ant_l - food.pos).length()
            c_l = (food.odor_intensity * advection_factor) / (1.0 + 0.12 * dist_l + 0.015 * (dist_l ** 2))
            conc_l += c_l

            dist_r = (ant_r - food.pos).length()
            c_r = (food.odor_intensity * advection_factor) / (1.0 + 0.12 * dist_r + 0.015 * (dist_r ** 2))
            conc_r += c_r

        return float(total_conc), float(conc_l), float(conc_r), nearest_food

    def consume_food(self, food: FoodSource, amount: float) -> bool:
        """Consumes nutrient mass from food. Returns True if food was fully eaten."""
        if not food.active:
            return False

        food.eaten_progress = min(1.0, food.eaten_progress + amount / food.energy_capacity)
        if food.node:
            scale = max(0.2, 1.0 - food.eaten_progress * 0.7)
            food.node.setScale(scale)

        if food.eaten_progress >= 1.0:
            food.active = False
            food.respawn_timer = 60.0  # Respawns after 60 seconds
            if food.node:
                food.node.hide()
            return True
        return False

    def reset_all(self):
        """Resets all foods for a new life run."""
        for food in self.foods:
            food.active = True
            food.eaten_progress = 0.0
            food.respawn_timer = 0.0
            if food.node:
                food.node.show()
                food.node.setScale(1.0)
