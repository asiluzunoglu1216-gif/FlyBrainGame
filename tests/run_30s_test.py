import sys
sys.path.insert(0, ".")
import time
import numpy as np
import pandas as pd
from game.brain_worker import BrainWorker
from game.environment import Environment
from game.fly_controller import FlyController
from panda3d.core import NodePath, loadPrcFileData
from direct.showbase.ShowBase import ShowBase

def run_test():
    loadPrcFileData("", "window-type none")
    loadPrcFileData("", "audio-library-name null")
    base = ShowBase()

    print("[30s Test] Setting up environment and fly...")
    env = Environment(base.render)
    worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=True)
    worker.start()

    fly = FlyController(base.render, env, worker)
    fly.set_mode("CONNECTOME")

    print("[30s Test] Running 30-second flight simulation...")
    t_start = time.time()
    latencies = []
    step_hz_samples = []
    altitudes = []

    dt = 0.02  # 50 FPS physics
    while time.time() - t_start < 30.0:
        t_loop_start = time.time()
        env.update(dt)
        fly.update(dt)
        altitudes.append(float(fly.pos.z))

        telem = worker.get_telemetry()
        if telem.step_latency_ms > 0:
            latencies.append(telem.step_latency_ms)
        if telem.brain_step_hz > 0:
            step_hz_samples.append(telem.brain_step_hz)

        # Pace loop
        time.sleep(max(0.001, dt - (time.time() - t_loop_start)))

    worker.stop()
    print("[30s Test] Simulation complete! Analyzing telemetry...")

    df = pd.read_csv("logs/neural_run.csv")
    head_on_count = df['decoded_action'].str.contains('HEADON').sum()
    lateral_count = df['decoded_action'].str.contains('STEER').sum()

    print("=" * 60)
    print(f"Total recorded brain steps: {len(df)}")
    print(f"Brain Step Hz - Mean: {np.mean(step_hz_samples):.2f}, Min: {np.min(step_hz_samples):.2f}, Max: {np.max(step_hz_samples):.2f}")
    print(f"Step Latency (ms) - Mean: {np.mean(latencies):.2f}, Min: {np.min(latencies):.2f}, Max: {np.max(latencies):.2f}")
    print(f"Mean Altitude (Z): {np.mean(altitudes):.2f} units")
    print(f"Max Altitude (Z): {np.max(altitudes):.2f} units")
    print(f"Head-on Escape Count: {head_on_count}")
    print(f"Lateral Escape Count: {lateral_count}")
    print(f"Fallback Active Steps: {df['fallback_active'].sum()} / {len(df)} ({df['fallback_active'].mean()*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
