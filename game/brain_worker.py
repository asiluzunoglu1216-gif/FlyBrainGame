"""Asynchronous Decoupled Connectome Worker.

Runs FlyBrain simulation in a separate thread (with modular architecture
compatible with multiprocessing) so Panda3D's 60 FPS render loop NEVER blocks.

Calculates:
- Brain Step Hz: Real connectome simulation steps per second
- Step Latency (ms): Time taken to compute one connectome step
- Real neuron spike counts and firing rates (Hz) for descending neurons
- Feeding (CEM, MN10), Landing (DNp02), Punch (DNg11), and Kick (pIP10) motor populations
- Persistent Mushroom Body associative memory (KC -> MBON gated by PAM / PPL1)
"""
from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Dict
import numpy as np

from flybrain import FlyBrain
from .sensory_encoder import SensoryInput, FeatureEncoder, EyeEncoder
from .motor_decoder import MotorDecoder, MotorState
from .memory_system import MushroomBodyMemorySystem
from .telemetry import TelemetryLogger


@dataclass
class BrainTelemetry:
    brain_step: int = 0
    brain_step_hz: float = 0.0       # Steps/sec of connectome simulation
    step_latency_ms: float = 0.0     # Step computation time in ms
    active_neurons: int = 0          # Number of neurons that fired in latest step
    sensory: SensoryInput = field(default_factory=SensoryInput)
    motor: MotorState = field(default_factory=MotorState)
    sensory_mode: str = "FEATURE_MODE"
    enabled: bool = True             # Connectome ON/OFF
    appetitive_mbon_drive: float = 0.0
    aversive_mbon_drive: float = 0.0
    memory_associations: int = 0
    memory_appetitive_events: int = 0
    memory_aversive_events: int = 0


class BrainWorker:
    """Thread-safe worker hosting the FlyBrain connectome and running its LIF dynamics."""

    def __init__(self, sensory_mode: str = "FEATURE_MODE", log_telemetry: bool = True, threaded: bool = True, paced: bool = True):
        self.sensory_mode = sensory_mode
        self.threaded = threaded
        self.paced = paced
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Lock for thread-safe state exchange
        self._lock = threading.Lock()

        # Shared states
        self._sensory_input = SensoryInput()
        self._latest_telemetry = BrainTelemetry(sensory_mode=sensory_mode)
        self._connectome_enabled = True
        self._paused = False
        self._reset_requested: Optional[int] = None

        # Telemetry logger
        self.logger = TelemetryLogger(enabled=log_telemetry)

        # Brain instance, memory system, and encoders
        self.brain: Optional[FlyBrain] = None
        self.memory: Optional[MushroomBodyMemorySystem] = None
        self.feature_encoder: Optional[FeatureEncoder] = None
        self.eye_encoder: Optional[EyeEncoder] = None
        self.decoder = MotorDecoder()

        # Descending neuron indices for readout
        self.readouts: Dict[str, np.ndarray] = {}

        # Spike history and step frequency tracking
        self.spike_history: Dict[str, deque] = {}
        self.step_times: deque = deque(maxlen=20)
        self.step_counter: int = 0
        self._prev_kc_active: np.ndarray = np.array([], dtype=np.int32)

    def start(self):
        """Starts the brain simulation worker thread (or initializes synchronously if threaded=False)."""
        if self._running:
            return
        self._running = True
        if self.threaded:
            self._thread = threading.Thread(target=self._run_loop, name="FlyBrainWorker", daemon=True)
            self._thread.start()
        else:
            self._init_brain()

    def stop(self):
        """Stops the worker thread, saves memory, and flushes telemetry."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.save_memory()
        self.logger.close()

    def update_sensory(self, sensory: SensoryInput):
        """Called by main render loop to submit latest sensory readings (thread-safe)."""
        with self._lock:
            self._sensory_input = sensory

    def get_telemetry(self) -> BrainTelemetry:
        """Called by main render loop / HUD to get latest motor & brain stats (thread-safe)."""
        with self._lock:
            return BrainTelemetry(
                brain_step=self._latest_telemetry.brain_step,
                brain_step_hz=self._latest_telemetry.brain_step_hz,
                step_latency_ms=self._latest_telemetry.step_latency_ms,
                active_neurons=self._latest_telemetry.active_neurons,
                sensory=self._sensory_input,
                motor=self._latest_telemetry.motor,
                sensory_mode=self.sensory_mode,
                enabled=self._connectome_enabled,
                appetitive_mbon_drive=self._latest_telemetry.appetitive_mbon_drive,
                aversive_mbon_drive=self._latest_telemetry.aversive_mbon_drive,
                memory_associations=self._latest_telemetry.memory_associations,
                memory_appetitive_events=self._latest_telemetry.memory_appetitive_events,
                memory_aversive_events=self._latest_telemetry.memory_aversive_events
            )

    def set_connectome_enabled(self, enabled: bool):
        with self._lock:
            self._connectome_enabled = enabled

    def set_paused(self, paused: bool):
        with self._lock:
            self._paused = paused

    def reset_brain(self, seed: Optional[int] = None):
        with self._lock:
            self._reset_requested = seed if seed is not None else 42

    def set_sensory_mode(self, mode: str):
        with self._lock:
            self.sensory_mode = mode

    def save_memory(self):
        """Persists associative memories to disk (strictly under 2 GB limit)."""
        if self.memory is not None:
            self.memory.save()

    def load_memory(self):
        """Loads associative memories from disk."""
        if self.memory is not None:
            self.memory.load()

    def _init_brain(self):
        """Initializes connectome, maps readout neurons, and sets up mushroom body memory."""
        print("[BrainWorker] Initializing 166,700-neuron MaleCNS connectome...")
        self.brain = FlyBrain(seed=42)
        types = set(self.brain.cell_type)

        # Readout neurons and motor population pools
        self.readouts = {
            # Individual neurons (for backward compatibility and test verification)
            "dnp01_l": self.brain.cells(["DNp01"], side="L"),
            "dnp01_r": self.brain.cells(["DNp01"], side="R"),
            "dna02_l": self.brain.cells(["DNa02"], side="L"),
            "dna02_r": self.brain.cells(["DNa02"], side="R"),
            "dng100_l": self.brain.cells(["DNg100"], side="L"),
            "dng100_r": self.brain.cells(["DNg100"], side="R"),
            "mdn_l": self.brain.cells(["MDN"], side="L"),
            "mdn_r": self.brain.cells(["MDN"], side="R"),

            # Population motor pools (MaleCNS descending motor groups)
            "fwd_pop_l": self.brain.cells(["DNg100", "DNp09"], side="L"),
            "fwd_pop_r": self.brain.cells(["DNg100", "DNp09"], side="R"),
            "steer_pop_l": self.brain.cells(["DNa02", "DNa01"], side="L"),
            "steer_pop_r": self.brain.cells(["DNa02", "DNa01"], side="R"),
            "esc_pop_l": self.brain.cells(["DNp01"], side="L"),
            "esc_pop_r": self.brain.cells(["DNp01"], side="R"),
            "bwd_pop_l": self.brain.cells(["MDN"], side="L"),
            "bwd_pop_r": self.brain.cells(["MDN"], side="R"),

            # Feeding & Proboscis Motor Population (CEM, MN10)
            "feeding_pop": self.brain.cells(["CEM", "MN10"]),

            # Landing / Deceleration Population (DNp02)
            "landing_pop": self.brain.cells(["DNp02"]),

            # Defensive Motor Populations (DNg11 punch, pIP10 kick)
            "punch_pop": self.brain.cells(["DNg11"]),
            "kick_pop": self.brain.cells(["pIP10"]),

            # Asynchronous Flight Power (DLMn downstroke + DVMn upstroke motor neurons)
            "flight_power_pop": self.brain.cells(["DLMn a, b", "DLMn c-f", "DVMn 1a-c", "DVMn 2a, b", "DVMn 3a, b", "hDVM MN"]),

            # Direct Wing Steering Motor Neurons (b1, b2, i1, i2, hi1, hi2, hg1-4)
            "wing_steer_l": self.brain.cells(["b1 MN", "b2 MN", "i1 MN", "i2 MN", "hi1 MN", "hi2 MN", "hg1 MN", "hg2 MN", "hg3 MN", "hg4 MN"], side="L"),
            "wing_steer_r": self.brain.cells(["b1 MN", "b2 MN", "i1 MN", "i2 MN", "hi1 MN", "hi2 MN", "hg1 MN", "hg2 MN", "hg3 MN", "hg4 MN"], side="R"),

            # Central Complex Steering Neurons (PFL3)
            "cx_steer_l": self.brain.cells(["PFL3"], side="L"),
            "cx_steer_r": self.brain.cells(["PFL3"], side="R"),

            # Grooming Motor Population (DNg12)
            "groom_pop": self.brain.cells(["DNg12_a", "DNg12_b", "DNg12_c", "DNg12_d", "DNg12_e"]),
        }

        # Initialize Mushroom Body Plasticity & Associative Memory System
        kc_types = [t for t in types if "KC" in str(t)]
        mbon_types = [t for t in types if "MBON" in str(t)]
        pam_types = [t for t in types if "PAM" in str(t)]
        ppl1_types = [t for t in types if "PPL1" in str(t)]

        self.memory = MushroomBodyMemorySystem(
            kc_indices=self.brain.cells(kc_types),
            mbon_indices=self.brain.cells(mbon_types),
            pam_indices=self.brain.cells(pam_types),
            ppl1_indices=self.brain.cells(ppl1_types),
            memory_path="memory/plastic_synapses.npz"
        )

        self.feature_encoder = FeatureEncoder(self.brain)
        self.eye_encoder = EyeEncoder(self.brain)

        # Build fast vectorized masks for descending neuron readouts
        self._readout_keys = list(self.readouts.keys())
        self._readout_masks = []
        for k in self._readout_keys:
            mask = np.zeros(170000, dtype=bool)
            idxs = self.readouts[k]
            if len(idxs) > 0:
                mask[idxs[idxs < 170000]] = True
            self._readout_masks.append(mask)

        self.spike_history = {k: deque(maxlen=10) for k in self.readouts}
        self.step_times.clear()
        self.step_counter = 0

        # JIT warmup
        print("[BrainWorker] Warming up Numba JIT compiler...")
        for _ in range(5):
            self.brain.step()
        print("[BrainWorker] Ready! Commencing autonomous neural loop.")

    def step_once(self, sensory: Optional[SensoryInput] = None) -> BrainTelemetry:
        """Executes a single connectome LIF simulation step and updates motor state."""
        t_start = time.perf_counter()

        with self._lock:
            if sensory is not None:
                self._sensory_input = sensory
            current_sensory = self._sensory_input
            mode = self.sensory_mode
            enabled = self._connectome_enabled
            reset_seed = self._reset_requested
            if reset_seed is not None:
                self._reset_requested = None

        if reset_seed is not None and self.brain is not None:
            self.brain.reset(seed=reset_seed)
            for k in self.readouts:
                if k in self.spike_history:
                    self.spike_history[k].clear()

        target_dt = self.brain.dt if self.brain is not None else 0.020

        # 1. Encode sensory input
        injections = []
        eye_drive = None
        if mode == "FEATURE_MODE" and self.feature_encoder is not None:
            injections = list(self.feature_encoder.encode(current_sensory))
        elif mode == "EYE_MODE" and self.eye_encoder is not None:
            eye_drive = self.eye_encoder.encode(current_sensory)

        # 1b. Inject plastic MBON currents from previously active Kenyon Cells
        if self.memory is not None and len(self._prev_kc_active) > 0:
            mbon_inj = self.memory.compute_mbon_injections(self._prev_kc_active)
            if mbon_inj:
                injections.extend(mbon_inj)

        # 2. Advance connectome by 1 biological step (20 ms)
        if self.brain is not None and enabled:
            fired = self.brain.step(eye_drive=eye_drive, inject=injections)
        else:
            fired = np.array([], dtype=int)
        active_count = len(fired)

        # 3. Update Mushroom Body Associative Memory & Plasticity
        app_drive, av_drive = 0.0, 0.0
        mem_assoc, mem_app, mem_av = 0, 0, 0
        if self.memory is not None:
            self.memory.update_activity_trace(fired, dt=target_dt)
            if current_sensory.pam_reward > 0.01 or current_sensory.ppl1_punish > 0.01:
                self.memory.apply_reinforcement(
                    pam_reward=current_sensory.pam_reward,
                    ppl1_punishment=current_sensory.ppl1_punish
                )
            if len(fired) > 0:
                valid_fired = fired[fired < len(self.memory._kc_slot_lut)]
                kc_active = valid_fired[self.memory._kc_slot_lut[valid_fired] >= 0]
            else:
                kc_active = np.array([], dtype=np.int32)
            self._prev_kc_active = kc_active
            app_drive, av_drive = self.memory.compute_learned_mbon_drive(kc_active)
            mem_assoc = self.memory.associations_count
            mem_app = self.memory.appetitive_events
            mem_av = self.memory.aversive_events

        # 4. Record readout spikes
        rates = {}
        window_duration = max(1, len(self.spike_history.get("dnp01_l", [1]))) * target_dt
        valid_fired = fired[fired < 170000] if len(fired) > 0 else np.array([], dtype=int)
        for i, k in enumerate(self._readout_keys):
            if k not in self.spike_history:
                self.spike_history[k] = deque(maxlen=10)
            spikes = int(np.sum(self._readout_masks[i][valid_fired])) if len(valid_fired) > 0 else 0
            self.spike_history[k].append(spikes)
            n_cells = max(1, len(self.readouts[k]))
            rates[k] = (sum(self.spike_history[k]) / n_cells) / window_duration

        # 5. Decode motor state
        motor = self.decoder.decode(rates)

        # 6. Measure latency & frequency
        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000.0
        self.step_times.append(t_start)

        step_hz = 0.0
        if len(self.step_times) >= 2:
            time_span = self.step_times[-1] - self.step_times[0]
            if time_span > 0:
                step_hz = (len(self.step_times) - 1) / time_span

        self.step_counter += 1

        # 7. Publish telemetry (thread-safe)
        telem = BrainTelemetry(
            brain_step=self.step_counter,
            brain_step_hz=step_hz,
            step_latency_ms=latency_ms,
            active_neurons=active_count,
            sensory=current_sensory,
            motor=motor,
            sensory_mode=mode,
            enabled=enabled,
            appetitive_mbon_drive=app_drive,
            aversive_mbon_drive=av_drive,
            memory_associations=mem_assoc,
            memory_appetitive_events=mem_app,
            memory_aversive_events=mem_av
        )
        with self._lock:
            self._latest_telemetry = telem

        # 8. Log to CSV
        self.logger.log(
            brain_step=self.step_counter,
            dng100_l=motor.dng100_l_hz,
            dng100_r=motor.dng100_r_hz,
            dna02_l=motor.dna02_l_hz,
            dna02_r=motor.dna02_r_hz,
            dnp01_l=motor.dnp01_l_hz,
            dnp01_r=motor.dnp01_r_hz,
            mdn_l=motor.mdn_l_hz,
            mdn_r=motor.mdn_r_hz,
            fwd_pop_hz=motor.fwd_pop_hz,
            steer_pop_hz=motor.steer_pop_hz,
            escape_pop_hz=motor.escape_pop_hz,
            back_pop_hz=motor.back_pop_hz,
            forward_speed=motor.forward_speed,
            turn_rate=motor.turn_rate,
            stimulus_l=current_sensory.stimulus_l,
            stimulus_r=current_sensory.stimulus_r,
            target_stim_l=current_sensory.target_stim_l,
            target_stim_r=current_sensory.target_stim_r,
            frog_looming=current_sensory.frog_looming,
            locomotion_mode=motor.locomotion_mode,
            surface_contact=current_sensory.surface_contact,
            decoded_action=motor.decision,
            fallback_active=current_sensory.fallback_active,
            fwd_stimulus=current_sensory.fwd_stimulus,
            fwd_source=current_sensory.fwd_source,
            optic_flow=current_sensory.optic_flow
        )

        return telem

    def _run_loop(self):
        self._init_brain()
        target_dt = self.brain.dt if self.brain is not None else 0.020

        while self._running:
            t_start = time.perf_counter()

            with self._lock:
                paused = self._paused
                enabled = self._connectome_enabled

            if paused:
                time.sleep(0.04)
                continue

            if not enabled:
                time.sleep(0.02)
                continue

            self.step_once()

            if self.paced:
                elapsed = time.perf_counter() - t_start
                sleep_time = target_dt - elapsed
                if sleep_time > 0.001:
                    time.sleep(sleep_time)
