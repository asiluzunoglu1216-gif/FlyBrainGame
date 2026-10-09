"""30-Second Baseline Diagnostic Test.

Runs FlyBrainApp in F1 Connectome mode for 30 seconds, logging all required biological
channels and computing diagnostic statistics to identify why the fly spins and doesn't
move forward enough.
"""
from __future__ import annotations

import sys
import os
import time
import math
import numpy as np
import pandas as pd
from panda3d.core import loadPrcFileData, Vec3, ClockObject

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless mode
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")

from game.main import FlyBrainApp


def run_diagnostic(duration_sec: float = 30.0):
    print("=" * 70)
    print(f"RUNNING {duration_sec:.0f}-SECOND CONNECTOME (F1) DIAGNOSTIC BENCHMARK")
    print("=" * 70)

    app = FlyBrainApp(headless=True)
    app.fly.set_mode("CONNECTOME")

    # Warmup
    print("[Diagnostic] Warming up connectome worker...")
    t_w = time.time()
    while time.time() - t_w < 10.0:
        telem = app.brain_worker.get_telemetry()
        if telem.brain_step > 5:
            break
        time.sleep(0.1)

    print(f"[Diagnostic] Worker ready at step {telem.brain_step}! Starting 30s run...")

    sim_dt = 1.0 / 50.0  # 50 Hz physics & connectome pacing
    clock = ClockObject.getGlobalClock()

    total_sim_time = 0.0
    total_yaw_delta = 0.0
    prev_yaw = float(app.fly.yaw)
    start_pos = Vec3(app.fly.pos)

    yaw_rates = []
    speeds = []
    spinning_frames = 0
    total_frames = 0

    # Remove old log if present
    if os.path.exists("logs/neural_run.csv"):
        try:
            os.remove("logs/neural_run.csv")
        except Exception:
            pass

    t_start_wall = time.perf_counter()
    while total_sim_time < duration_sec:
        t_frame_start = time.perf_counter()
        clock.setDt(sim_dt)
        app.taskMgr.step()
        total_sim_time += sim_dt
        total_frames += 1

        cur_yaw = float(app.fly.yaw)
        d_yaw = abs((cur_yaw - prev_yaw + 180.0) % 360.0 - 180.0)
        total_yaw_delta += d_yaw
        prev_yaw = cur_yaw

        turn_rate = float(app.fly._current_turn_rate)
        yaw_rates.append(abs(turn_rate))
        speeds.append(float(app.fly._current_speed))

        if abs(turn_rate) > 40.0:
            spinning_frames += 1

        # Real-time pacing (50 Hz)
        elapsed_frame = time.perf_counter() - t_frame_start
        sleep_dur = sim_dt - elapsed_frame
        if sleep_dur > 0.001:
            time.sleep(sleep_dur)

    app.brain_worker.stop()
    app.destroy()

    end_pos = Vec3(app.fly.pos)
    net_displacement = (end_pos - start_pos).length()
    path_distance = app.fly.distance_travelled

    # Read the logged CSV
    df = pd.read_csv("logs/neural_run.csv")
    print("\n" + "=" * 70)
    print("30-SECOND F1 CONNECTOME DIAGNOSTIC REPORT")
    print("=" * 70)

    print(f"Total Brain Steps Logged:       {len(df)}")
    print(f"Simulation Duration:            {total_sim_time:.2f} s ({total_frames} frames)")
    print(f"Total Distance Travelled (path): {path_distance:.2f} units")
    print(f"Net Displacement (start->end):   {net_displacement:.2f} units")
    print(f"Total Yaw Rotation:             {total_yaw_delta:.1f} degrees ({total_yaw_delta / 360.0:.2f} full rotations)")
    spin_ratio = (spinning_frames / total_frames) * 100.0 if total_frames > 0 else 0.0
    print(f"Spin-in-Place Ratio (|w|>40°/s): {spin_ratio:.1f}%")

    print("-" * 70)
    print("DESCENDING MOTOR NEURON FIRING RATES (Hz):")
    for ch in ["dng100_l_hz", "dng100_r_hz", "dna02_l_hz", "dna02_r_hz", "dnp01_l_hz", "dnp01_r_hz", "mdn_l_hz", "mdn_r_hz"]:
        vals = pd.to_numeric(df[ch], errors="coerce").fillna(0.0)
        print(f"  {ch:15s} -> Mean: {vals.mean():5.2f} Hz | Min: {vals.min():5.2f} Hz | Max: {vals.max():5.2f} Hz")

    dng_l = pd.to_numeric(df["dng100_l_hz"], errors="coerce").fillna(0.0)
    dng_r = pd.to_numeric(df["dng100_r_hz"], errors="coerce").fillna(0.0)
    dna_l = pd.to_numeric(df["dna02_l_hz"], errors="coerce").fillna(0.0)
    dna_r = pd.to_numeric(df["dna02_r_hz"], errors="coerce").fillna(0.0)
    dng_avg = (dng_l + dng_r) / 2.0
    dna_avg = (dna_l + dna_r) / 2.0
    print(f"\n  DNg100 Combined -> Mean: {dng_avg.mean():5.2f} Hz | Min: {dng_avg.min():5.2f} Hz | Max: {dng_avg.max():5.2f} Hz")
    print(f"  DNa02 Combined  -> Mean: {dna_avg.mean():5.2f} Hz | Min: {dna_avg.min():5.2f} Hz | Max: {dna_avg.max():5.2f} Hz")

    print("-" * 70)
    print("DECODED FLIGHT PARAMETERS:")
    fwd_speeds = pd.to_numeric(df["forward_speed"], errors="coerce").fillna(0.0)
    turn_rates = pd.to_numeric(df["turn_rate"], errors="coerce").fillna(0.0)
    print(f"  Forward Speed:   Mean: {fwd_speeds.mean():5.2f} | Min: {fwd_speeds.min():5.2f} | Max: {fwd_speeds.max():5.2f}")
    print(f"  Turn Rate |w|:   Mean: {turn_rates.abs().mean():5.2f} deg/s | Min: {turn_rates.abs().min():5.2f} | Max: {turn_rates.abs().max():5.2f}")

    # ZERO SPEED CHECK WHEN DNg100 = 0
    zero_dng_mask = (dng_avg == 0.0)
    zero_dng_count = zero_dng_mask.sum()
    if zero_dng_count > 0:
        fwd_at_zero = fwd_speeds[zero_dng_mask]
        print(f"  Speed when DNg100=0: Max: {fwd_at_zero.max():5.2f} | Mean: {fwd_at_zero.mean():5.2f} (Strictly 0.0 required!) [{zero_dng_count} steps]")
    else:
        print("  DNg100 was active throughout flight (> 0 Hz).")

    fallback_pct = (df["fallback_active"].astype(str).str.lower() == "true").mean() * 100.0
    print(f"  Fallback Safeguard Active: {fallback_pct:5.2f}%")

    print("-" * 70)
    print("SENSORY STIMULATION CHANNELS:")
    for ch in ["stimulus_l", "stimulus_r", "target_stim_l", "target_stim_r", "fwd_stimulus", "optic_flow", "frog_looming"]:
        if ch in df.columns:
            vals = pd.to_numeric(df[ch], errors="coerce").fillna(0.0)
            active_pct = (vals > 0.01).mean() * 100.0
            print(f"  {ch:15s} -> Mean: {vals.mean():5.3f} | Max: {vals.max():5.3f} | Active Time: {active_pct:5.1f}%")

    if "fwd_source" in df.columns:
        print("\nFORWARD-CIRCUIT STIMULUS SOURCES (PVLP137/PLP300m/CB4105):")
        # Extract base source type before details in parentheses
        base_src = df["fwd_source"].astype(str).apply(lambda s: s.split("(")[0])
        for src, count in base_src.value_counts().items():
            print(f"  Source {src:15s}: {count:4d} steps ({count / len(df) * 100.0:.1f}%)")

    print("-" * 70)
    print("DECODED ACTION DISTRIBUTION:")
    action_counts = df["decoded_action"].value_counts()
    for action, count in action_counts.items():
        print(f"  {action:25s}: {count:4d} steps ({count / len(df) * 100.1:.1f}%)")
    print("=" * 70)


if __name__ == "__main__":
    run_diagnostic(30.0)
