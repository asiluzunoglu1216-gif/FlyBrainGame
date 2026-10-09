"""Internal Physiological State & External Physiological Sensor Model for Drosophila.

Models energy, hunger, satiety, and hydration.
Recalibrated to realistic foraging timescales:
- Flight: High energy burn (~330-450s continuous flight before lethal exhaustion)
- Walking: Moderate energy burn (~1000s)
- Perching / Resting: Low basal metabolic rate (~3300s)

Crucially:
- Hunger DOES NOT directly command velocity, turn rate, or destinations.
- Hunger modulates sensory gains (olfactory gain, gustatory gain, PAM reward valuation).
- Connectome circuits (ORNs -> PNs -> MB/LH -> DNs) produce natural emergent foraging.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExternalPhysiologicalSensors:
    """EXTERNAL PHYSIOLOGICAL SENSOR MODEL.

    Measures internal physiological states and delivers scientifically labeled
    interoceptive signals to downstream neuroendocrine and neuromodulatory circuits.
    """
    gut_fullness: float = 0.85       # 0.0 (empty) to 1.0 (replete)
    nutrient_absorption: float = 0.0 # Rate of caloric absorption from midgut
    hydration_osmolarity: float = 0.90 # Internal hemolymph osmolarity
    starvation_urgency: float = 0.0  # Non-linear urgency signal when energy < 0.25


@dataclass
class InternalPhysiologicalState:
    energy: float = 0.85          # [0.0, 1.0]: 1.0 = fully satiated, 0.0 = starved
    hydration: float = 0.90       # [0.0, 1.0]: 1.0 = fully hydrated, 0.0 = desiccated
    hunger: float = 0.15          # Derived: 1.0 - energy
    feeding_rate: float = 0.0     # Current feeding intensity (0.0 to 1.0)
    total_energy_consumed: float = 0.0
    sensors: ExternalPhysiologicalSensors = field(default_factory=ExternalPhysiologicalSensors)

    def __post_init__(self):
        self.hunger = float(max(0.0, min(1.0, 1.0 - self.energy)))
        self._sync_sensors()

    def _sync_sensors(self):
        self.sensors.gut_fullness = self.energy
        self.sensors.hydration_osmolarity = self.hydration
        self.sensors.starvation_urgency = float(max(0.0, (0.30 - self.energy) / 0.30)) if self.energy < 0.30 else 0.0

    def update(self, dt: float, locomotion_mode: str, speed: float, feeding_activity: float = 0.0):
        """Updates energy expenditure and replenishment based on physical activity."""
        # 1. Energy expenditure (Realistic biological timescale: ~5-8 minutes flight to starvation)
        if locomotion_mode == "AIRBORNE":
            # Aerodynamic flight power: baseline hovering plus speed-dependent thrust
            burn_rate = 0.0022 + 0.0010 * min(2.0, max(0.0, speed) / 6.0)
        elif locomotion_mode == "GROUNDED" and speed > 0.1:
            # Walking burns ~1/3 of flight power
            burn_rate = 0.0010
        else:
            # Resting / perching basal metabolic maintenance
            burn_rate = 0.0003

        self.energy = max(0.0, self.energy - burn_rate * dt)
        self.hydration = max(0.0, self.hydration - 0.00025 * dt)

        # 2. Feeding replenishment (active only during verified proboscis extension onto nutrient substrate)
        self.feeding_rate = max(0.0, min(1.0, feeding_activity))
        if self.feeding_rate > 0.05:
            # Sustained feeding replenishes ~12% per second of full ingestion
            gain = 0.12 * self.feeding_rate * dt
            self.energy = min(1.0, self.energy + gain)
            self.hydration = min(1.0, self.hydration + gain * 0.6)
            self.total_energy_consumed += gain
            self.sensors.nutrient_absorption = self.feeding_rate * 0.12
        else:
            self.sensors.nutrient_absorption = 0.0

        # 3. Hunger level derived directly from energy deficit
        self.hunger = float(max(0.0, min(1.0, 1.0 - self.energy)))
        self._sync_sensors()

    @property
    def olfactory_gain(self) -> float:
        """Modulates sensitivity to food odors. Hungry flies exhibit up to 1.8x heightened sensitivity."""
        return 1.0 + self.hunger * 0.8

    @property
    def gustatory_gain(self) -> float:
        """Modulates taste sensitivity. Depleted flies exhibit heightened proboscis reflexes."""
        return 1.0 + self.hunger * 0.9

    @property
    def dopamine_appetitive_gain(self) -> float:
        """Modulates PAM dopaminergic reward strength during nutrient intake."""
        return 1.0 + self.hunger * 1.5

    def reset_for_retry(self):
        """Resets physical body variables for a reincarnated life cycle."""
        self.energy = 0.85
        self.hydration = 0.90
        self.hunger = 0.15
        self.feeding_rate = 0.0
        self._sync_sensors()
