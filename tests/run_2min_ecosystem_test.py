"""2-Minute Headless Living Ecosystem Benchmark.

Runs FlyBrainApp: 'Bir Sineğin Günü' in headless Panda3D mode for 120 simulated seconds.
Records:
- Render FPS
- Brain Step Hz and step latency (ms)
- Distance travelled and flight trajectory
- Landing & perching events
- Food encounters and feeding completions
- Frog predator encounters and escapes
- Fallback safeguard activation percentage
"""
from __future__ import annotations

import time
import math
from panda3d.core import loadPrcFileData, Vec3, ClockObject

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set headless mode
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")

from game.main import FlyBrainApp


def run_benchmark(target_duration_sec: float = 120.0):
    print("=" * 70)
    print(f"STARTING {target_duration_sec:.0f}-SECOND LIVING ECOSYSTEM BENCHMARK")
    print("=" * 70)

    app = FlyBrainApp(headless=True)

    # Wait for brain worker to initialize and warmup
    print("[Benchmark] Waiting for connectome worker warmup...")
    t_wait = time.time()
    while time.time() - t_wait < 10.0:
        telem = app.brain_worker.get_telemetry()
        if telem.brain_step > 5:
            break
        time.sleep(0.2)

    print(f"[Benchmark] Worker ready at connectome step {telem.brain_step}! Commencing simulation loop...")

    sim_dt = 1.0 / 60.0  # 60 FPS simulated physics step
    clock = ClockObject.getGlobalClock()

    total_sim_time = 0.0
    wall_start = time.perf_counter()

    sample_interval = 1.0
    last_sample_time = 0.0

    brain_hz_samples = []
    latency_samples = []
    altitude_samples = []
    fallback_frames = 0
    total_frames = 0
    perch_frames = 0

    while total_sim_time < target_duration_sec:
        # Step clock & app
        clock.setDt(sim_dt)
        app.taskMgr.step()

        total_sim_time += sim_dt
        total_frames += 1

        telem = app.brain_worker.get_telemetry()
        pos = app.fly.pos

        if app.fly.is_landed:
            perch_frames += 1

        if app.fly.fallback_active:
            fallback_frames += 1

        altitude_samples.append(pos.z)
        if telem.brain_step_hz > 0:
            brain_hz_samples.append(telem.brain_step_hz)
        if telem.step_latency_ms > 0:
            latency_samples.append(telem.step_latency_ms)

        # Periodic logging every 15 simulated seconds
        if total_sim_time - last_sample_time >= 15.0:
            last_sample_time = total_sim_time
            print(
                f"[Sim {total_sim_time:5.1f}s / {target_duration_sec:.0f}s] "
                f"Pos: ({pos.x:5.1f}, {pos.y:5.1f}, {pos.z:4.1f}) | "
                f"Landed: {app.fly.is_landed} ({app.fly.current_surface}) | "
                f"Food Eaten: {app.fly.food_eaten} | "
                f"Landings: {app.fly.total_landings} | "
                f"Frog Encounters: {app.fly.frog_encounters} | "
                f"Escapes: {app.fly.frog_escapes} | "
                f"Brain Hz: {telem.brain_step_hz:.1f} | "
                f"Decision: {telem.motor.decision}"
            )

    wall_duration = time.perf_counter() - wall_start
    real_fps = total_frames / wall_duration if wall_duration > 0 else 0.0

    app.brain_worker.stop()
    app.destroy()

    avg_brain_hz = sum(brain_hz_samples) / len(brain_hz_samples) if brain_hz_samples else 0.0
    avg_latency = sum(latency_samples) / len(latency_samples) if latency_samples else 0.0
    avg_altitude = sum(altitude_samples) / len(altitude_samples) if altitude_samples else 0.0
    max_altitude = max(altitude_samples) if altitude_samples else 0.0
    min_altitude = min(altitude_samples) if altitude_samples else 0.0
    fallback_pct = (fallback_frames / total_frames) * 100.0 if total_frames > 0 else 0.0
    perch_pct = (perch_frames / total_frames) * 100.0 if total_frames > 0 else 0.0

    print("\n" + "=" * 70)
    print("2-MINUTE LIVING ECOSYSTEM SIMULATION RESULTS")
    print("=" * 70)
    print(f"Simulated Duration:       {total_sim_time:.1f} s ({total_frames} frames @ 60 FPS)")
    print(f"Wall-Clock Time:          {wall_duration:.2f} s (Simulation speedup: {total_sim_time / wall_duration:.2f}x)")
    print(f"Average Render Rate:      {real_fps:.1f} FPS")
    print(f"Connectome Brain Step Hz: {avg_brain_hz:.2f} Hz (Biological step = 20ms)")
    print(f"Step Latency:             {avg_latency:.2f} ms")
    print(f"Distance Travelled:       {app.fly.distance_travelled:.1f} units")
    print(f"Total Landings:           {app.fly.total_landings}")
    print(f"Time Spent Perched:       {perch_pct:.1f}%")
    print(f"Food Items Consumed:      {app.fly.food_eaten}")
    print(f"Frog Encounters:          {app.fly.frog_encounters}")
    print(f"Successful Escapes:       {app.fly.frog_escapes}")
    print(f"Altitude (Min / Avg / Max): {min_altitude:.2f} / {avg_altitude:.2f} / {max_altitude:.2f} units")
    print(f"Fallback Safeguard Rate:  {fallback_pct:.2f}% (Pure connectome control: {100.0 - fallback_pct:.2f}%)")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark(120.0)
