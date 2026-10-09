"""Mushroom-Body Associative Memory & Plasticity System for MaleCNS Connectome.

Implements a biologically authentic 3-factor learning rule restricted to the
Mushroom Body compartment:
    KC (Kenyon Cells) -> MBON (Mushroom Body Output Neurons)
modulated by Dopaminergic Neurons (DANs):
    - PAM (Protocerebral Anterior Medial): Appetitive reward (sugar intake)
    - PPL1 (Protocerebral Posterior Lateral): Aversive punishment (predator attack)

Persists learned synaptic weight matrices and odor traces across retries in:
    memory/plastic_synapses.npz
Storage limit: Strictly under 2 GB (uses compressed NPZ ~400 KB).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np


class MushroomBodyMemorySystem:
    def __init__(
        self,
        kc_indices: np.ndarray,
        mbon_indices: np.ndarray,
        pam_indices: np.ndarray,
        ppl1_indices: np.ndarray,
        memory_path: Path | str = "memory/plastic_synapses.npz"
    ):
        self.kc_indices = np.array(kc_indices, dtype=np.int32)
        self.mbon_indices = np.array(mbon_indices, dtype=np.int32)
        self.pam_indices = np.array(pam_indices, dtype=np.int32)
        self.ppl1_indices = np.array(ppl1_indices, dtype=np.int32)
        self.memory_path = Path(memory_path)

        self.num_kc = len(self.kc_indices)
        self.num_mbon = len(self.mbon_indices)

        # Base baseline weights (KC -> MBON)
        # In Drosophila mushroom body, baseline synapses are uniform/sparse
        self.weights = np.ones((self.num_kc, self.num_mbon), dtype=np.float32) * 0.08
        self.base_weights = np.copy(self.weights)

        # Odor representation activity trace (eligibility trace)
        self.kc_trace = np.zeros(self.num_kc, dtype=np.float32)

        # MBON valence specialization:
        # First half of MBONs project to approach/proboscis/locomotion facilitation;
        # Second half project to avoidance/escape/turning.
        self.mbon_appetitive_mask = np.zeros(self.num_mbon, dtype=np.float32)
        self.mbon_aversive_mask = np.zeros(self.num_mbon, dtype=np.float32)
        half = max(1, self.num_mbon // 2)
        self.mbon_appetitive_mask[:half] = 1.0
        self.mbon_aversive_mask[half:] = 1.0

        # Fast vectorized lookup for Kenyon Cell activity trace
        self._kc_slot_lut = np.full(170000, -1, dtype=np.int32)
        if len(self.kc_indices) > 0:
            valid_kc = self.kc_indices[self.kc_indices < 170000]
            self._kc_slot_lut[valid_kc] = np.arange(len(valid_kc), dtype=np.int32)

        # Experience statistics
        self.associations_count = 0
        self.appetitive_events = 0
        self.aversive_events = 0
        self.total_plastic_steps = 0

        # Try to load existing persisted memories from previous sessions
        self.load()

    def update_activity_trace(self, active_neurons, dt: float = 0.02):
        """Updates eligibility traces for Kenyon Cells based on current spikes."""
        decay = float(np.exp(-dt / 1.2))
        self.kc_trace *= decay

        if active_neurons is not None and len(active_neurons) > 0:
            if isinstance(active_neurons, set):
                arr = np.fromiter(active_neurons, dtype=np.int32, count=len(active_neurons))
            else:
                arr = np.asarray(active_neurons, dtype=np.int32)
            valid = arr[arr < len(self._kc_slot_lut)]
            slots = self._kc_slot_lut[valid]
            kc_slots = slots[slots >= 0]
            if len(kc_slots) > 0:
                np.add.at(self.kc_trace, kc_slots, 1.0)

        np.clip(self.kc_trace, 0.0, 3.0, out=self.kc_trace)

    def apply_reinforcement(
        self,
        pam_reward: float = 0.0,
        ppl1_punishment: float = 0.0,
        active_kc_indices: Optional[np.ndarray] = None
    ):
        """Applies 3-factor synaptic plasticity to KC->MBON synapses."""
        if pam_reward <= 0.001 and ppl1_punishment <= 0.001:
            return

        learning_rate = 0.025

        # Use explicit active KC indices or current eligibility trace
        if active_kc_indices is not None and len(active_kc_indices) > 0:
            kc_vector = np.zeros(self.num_kc, dtype=np.float32)
            mask = np.isin(self.kc_indices, active_kc_indices)
            kc_vector[mask] = 1.0
        else:
            kc_vector = self.kc_trace

        active_count = int(np.sum(kc_vector > 0.1))
        if active_count == 0:
            return

        self.total_plastic_steps += 1

        # 1. Appetitive Reinforcement (Sugar Feeding / PAM Dopamine)
        if pam_reward > 0.01:
            self.appetitive_events += 1
            # Strengthen synapses to appetitive MBONs; depress synapses to aversive MBONs
            delta_app = learning_rate * pam_reward * np.outer(kc_vector, self.mbon_appetitive_mask)
            delta_dep = learning_rate * pam_reward * 0.4 * np.outer(kc_vector, self.mbon_aversive_mask)
            self.weights += delta_app - delta_dep
            self.associations_count += 1

        # 2. Aversive Reinforcement (Predator Attack / PPL1 Dopamine)
        if ppl1_punishment > 0.01:
            self.aversive_events += 1
            # Strengthen synapses to aversive MBONs; depress synapses to appetitive MBONs
            delta_av = learning_rate * ppl1_punishment * np.outer(kc_vector, self.mbon_aversive_mask)
            delta_dep = learning_rate * ppl1_punishment * 0.4 * np.outer(kc_vector, self.mbon_appetitive_mask)
            self.weights += delta_av - delta_dep
            self.associations_count += 1

        # Bound synaptic weights to prevent runaway instability
        self.weights = np.clip(self.weights, 0.01, 0.45)

    def compute_learned_mbon_drive(self, active_kc_indices: np.ndarray) -> Tuple[float, float]:
        """Calculates learned appetitive approach and aversive avoidance drive.

        Returns:
            (appetitive_drive, aversive_drive)
        """
        if len(active_kc_indices) == 0:
            return 0.0, 0.0

        mask = np.isin(self.kc_indices, active_kc_indices)
        if not np.any(mask):
            return 0.0, 0.0

        # Sum weights from currently active Kenyon cells
        w_sub = self.weights[mask, :]  # (k, num_mbon)
        mbon_activity = np.sum(w_sub, axis=0)  # (num_mbon,)

        app_drive = float(np.sum(mbon_activity * self.mbon_appetitive_mask))
        av_drive = float(np.sum(mbon_activity * self.mbon_aversive_mask))

        return app_drive, av_drive

    def compute_mbon_injections(self, active_kc_indices: np.ndarray) -> list[tuple[np.ndarray, float]]:
        """Calculates post-synaptic currents injected into MBONs through learned plastic synapses."""
        if len(active_kc_indices) == 0 or len(self.mbon_indices) == 0:
            return []

        mask = np.isin(self.kc_indices, active_kc_indices)
        if not np.any(mask):
            return []

        # Sum weights from currently active Kenyon cells onto each MBON
        w_sub = self.weights[mask, :]
        mbon_drive = np.sum(w_sub, axis=0)  # shape: (num_mbon,)

        # Divide into appetitive and aversive groups for physiological current injection
        injections = []
        app_mask = self.mbon_appetitive_mask > 0.5
        av_mask = self.mbon_aversive_mask > 0.5

        if np.any(app_mask):
            app_drive = float(np.mean(mbon_drive[app_mask]))
            if app_drive > 0.01:
                # Moderate current to excite appetitive MBONs
                injections.append((self.mbon_indices[app_mask], min(0.20, app_drive * 0.12)))

        if np.any(av_mask):
            av_drive = float(np.mean(mbon_drive[av_mask]))
            if av_drive > 0.01:
                # Moderate current to excite aversive MBONs
                injections.append((self.mbon_indices[av_mask], min(0.20, av_drive * 0.12)))

        return injections

    def save(self) -> bool:
        """Persists learned synaptic state to disk."""
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                self.memory_path,
                weights=self.weights,
                associations_count=np.array([self.associations_count], dtype=np.int32),
                appetitive_events=np.array([self.appetitive_events], dtype=np.int32),
                aversive_events=np.array([self.aversive_events], dtype=np.int32),
                total_plastic_steps=np.array([self.total_plastic_steps], dtype=np.int32)
            )
            return True
        except Exception as e:
            print(f"[MemorySystem] Warning: Failed to save memory: {e}")
            return False

    def load(self) -> bool:
        """Loads persisted learned synaptic state from disk if present."""
        if not self.memory_path.exists():
            return False
        try:
            data = np.load(self.memory_path)
            if "weights" in data and data["weights"].shape == self.weights.shape:
                self.weights = data["weights"].astype(np.float32)
                self.associations_count = int(data["associations_count"][0]) if "associations_count" in data else 0
                self.appetitive_events = int(data["appetitive_events"][0]) if "appetitive_events" in data else 0
                self.aversive_events = int(data["aversive_events"][0]) if "aversive_events" in data else 0
                self.total_plastic_steps = int(data["total_plastic_steps"][0]) if "total_plastic_steps" in data else 0
                print(f"[MemorySystem] [*] Loaded {self.associations_count} persisted associative memories "
                      f"({self.memory_path.stat().st_size / 1024:.1f} KB)!")
                return True
        except Exception as e:
            print(f"[MemorySystem] Warning: Could not parse memory file: {e}")
        return False

    def get_memory_stats(self) -> Dict[str, any]:
        """Returns statistics for HUD display."""
        exists = self.memory_path.exists()
        size_kb = (self.memory_path.stat().st_size / 1024.0) if exists else 0.0
        return {
            "saved": exists,
            "associations": self.associations_count,
            "file_size_kb": size_kb,
            "appetitive": self.appetitive_events,
            "aversive": self.aversive_events
        }
