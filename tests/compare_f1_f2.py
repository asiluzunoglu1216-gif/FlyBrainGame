"""Comparative A/B Benchmark: F1 (Connectome) vs F2 (Scripted Bot).

Runs both control architectures from the exact same initial state for 20 seconds each
and measures:
- Total trajectory distance
- Total absolute turn angle (degrees turned)
- Number of fallback safeguard activations
- Minimum distance to obstacle / near misses
"""
import sys
sys.path.insert(0, ".")
import time
import math
from game.brain_worker import BrainWorker
from game.environment import Environment
from game.fly_controller import FlyController
from panda3d.core import loadPrcFileData, Vec3
from direct.showbase.ShowBase import ShowBase


def benchmark_mode(mode_name: str, duration: float = 20.0):
    loadPrcFileData("", "window-type none")
    loadPrcFileData("", "audio-library-name null")
    base = ShowBase()

    env = Environment(base.render)
    worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=False)
    worker.start()

    fly = FlyController(base.render, env, worker)
    fly.set_mode(mode_name)
    fly.reset_position()

    total_dist = 0.0
    total_turn_deg = 0.0
    fallback_events = 0
    min_obstacle_dist = 1e9
    close_proximity_count = 0  # frames where obstacle < 4.0 units

    # Wait for JIT warmup
    t_wait = time.time()
    while time.time() - t_wait < 8.0:
        if worker.get_telemetry().brain_step > 3:
            break
        time.sleep(0.1)

    prev_pos = Vec3(fly.pos)
    prev_yaw = fly.yaw

    dt = 0.02  # 50 Hz steps
    steps = 0
    t_start = time.time()
    while time.time() - t_start < duration:
        t_step = time.time()
        env.update(dt)
        fly.update(dt)
        steps += 1

        # 1. Distance
        disp = (fly.pos - prev_pos).length()
        total_dist += disp
        prev_pos = Vec3(fly.pos)

        # 2. Turn angle
        yaw_diff = abs((fly.yaw - prev_yaw + 180.0) % 360.0 - 180.0)
        total_turn_deg += yaw_diff
        prev_yaw = fly.yaw

        # 3. Fallback
        if fly.fallback_active:
            fallback_events += 1

        # 4. Raycast proximity check to nearest obstacle
        fwd = fly._get_forward_vec(fly.yaw)
        d = env.raycast(fly.pos, fwd, max_dist=40.0)
        if d < min_obstacle_dist:
            min_obstacle_dist = d
        if d < 4.0:
            close_proximity_count += 1

        elapsed = time.time() - t_step
        if dt > elapsed:
            time.sleep(dt - elapsed)

    worker.stop()
    base.destroy()

    return {
        "mode": mode_name,
        "duration_s": duration,
        "total_distance": total_dist,
        "total_turn_degrees": total_turn_deg,
        "fallback_steps": fallback_events,
        "fallback_pct": (fallback_events / steps) * 100.0,
        "min_dist_to_obstacle": min_obstacle_dist,
        "close_proximity_frames": close_proximity_count
    }


def main():
    print("=== Running F1: CONNECTOME Benchmark (20s) ===")
    res_f1 = benchmark_mode("CONNECTOME", duration=20.0)

    print("\n=== Running F2: SCRIPTED BOT Benchmark (20s) ===")
    res_f2 = benchmark_mode("SCRIPTED_BOT", duration=20.0)

    print("\n" + "=" * 65)
    print("           A/B BENCHMARK COMPARISON RESULTS (20 SECONDS)")
    print("=" * 65)
    print(f"{'Metric':<32} | {'F1: CONNECTOME':<14} | {'F2: SCRIPTED':<14}")
    print("-" * 65)
    print(f"{'Total Distance Traveled (units)':<32} | {res_f1['total_distance']:<14.2f} | {res_f2['total_distance']:<14.2f}")
    print(f"{'Total Yaw Turned (degrees)':<32} | {res_f1['total_turn_degrees']:<14.1f} | {res_f2['total_turn_degrees']:<14.1f}")
    print(f"{'Fallback Safeguard Steps':<32} | {res_f1['fallback_steps']:<14d} | {res_f2['fallback_steps']:<14d}")
    print(f"{'Fallback Safeguard Pct (%)':<32} | {res_f1['fallback_pct']:<14.1f} | {res_f2['fallback_pct']:<14.1f}")
    print(f"{'Minimum Obstacle Distance (u)':<32} | {res_f1['min_dist_to_obstacle']:<14.2f} | {res_f2['min_dist_to_obstacle']:<14.2f}")
    print(f"{'Near-Hazard Proximity Frames (<4u)':<32} | {res_f1['close_proximity_frames']:<14d} | {res_f2['close_proximity_frames']:<14d}")
    print("=" * 65)


if __name__ == "__main__":
    main()
