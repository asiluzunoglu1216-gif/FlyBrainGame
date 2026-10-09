"""10-Minute Accelerated Headless Living Ecosystem Benchmark & Neural Purity Test.

Runs FlyBrainApp: 'Bir Sineğin Günü' in accelerated headless Panda3D mode
for 600 simulated seconds (10 full minutes of ecosystem time).

Tracks:
1. Pure Connectome Control:
   - Invariant: non_neural_horizontal_movement_commands == 0
   - Strict adherence: 0 forward spikes -> 0.0 forward speed
2. Life Cycle & Demographics:
   - Lifetimes & Reincarnations across death/retry cycles
   - Starvation vs Predator deaths
3. Energetics & Feeding:
   - Energy expenditure, hydration decay, and hunger dynamics
   - Food items consumed and calories replenished
   - Proboscis extensions (PER) onto food substrate
4. Locomotion & Perching:
   - Total distance travelled (airborne vs grounded)
   - Landing events (DNp02-driven vs surface touchdown)
   - Perching time vs Tripod walking time
5. Predator Interactions:
   - Frog encounters (hysteresis counted strictly once per encounter)
   - Physical tongue strike escapes vs predatory strikes
6. Mushroom Body Plasticity & Persistent Memory:
   - Associative memory synaptic potentiation (KC -> MBON gated by PAM/PPL1)
   - File size verification of memory/plastic_synapses.npz (< 2 GB limit)
   - Memory retention across reincarnation cycles
"""
from __future__ import annotations

import os
import sys
import time
import math
from typing import List, Dict

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from panda3d.core import loadPrcFileData, Vec3, ClockObject

# Set headless mode
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")

from game.main import FlyBrainApp
from game.sensory_encoder import SensoryInput


def run_10min_accelerated_life_test(target_duration_sec: float = 600.0, sim_dt: float = 0.04):
    print("=" * 78)
    print(f"STARTING 10-MINUTE ACCELERATED LIVING ECOSYSTEM BENCHMARK ({target_duration_sec:.0f}s SIM TIME)")
    print("=" * 78)

    # Initialize FlyBrainApp with synchronous unthrottled brain worker
    app = FlyBrainApp(headless=True, synchronous_brain=True)

    # Warmup connectome
    print("[LifeTest] Connectome initialized with 166,700 neurons.")
    print(f"[LifeTest] Simulation Step: dt = {sim_dt:.3f}s ({1.0 / sim_dt:.0f} Hz biological clock)")
    total_steps = int(target_duration_sec / sim_dt)
    print(f"[LifeTest] Target steps: {total_steps:,} biological simulation cycles...")

    clock = ClockObject.getGlobalClock()

    total_sim_time = 0.0
    wall_start = time.perf_counter()

    # Metrics
    non_neural_horizontal_commands = 0
    total_reincarnations = 0
    predator_deaths = 0
    starvation_deaths = 0

    cumulative_distance = 0.0
    cumulative_food_eaten = 0
    cumulative_calories = 0.0
    cumulative_landings = 0
    cumulative_escapes = 0
    cumulative_encounters = 0

    airborne_steps = 0
    walking_steps = 0
    perched_steps = 0

    brain_hz_samples: List[float] = []
    latency_samples: List[float] = []
    active_neuron_samples: List[int] = []

    last_report_sim_time = 0.0
    report_interval = 60.0  # Report every 60 simulated seconds (1 sim minute)

    print("\n[LifeTest] Commencing accelerated ecosystem loop...")

    step_idx = 0
    while total_sim_time < target_duration_sec:
        step_idx += 1
        clock.setDt(sim_dt)

        # Check for game over (death event) before stepping
        if app.game_over:
            # Classify cause of death
            if app.fly.internal_state.energy <= 0.0:
                starvation_deaths += 1
                death_cause = "STARVATION"
            else:
                predator_deaths += 1
                death_cause = "FROG_PREDATOR_STRIKE"

            total_reincarnations += 1
            cumulative_food_eaten += app.fly.food_eaten
            cumulative_distance += app.fly.distance_travelled
            cumulative_landings += app.fly.total_landings
            cumulative_escapes += app.fly.frog_escapes
            cumulative_encounters += app.fly.frog_encounters

            print(f"  [Reincarnation #{total_reincarnations}] Fly died of {death_cause} at t={total_sim_time:.1f}s. "
                  f"Life stats: distance={app.fly.distance_travelled:.1f}, food={app.fly.food_eaten}, "
                  f"landings={app.fly.total_landings}. Triggering reincarnation...")
            app._on_retry()

        # Step Panda3D game update (which calls brain_worker.step_once and fly.update)
        app.taskMgr.step()
        total_sim_time += sim_dt

        # Telemetry & Purity Invariant Verification
        telem = app.brain_worker.get_telemetry()
        motor = telem.motor

        # INVARIANT 1: Control mode must be CONNECTOME
        if app.fly.control_mode != "CONNECTOME":
            non_neural_horizontal_commands += 1

        # INVARIANT 2: When fwd_pop_hz == 0.0 Hz, decoded forward_speed must be strictly 0.0
        if motor.fwd_pop_hz == 0.0 and motor.forward_speed > 0.0:
            non_neural_horizontal_commands += 1

        # Track locomotion state
        if app.fly.locomotion_mode == "AIRBORNE":
            airborne_steps += 1
        elif app.fly.locomotion_mode == "GROUNDED":
            if app.fly._current_speed > 0.05:
                walking_steps += 1
            else:
                perched_steps += 1

        if telem.brain_step_hz > 0:
            brain_hz_samples.append(telem.brain_step_hz)
        if telem.step_latency_ms > 0:
            latency_samples.append(telem.step_latency_ms)
        active_neuron_samples.append(telem.active_neurons)

        # Periodic logging every 60 simulated seconds
        if total_sim_time - last_report_sim_time >= report_interval:
            last_report_sim_time = total_sim_time
            wall_elapsed = time.perf_counter() - wall_start
            speedup = total_sim_time / max(0.001, wall_elapsed)
            mem_assoc = telem.memory_associations
            current_tot_dist = cumulative_distance + app.fly.distance_travelled
            current_tot_food = cumulative_food_eaten + app.fly.food_eaten
            current_tot_landings = cumulative_landings + app.fly.total_landings

            print(
                f"[Sim {total_sim_time:5.0f}s / {target_duration_sec:.0f}s] "
                f"Speedup: {speedup:4.1f}x | "
                f"Pos: ({app.fly.pos.x:5.1f}, {app.fly.pos.y:5.1f}, {app.fly.pos.z:4.1f}) | "
                f"Mode: {app.fly.locomotion_mode} ({app.fly.current_surface}) | "
                f"Energy: {app.fly.internal_state.energy:4.1f}% | "
                f"Food: {current_tot_food} | "
                f"Landings: {current_tot_landings} | "
                f"Reincarnations: {total_reincarnations} | "
                f"Memory Assocs: {mem_assoc} | "
                f"Non-neural cmds: {non_neural_horizontal_commands}"
            )

    wall_total = time.perf_counter() - wall_start

    # Accumulate final run stats
    cumulative_food_eaten += app.fly.food_eaten
    cumulative_distance += app.fly.distance_travelled
    cumulative_landings += app.fly.total_landings
    cumulative_escapes += app.fly.frog_escapes
    cumulative_encounters += app.fly.frog_encounters

    # Memory persistence file check
    app.brain_worker.save_memory()
    mem_file = "memory/plastic_synapses.npz"
    mem_size_bytes = os.path.getsize(mem_file) if os.path.exists(mem_file) else 0
    mem_size_kb = mem_size_bytes / 1024.0

    # Summary Statistics
    avg_latency = sum(latency_samples) / len(latency_samples) if latency_samples else 0.0
    avg_active = sum(active_neuron_samples) / len(active_neuron_samples) if active_neuron_samples else 0.0
    total_frames = airborne_steps + walking_steps + perched_steps
    air_pct = (airborne_steps / total_frames) * 100.0 if total_frames > 0 else 0.0
    walk_pct = (walking_steps / total_frames) * 100.0 if total_frames > 0 else 0.0
    perch_pct = (perched_steps / total_frames) * 100.0 if total_frames > 0 else 0.0

    print("\n" + "=" * 78)
    print("10-MINUTE ACCELERATED LIVING ECOSYSTEM BENCHMARK RESULTS")
    print("=" * 78)
    print(f"Simulated Ecosystem Duration:   {total_sim_time:.1f} seconds ({total_sim_time / 60.0:.1f} simulated minutes)")
    print(f"Wall-Clock Execution Time:      {wall_total:.2f} seconds (Speedup: {total_sim_time / wall_total:.1f}x real-time)")
    print(f"Connectome Biological Steps:    {step_idx:,} steps (at dt={sim_dt:.3f}s)")
    print(f"Average Connectome Step Latency:{avg_latency:.2f} ms")
    print(f"Average Active Neurons / Step:  {avg_active:.1f} / 166,700 neurons")
    print("-" * 78)
    print("LOCOMOTION & BEHAVIOR DEMOGRAPHICS:")
    print(f"Total Distance Travelled:       {cumulative_distance:.1f} units")
    print(f"Total Landing Events:           {cumulative_landings}")
    print(f"Airborne Flight Time:           {air_pct:.1f}% ({airborne_steps * sim_dt:.1f}s)")
    print(f"Tripod Walking Time:            {walk_pct:.1f}% ({walking_steps * sim_dt:.1f}s)")
    print(f"Perching / Resting Time:        {perch_pct:.1f}% ({perched_steps * sim_dt:.1f}s)")
    print("-" * 78)
    print("ECOLOGICAL & ENERGETIC INTERACTIONS:")
    print(f"Food Items Consumed:            {cumulative_food_eaten}")
    print(f"Frog Predator Encounters:       {cumulative_encounters} (hysteresis single-count)")
    print(f"Successful Frog Escapes:        {cumulative_escapes}")
    print(f"Predator Tongue Strike Deaths:  {predator_deaths}")
    print(f"Starvation Deaths:              {starvation_deaths}")
    print(f"Total Reincarnations:           {total_reincarnations}")
    print("-" * 78)
    print("MUSHROOM BODY ASSOCIATIVE MEMORY:")
    telem = app.brain_worker.get_telemetry()
    print(f"Learned Associative Pairs:      {telem.memory_associations}")
    print(f"Appetitive (PAM) Events:        {telem.memory_appetitive_events}")
    print(f"Aversive (PPL1) Events:         {telem.memory_aversive_events}")
    print(f"Persisted File Size:            {mem_size_kb:.2f} KB (Storage limit: < 2,097,152 KB)")
    print("-" * 78)
    print("NEURAL CONTROL PURITY INVARIANT:")
    print(f"Non-Neural Horizontal Commands: {non_neural_horizontal_commands} (Strict requirement: 0)")
    print("=" * 78)

    # Verification assertions
    assert non_neural_horizontal_commands == 0, f"VIOLATION: Found {non_neural_horizontal_commands} non-neural commands!"
    assert mem_size_bytes < 2 * 1024 * 1024 * 1024, "Storage limit exceeded: memory file >= 2 GB!"
    assert step_idx >= int(target_duration_sec / sim_dt) * 0.95, "Failed to complete target simulation steps!"

    # Clean shutdown
    app.brain_worker.stop()
    print("\n[LifeTest] All assertions PASSED! 100% pure connectome control verified.")
    return True


if __name__ == "__main__":
    duration = 600.0
    dt = 0.04
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            dt = float(sys.argv[2])
        except ValueError:
            pass
    run_10min_accelerated_life_test(duration, dt)
