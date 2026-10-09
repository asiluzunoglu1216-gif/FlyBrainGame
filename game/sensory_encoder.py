"""Sensory Encoders for Drosophila Connectome Simulation.

Supports two modes:
1. FEATURE_MODE (Default & robust):
   Computes looming intensity from raycasts/distances and directly stimulates
   identified sensory projection neurons:
   - LC4 / LPLC2: Fast looming & approaching obstacles (escape)
   - LC10a: Visual target tracking (fruits / objects)
   - LC9 / Airflow / JO: Retinal optic flow & antennal wind forward drive
   - ORN / ALPN (DM1, DM2, DM4, DL5, DP1m): Bilateral olfactory fruit odors
   - BM_Taste: SEZ gustatory sucrose feeding reflex circuit
   - LgLG1-8 / LgAG: 6-leg mechanosensory and tactile surface contact
   - DNp02: Surface approach & landing deceleration circuit
   - PAM / PPL1: Dopaminergic appetitive reward and aversive threat reinforcement

2. EYE_MODE (Experimental):
   Downsamples visual field into a 1-D azimuthal panorama and drives
   photoreceptors using flybrain.eyes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np
from panda3d.core import Vec3

from flybrain import FlyBrain
from flybrain.eyes import Eyes, Blob


@dataclass
class SensoryInput:
    # 1. Spatial Obstacle Sensing
    dist_left: float = 50.0       # Distance to left obstacle (units)
    dist_center: float = 50.0     # Distance to center obstacle (units)
    dist_right: float = 50.0      # Distance to right obstacle (units)
    max_range: float = 40.0       # Max sensor range

    # 2. Visual Target (Fruit/Sphere) Tracking
    target_visible: bool = False
    target_azimuth: float = 0.0   # -1.0 (far left) .. +1.0 (far right)
    target_dist: float = 50.0
    target_pos: Vec3 = field(default_factory=lambda: Vec3(0, 0, 1.0))

    # 3. Measured looming intensities (for telemetry / HUD display)
    stimulus_l: float = 0.0
    stimulus_r: float = 0.0
    target_stim_l: float = 0.0
    target_stim_r: float = 0.0
    fwd_stimulus: float = 0.0     # Voltage injected into forward circuit
    fwd_source: str = "NONE"      # Reason/source for forward stimulus
    optic_flow: float = 0.0       # Retinal visual motion energy (rad/s)
    airspeed: float = 0.0         # Relative air velocity past antennae (units/s)
    ambient_breeze: float = 0.0   # Environmental meadow wind (units/s)
    surface_dist: float = 50.0    # Distance to solid surface beneath fly
    surface_contact: bool = False # Physical contact with ground/branch/food
    surface_type: str = "AIR"     # "GROUND", "BRANCH", "WATER", "FOOD", "AIR"
    frog_looming: float = 0.0
    env_motion: float = 0.0       # Environmental parallax motion
    locomotion_mode: str = "AIRBORNE" # "AIRBORNE" or "GROUNDED"
    fallback_active: bool = False

    # 4. Olfactory Input (3D Odor Plume & Bilateral Antennae)
    odor_conc: float = 0.0        # Total odor concentration at fly head
    odor_conc_l: float = 0.0      # Odor concentration at Left Antenna
    odor_conc_r: float = 0.0      # Odor concentration at Right Antenna
    odor_type: str = "NONE"       # Chemical identifier (e.g. "ETHYL_ACETATE")

    # 5. Gustatory & Feeding Input
    taste_sugar: float = 0.0      # Sweetness detected by proboscis / labellum (0.0 to 1.0)
    leg_taste: float = 0.0        # Sweetness detected by tarsal taste hairs (0.0 to 1.0)

    # 6. Six Individual Leg Contact Sensors (FL, FR, ML, MR, RL, RR)
    leg_contacts: Tuple[bool, bool, bool, bool, bool, bool] = (False, False, False, False, False, False)

    # 7. Internal Physiological State Modulation
    energy: float = 0.85
    hunger: float = 0.15
    hydration: float = 0.90
    olfactory_gain: float = 1.0   # Multiplier for ORN/PN sensitivity
    gustatory_gain: float = 1.0   # Multiplier for taste sensitivity

    # 8. Reinforcement & Attack States
    predator_attack_active: bool = False
    pam_reward: float = 0.0       # Dopaminergic reward (feeding)
    ppl1_punish: float = 0.0      # Dopaminergic punishment (threat/attack)

    # 9. Extended Virtual Compound Eye Fields
    eye_flow_l: float = 0.0
    eye_flow_r: float = 0.0
    eye_loom_l: float = 0.0
    eye_loom_r: float = 0.0
    target_elevation: float = 0.0

    # 10. Multi-Modal Gustatory Fields
    tarsal_sweet: float = 0.0
    tarsal_bitter: float = 0.0
    tarsal_water: float = 0.0
    tarsal_salt: float = 0.0
    labellar_sweet: float = 0.0
    labellar_bitter: float = 0.0
    labellar_water: float = 0.0
    labellar_salt: float = 0.0
    pharyngeal_ingestion: float = 0.0

    # 11. Central Complex Compass & Wind
    fly_heading_deg: float = 0.0
    jo_wind_airspeed: float = 0.0


class FeatureEncoder:
    """FEATURE_MODE: Directly stimulates identified projection and sensory neurons."""

    def __init__(self, brain: FlyBrain):
        self.brain = brain
        types = set(brain.cell_type)

        # 1. Visual Looming & Escape Circuits
        self.lc4_lplc2_l = brain.cells(["LC4", "LPLC2"], side="L")
        self.lc4_lplc2_r = brain.cells(["LC4", "LPLC2"], side="R")

        # 2. Visual Object Tracking (LC10 family: LC10a, LC10b, LC10c)
        self.lc10a_l = brain.cells(["LC10a"], side="L")
        self.lc10a_r = brain.cells(["LC10a"], side="R")
        self.lc10_family_l = brain.cells(["LC10a", "LC10b", "LC10c"], side="L")
        self.lc10_family_r = brain.cells(["LC10a", "LC10b", "LC10c"], side="R")

        # 3. Forward Population Drive Circuits & Optic Flow (LC9, LPLC1)
        self.lc9_l = brain.cells(["LC9"], side="L")
        self.lc9_r = brain.cells(["LC9"], side="R")
        self.lc9_all = brain.cells(["LC9"])
        self.flow_circuit = brain.cells(["LC9", "LPLC1"])
        self.fwd_circuit = brain.cells(["PVLP137", "PLP300m", "CB4105"])

        # Johnston's Organ mechanosensory (JO-C/E wind/gravity, JO-A/B vibration)
        jo_wind_types = [t for t in types if "JO-C" in str(t) or "JO-E" in str(t)]
        self.jo_wind = brain.cells(jo_wind_types) if len(jo_wind_types) > 0 else np.array([], dtype=int)
        jo_sound_types = [t for t in types if "JO-A" in str(t) or "JO-B" in str(t)]
        self.jo_sound = brain.cells(jo_sound_types) if len(jo_sound_types) > 0 else np.array([], dtype=int)

        # Central Complex Compass Heading (EPG and PEN ring attractor)
        self.epg_cells = brain.cells(["EPG"])
        self.pen_cells = brain.cells(["PEN_a(PEN1)", "PEN_b(PEN2)"])

        # 4. Olfactory Receptor Neurons (ORNs) & Antennal Lobe Projection Neurons (ALPNs)
        fruit_orn_names = ["ORN_DM1", "ORN_DM2", "ORN_DM4", "ORN_DL5", "ORN_DP1m"]
        self.orn_fruit_l = brain.cells(fruit_orn_names, side="L")
        self.orn_fruit_r = brain.cells(fruit_orn_names, side="R")

        fruit_pn_names = ["DM1_lPN", "DM2_lPN", "DM4_adPN", "DM4_vPN", "DL5_adPN"]
        self.alpn_fruit_l = brain.cells(fruit_pn_names, side="L")
        self.alpn_fruit_r = brain.cells(fruit_pn_names, side="R")

        # 5. Gustatory Sensory Neurons (SEZ BM_Taste, BM_Hau, BM_MaPa)
        self.bm_taste = brain.cells(["BM_Taste", "BM_Hau", "BM_MaPa"])

        # 6. Six-Leg Mechanosensory Neurons (LgLG / LgAG)
        self.lg_front_l = brain.cells(["LgLG1a", "LgLG1b", "LgLG2"], side="L")
        self.lg_front_r = brain.cells(["LgLG1a", "LgLG1b", "LgLG2"], side="R")
        self.lg_mid_l = brain.cells(["LgLG3", "LgLG4", "LgLG5"], side="L")
        self.lg_mid_r = brain.cells(["LgLG3", "LgLG4", "LgLG5"], side="R")
        self.lg_rear_l = brain.cells(["LgLG6", "LgLG7", "LgLG8"], side="L")
        self.lg_rear_r = brain.cells(["LgLG6", "LgLG7", "LgLG8"], side="R")
        self.lg_contact_all = brain.cells(["LgLG1a", "LgLG1b", "LgLG2", "LgLG3", "LgLG4", "LgLG5", "LgLG6", "LgLG7", "LgLG8"])

        # 7. Landing & Deceleration Circuit (DNp02)
        self.dnp02_l = brain.cells(["DNp02"], side="L")
        self.dnp02_r = brain.cells(["DNp02"], side="R")
        self.dnp02_all = brain.cells(["DNp02"])

        # 8. Dopaminergic Reinforcement Circuits
        pam_types = [t for t in types if "PAM" in str(t)]
        ppl1_types = [t for t in types if "PPL1" in str(t)]
        self.pam_cells = brain.cells(pam_types) if len(pam_types) > 0 else np.array([], dtype=int)
        self.ppl1_cells = brain.cells(ppl1_types) if len(ppl1_types) > 0 else np.array([], dtype=int)

        self.prev_dist_l: Optional[float] = None
        self.prev_dist_r: Optional[float] = None
        self.prev_dist_c: Optional[float] = None

    def encode(self, sensory: SensoryInput) -> List[Tuple[np.ndarray, float]]:
        """Converts sensory inputs into [(cell_indices, voltage_amount), ...] pairs."""
        injections = []
        max_r = sensory.max_range

        if self.prev_dist_l is None:
            self.prev_dist_l = sensory.dist_left
            self.prev_dist_r = sensory.dist_right
            self.prev_dist_c = sensory.dist_center

        # Looming: rate of approach (-ddist)
        # Biological reality: An obstacle cannot physically approach the fly faster
        # than the fly's own flight speed plus predator speed. Large raycast distance drops
        # caused by yaw rotation / obstacle parallax must be clamped to physical limits
        # to prevent spurious looming shocks and escape ping-pong spinning!
        max_physical_drop = max(0.4, (sensory.airspeed + 3.0) * 0.05)
        raw_drop_l = max(0.0, self.prev_dist_l - sensory.dist_left)
        raw_drop_r = max(0.0, self.prev_dist_r - sensory.dist_right)
        raw_drop_c = max(0.0, self.prev_dist_c - sensory.dist_center)

        growth_l = min(max_physical_drop, raw_drop_l) / max_r
        growth_r = min(max_physical_drop, raw_drop_r) / max_r
        growth_c = min(max_physical_drop, raw_drop_c) / max_r

        self.prev_dist_l = sensory.dist_left
        self.prev_dist_r = sensory.dist_right
        self.prev_dist_c = sensory.dist_center

        # Biological looming model:
        # 1. Emergency proximity: only fires when an obstacle enters critical close range (< 10.0 units)
        emerg_thresh = 10.0
        emerg_l = max(0.0, (emerg_thresh - sensory.dist_left) / emerg_thresh)
        emerg_r = max(0.0, (emerg_thresh - sensory.dist_right) / emerg_thresh)
        emerg_c = max(0.0, (emerg_thresh - sensory.dist_center) / emerg_thresh)

        # 2. Dynamic looming from rapid angular expansion (growth)
        loom_l = growth_l * 3.0 if growth_l > 0.02 else 0.0
        loom_r = growth_r * 3.0 if growth_r > 0.02 else 0.0
        loom_c = growth_c * 2.5 if growth_c > 0.02 else 0.0

        # Compute left and right looming stimulation (LC4 / LPLC2)
        # Combines raycast distance rate-of-expansion and compound eye retinal angular expansion
        eye_l = sensory.eye_loom_l * 0.60
        eye_r = sensory.eye_loom_r * 0.60
        stim_l = np.clip(emerg_l * 0.85 + loom_l + emerg_c * 0.4 + loom_c * 0.6 + eye_l, 0.0, 0.85)
        stim_r = np.clip(emerg_r * 0.85 + loom_r + emerg_c * 0.4 + loom_c * 0.6 + eye_r, 0.0, 0.85)

        sensory.stimulus_l = float(stim_l)
        sensory.stimulus_r = float(stim_r)

        if stim_l > 0.08:
            injections.append((self.lc4_lplc2_l, float(stim_l)))
        if stim_r > 0.08:
            injections.append((self.lc4_lplc2_r, float(stim_r)))

        # 3. Dynamic Multi-Channel Forward Population Drive:
        # Combines retinal optic flow (LC9 / LPLC1 -> DNp09) and antennal airflow (fwd_circuit + JO -> DNg100).
        fwd_voltage = 0.0
        sources = []

        if stim_l < 0.35 and stim_r < 0.35:
            # A. Retinal Optic Flow -> LC9 + LPLC1
            total_flow = max(sensory.optic_flow, (sensory.eye_flow_l + sensory.eye_flow_r) * 0.5)
            if total_flow > 0.01 and len(self.flow_circuit) > 0:
                flow_v = min(0.35, total_flow * 0.55)
                if flow_v > 0.04:
                    injections.append((self.flow_circuit, float(flow_v)))
                    fwd_voltage = max(fwd_voltage, flow_v)
                    sources.append(f"FLOW({total_flow:.2f})")

            # B. Antennal Airflow & Meadow Breeze -> fwd_circuit (PVLP/PLP/CB) + JO-C/E
            eff_airspeed = max(sensory.airspeed, sensory.jo_wind_airspeed)
            if eff_airspeed > 0.10:
                air_v = min(0.32, eff_airspeed * 0.11)
                if air_v > 0.04:
                    if len(self.fwd_circuit) > 0:
                        injections.append((self.fwd_circuit, float(air_v)))
                    if len(self.jo_wind) > 0:
                        injections.append((self.jo_wind, float(air_v * 0.65)))
                    fwd_voltage = max(fwd_voltage, air_v)
                    sources.append(f"AIR({eff_airspeed:.1f})")

        sensory.fwd_stimulus = float(fwd_voltage)
        sensory.fwd_source = "+".join(sources) if sources else "NONE"

        # 4. Central Complex Compass Heading (EPG Ring Attractor)
        if len(self.epg_cells) > 0 and sensory.fly_heading_deg != 0.0:
            norm_head = (sensory.fly_heading_deg % 360.0) / 360.0
            wedge_idx = int(norm_head * len(self.epg_cells)) % len(self.epg_cells)
            # Stimulate 2 adjacent wedges to form a smooth compass bump
            active_epg = self.epg_cells[np.array([wedge_idx, (wedge_idx + 1) % len(self.epg_cells)])]
            injections.append((active_epg, 0.12))

        # 5. Six Individual Leg Contact Sensors (LgLG1-8)
        # leg_contacts = (FL, FR, ML, MR, RL, RR)
        c_fl, c_fr, c_ml, c_mr, c_rl, c_rr = sensory.leg_contacts
        leg_v = 0.24 if sensory.surface_contact else 0.14

        if c_fl and len(self.lg_front_l) > 0:
            injections.append((self.lg_front_l, leg_v))
        if c_fr and len(self.lg_front_r) > 0:
            injections.append((self.lg_front_r, leg_v))
        if c_ml and len(self.lg_mid_l) > 0:
            injections.append((self.lg_mid_l, leg_v))
        if c_mr and len(self.lg_mid_r) > 0:
            injections.append((self.lg_mid_r, leg_v))
        if c_rl and len(self.lg_rear_l) > 0:
            injections.append((self.lg_rear_l, leg_v))
        if c_rr and len(self.lg_rear_r) > 0:
            injections.append((self.lg_rear_r, leg_v))

        # Fallback general surface contact injection if no per-leg contact specified
        if sensory.surface_contact and not any(sensory.leg_contacts):
            if len(self.lg_contact_all) > 0:
                injections.append((self.lg_contact_all, 0.22))

        # 6. Visual Target Tracking via LC10 Family (LC10a, LC10b, LC10c)
        t_stim_l = 0.0
        t_stim_r = 0.0
        if sensory.target_visible and sensory.target_dist < 38.0:
            t_intensity = float(np.clip(1.0 - sensory.target_dist / 38.0, 0.0, 0.85))
            az = sensory.target_azimuth
            target_cells_l = self.lc10_family_l if len(self.lc10_family_l) > 0 else self.lc10a_l
            target_cells_r = self.lc10_family_r if len(self.lc10_family_r) > 0 else self.lc10a_r

            if abs(az) > 0.10:
                if az > 0:
                    # Target on right -> stimulate right visual tracking circuit
                    t_stim_r = t_intensity * abs(az)
                    injections.append((target_cells_r, t_stim_r))
                else:
                    # Target on left -> stimulate left visual tracking circuit
                    t_stim_l = t_intensity * abs(az)
                    injections.append((target_cells_l, t_stim_l))
            else:
                t_stim_l = t_intensity * 0.30
                t_stim_r = t_intensity * 0.30
                injections.append((target_cells_l, t_stim_l))
                injections.append((target_cells_r, t_stim_r))

        sensory.target_stim_l = float(t_stim_l)
        sensory.target_stim_r = float(t_stim_r)

        # 7. Bilateral Olfactory Input: Fruit ORNs + ALPNs modulated by internal hunger gain
        gain_olf = sensory.olfactory_gain
        c_l = sensory.odor_conc_l * gain_olf
        c_r = sensory.odor_conc_r * gain_olf

        if c_l > 0.08:
            v_l = float(min(0.15, c_l * 0.06))
            if len(self.alpn_fruit_l) > 0:
                injections.append((self.alpn_fruit_l, v_l))
            if len(self.orn_fruit_l) > 0:
                injections.append((self.orn_fruit_l, v_l * 0.6))

        if c_r > 0.08:
            v_r = float(min(0.15, c_r * 0.06))
            if len(self.alpn_fruit_r) > 0:
                injections.append((self.alpn_fruit_r, v_r))
            if len(self.orn_fruit_r) > 0:
                injections.append((self.orn_fruit_r, v_r * 0.6))

        # 8. Gustatory Feeding Input: BM_Taste / BM_Hau / BM_MaPa (SEZ feeding motor reflex)
        effective_taste = max(sensory.taste_sugar, sensory.labellar_sweet,
                              sensory.leg_taste * 0.7, sensory.tarsal_sweet * 0.7)
        if effective_taste > 0.10:
            taste_v = float(min(0.20, effective_taste * sensory.gustatory_gain * 0.18))
            if len(self.bm_taste) > 0:
                injections.append((self.bm_taste, taste_v))

        # 9. Landing Deceleration & Approach Circuit: DNp02
        if sensory.locomotion_mode == "AIRBORNE" and sensory.surface_dist < 3.2:
            approach_v = float(min(0.35, (3.2 - sensory.surface_dist) * 0.12))
            if approach_v > 0.03 and len(self.dnp02_all) > 0:
                injections.append((self.dnp02_all, approach_v))

        # 10. Dopaminergic Reinforcement Circuits (PAM appetitive, PPL1 aversive)
        if sensory.pam_reward > 0.05 and len(self.pam_cells) > 0:
            injections.append((self.pam_cells, float(min(0.12, sensory.pam_reward * 0.10))))

        if sensory.ppl1_punish > 0.05 and len(self.ppl1_cells) > 0:
            injections.append((self.ppl1_cells, float(min(0.15, sensory.ppl1_punish * 0.12))))

        return injections


class EyeEncoder:
    """EYE_MODE (Experimental): Drives photoreceptors directly via 1-D panorama."""

    def __init__(self, brain: FlyBrain):
        self.brain = brain
        self.eyes = Eyes(brain.azimuth)

    def encode(self, sensory: SensoryInput) -> Optional[np.ndarray]:
        """Converts sensory blobs into photoreceptor drive array."""
        try:
            blobs = []
            max_r = sensory.max_range
            if sensory.dist_left < max_r:
                blobs.append(Blob(center=-0.6, half_width=0.3, darkness=0.8))
            if sensory.dist_right < max_r:
                blobs.append(Blob(center=0.6, half_width=0.3, darkness=0.8))
            if sensory.dist_center < max_r:
                blobs.append(Blob(center=0.0, half_width=0.4, darkness=0.9))
            if sensory.target_visible:
                blobs.append(Blob(center=float(np.clip(sensory.target_azimuth, -1, 1)),
                                  half_width=0.2, darkness=0.5))

            return self.eyes.drive(blobs)
        except Exception:
            return None
