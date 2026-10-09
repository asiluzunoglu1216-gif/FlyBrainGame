"""Neural Flight Telemetry Logger.

Logs every brain step and motor decision to logs/neural_run.csv for analysis
and neural causality verification.
"""
from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Optional


class TelemetryLogger:
    def __init__(self, log_path: Path | str = "logs/neural_run.csv", enabled: bool = True):
        self.log_path = Path(log_path)
        self.enabled = enabled
        self._file = None
        self._writer = None

        if self.enabled:
            self.open()

    def open(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.log_path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow([
            "timestamp",
            "brain_step",
            "dng100_l_hz",
            "dng100_r_hz",
            "dna02_l_hz",
            "dna02_r_hz",
            "dnp01_l_hz",
            "dnp01_r_hz",
            "mdn_l_hz",
            "mdn_r_hz",
            "fwd_pop_hz",
            "steer_pop_hz",
            "escape_pop_hz",
            "back_pop_hz",
            "forward_speed",
            "turn_rate",
            "stimulus_l",
            "stimulus_r",
            "target_stim_l",
            "target_stim_r",
            "fwd_stimulus",
            "fwd_source",
            "optic_flow",
            "frog_looming",
            "locomotion_mode",
            "surface_contact",
            "decoded_action",
            "fallback_active"
        ])
        self._file.flush()

    def log(self, brain_step: int,
            dng100_l: float, dng100_r: float,
            dna02_l: float, dna02_r: float,
            dnp01_l: float, dnp01_r: float,
            mdn_l: float, mdn_r: float,
            forward_speed: float, turn_rate: float,
            stimulus_l: float, stimulus_r: float,
            target_stim_l: float, target_stim_r: float,
            frog_looming: float,
            decoded_action: str, fallback_active: bool,
            fwd_stimulus: float = 0.0,
            fwd_source: str = "NONE",
            optic_flow: float = 0.0,
            fwd_pop_hz: float = 0.0,
            steer_pop_hz: float = 0.0,
            escape_pop_hz: float = 0.0,
            back_pop_hz: float = 0.0,
            locomotion_mode: str = "AIRBORNE",
            surface_contact: bool = False):
        if not self.enabled or self._writer is None:
            return

        self._writer.writerow([
            f"{time.time():.3f}",
            brain_step,
            f"{dng100_l:.1f}",
            f"{dng100_r:.1f}",
            f"{dna02_l:.1f}",
            f"{dna02_r:.1f}",
            f"{dnp01_l:.1f}",
            f"{dnp01_r:.1f}",
            f"{mdn_l:.1f}",
            f"{mdn_r:.1f}",
            f"{fwd_pop_hz:.1f}",
            f"{steer_pop_hz:.1f}",
            f"{escape_pop_hz:.1f}",
            f"{back_pop_hz:.1f}",
            f"{forward_speed:.2f}",
            f"{turn_rate:.2f}",
            f"{stimulus_l:.3f}",
            f"{stimulus_r:.3f}",
            f"{target_stim_l:.3f}",
            f"{target_stim_r:.3f}",
            f"{fwd_stimulus:.3f}",
            fwd_source,
            f"{optic_flow:.3f}",
            f"{frog_looming:.3f}",
            locomotion_mode,
            surface_contact,
            decoded_action,
            fallback_active
        ])
        # Periodic flush
        if brain_step % 10 == 0:
            self._file.flush()

    def close(self):
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None
            self._writer = None
