"""Multi-Modal Gustatory Sensory System for Drosophila.

Based on adult Drosophila connectomics and neurobiology (Dethier 1976, Jaeger et al. 2018,
Sterne et al. 2021).
Taste in Drosophila is mediated by gustatory receptor neurons (GRNs) housed in sensilla
on the tarsi (legs), labellum (proboscis tip), and internal pharyngeal sense organs.

Modalities:
1. Sweet / Nutrient (Sucrose, Fructose, Trehalose) -> Appetitive, drives PER and feeding
2. Bitter / Aversive (Caffeine, Plant Alkaloids) -> Aversive, inhibits feeding, drives avoidance
3. Water / Low Osmolality (Hydration) -> Appetitive when thirsty
4. Salt (NaCl) -> Low salt (< 100 mM) appetitive; high salt (> 300 mM) aversive

Strict Physical Constraint:
Taste occurs ONLY when physical contact is established between tarsal/labellar surfaces
and a chemical substrate. Spatial proximity alone is NOT taste.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from panda3d.core import Vec3, Vec4


@dataclass
class TasteProfile:
    sweet: float = 0.0      # 0.0 to 1.0 (Sucrose / Fructose)
    bitter: float = 0.0     # 0.0 to 1.0 (Toxic / Aversive)
    water: float = 0.0      # 0.0 to 1.0 (Moisture / Hydration)
    salt: float = 0.0       # 0.0 to 1.0 (Electrolytes)
    nutrient_density: float = 1.0  # Caloric value


@dataclass
class GustatorySensoryOutput:
    # Tarsal (Leg) Taste Readings (FL, FR, ML, MR, RL, RR)
    tarsal_sweet: float = 0.0
    tarsal_bitter: float = 0.0
    tarsal_water: float = 0.0
    tarsal_salt: float = 0.0
    tarsal_contact_any: bool = False

    # Labellar (Proboscis Tip) Taste Readings
    labellar_sweet: float = 0.0
    labellar_bitter: float = 0.0
    labellar_water: float = 0.0
    labellar_salt: float = 0.0
    labellar_contact: bool = False

    # Pharyngeal Ingestion Sensors
    pharyngeal_ingestion_rate: float = 0.0
    gut_nutrient_intake: float = 0.0


# Standard profiles for ecosystem substrates
SUBSTRATE_TASTE_PROFILES: Dict[str, TasteProfile] = {
    "APPLE": TasteProfile(sweet=0.88, bitter=0.02, water=0.75, salt=0.05, nutrient_density=25.0),
    "BANANA": TasteProfile(sweet=0.92, bitter=0.01, water=0.65, salt=0.08, nutrient_density=30.0),
    "STRAWBERRY": TasteProfile(sweet=0.80, bitter=0.05, water=0.85, salt=0.04, nutrient_density=20.0),
    "GRAPE": TasteProfile(sweet=0.85, bitter=0.03, water=0.80, salt=0.06, nutrient_density=22.0),
    "PEACH": TasteProfile(sweet=0.86, bitter=0.02, water=0.78, salt=0.05, nutrient_density=24.0),
    "SUGAR_DROP": TasteProfile(sweet=1.00, bitter=0.00, water=0.10, salt=0.01, nutrient_density=35.0),
    "DIRT_GROUND": TasteProfile(sweet=0.00, bitter=0.15, water=0.10, salt=0.12, nutrient_density=0.0),
    "POND_WATER": TasteProfile(sweet=0.00, bitter=0.00, water=1.00, salt=0.02, nutrient_density=0.0),
    "MOSS_ROCK": TasteProfile(sweet=0.05, bitter=0.20, water=0.40, salt=0.08, nutrient_density=1.0),
}


class GustatorySystem:
    """Manages tarsal and labellar physical contact sampling and taste transduction."""

    def __init__(self):
        pass

    def compute_taste(
        self,
        fly_pos: Vec3,
        fly_is_grounded: bool,
        proboscis_extension: float,
        foods: List[Tuple[str, Vec3, float]],  # (name, pos, radius)
        surface_type: str,
        surface_dist: float,
        leg_contacts: Tuple[bool, bool, bool, bool, bool, bool]
    ) -> GustatorySensoryOutput:
        """Evaluates physical taste contact across 6 tarsi and the proboscis labellum."""
        out = GustatorySensoryOutput()

        # 1. Determine which substrate the fly's legs are physically contacting
        contacting_food_name: Optional[str] = None
        contacting_food_dist = 1e9

        # A. Check food surface contact
        for name, f_pos, f_radius in foods:
            to_food = fly_pos - f_pos
            dist = to_food.length()
            # Physical tarsal contact: fly elevation and horizontal radius touch food mesh
            if dist < f_radius + 0.65 and (fly_is_grounded or surface_dist < 0.45):
                if dist < contacting_food_dist:
                    contacting_food_dist = dist
                    contacting_food_name = name

        # B. Tarsal Taste Sampling
        if contacting_food_name is not None:
            profile = SUBSTRATE_TASTE_PROFILES.get(contacting_food_name, SUBSTRATE_TASTE_PROFILES["APPLE"])
            # Legs are touching sweet food substrate!
            if any(leg_contacts) or fly_is_grounded:
                out.tarsal_sweet = profile.sweet
                out.tarsal_bitter = profile.bitter
                out.tarsal_water = profile.water
                out.tarsal_salt = profile.salt
                out.tarsal_contact_any = True
        elif fly_is_grounded or surface_dist < 0.35:
            # Touching ground or pond
            profile_name = "POND_WATER" if "POND" in surface_type else "DIRT_GROUND"
            profile = SUBSTRATE_TASTE_PROFILES.get(profile_name, SUBSTRATE_TASTE_PROFILES["DIRT_GROUND"])
            if any(leg_contacts) or fly_is_grounded:
                out.tarsal_sweet = profile.sweet
                out.tarsal_bitter = profile.bitter
                out.tarsal_water = profile.water
                out.tarsal_salt = profile.salt
                out.tarsal_contact_any = True

        # C. Labellar (Proboscis Tip) Sampling
        # The proboscis must physically extend downward to touch the substrate
        # Proboscis length is ~0.5 units when extended
        if proboscis_extension > 0.25:
            labellum_reach = 0.25 + proboscis_extension * 0.45
            if contacting_food_name is not None and contacting_food_dist < (f_radius + labellum_reach):
                profile = SUBSTRATE_TASTE_PROFILES.get(contacting_food_name, SUBSTRATE_TASTE_PROFILES["APPLE"])
                out.labellar_sweet = profile.sweet * proboscis_extension
                out.labellar_bitter = profile.bitter * proboscis_extension
                out.labellar_water = profile.water * proboscis_extension
                out.labellar_salt = profile.salt * proboscis_extension
                out.labellar_contact = True

                # Ingestion rate scales with labellar contact and proboscis extension
                out.pharyngeal_ingestion_rate = float(min(1.0, proboscis_extension * profile.sweet))
                out.gut_nutrient_intake = out.pharyngeal_ingestion_rate * profile.nutrient_density

            elif (fly_is_grounded or surface_dist < 0.25) and "POND" in surface_type:
                # Drinking water from pond
                profile = SUBSTRATE_TASTE_PROFILES["POND_WATER"]
                out.labellar_water = profile.water * proboscis_extension
                out.labellar_contact = True
                out.pharyngeal_ingestion_rate = float(proboscis_extension * 0.8)

        return out
