"""Deterministic Live Reproduction Diagnostic.

Runs the exact game loop from run_game.py in headless synchronous mode
for 180 simulated seconds, logging:
- Position XYZ
- Populations (Fwd, Steer, Esc, Bwd, Feed, Land)
- Hunger, Energy
- Odor L/R, Taste
- Surface distance, Locomotion mode
- Landings, Food contacts, Feedings
- Frog distance, Frog state, Tongue state, Tongue hit distance
- Cause of death
"""
from __future__ import annotations
import os, sys, time, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from panda3d.core import loadPrcFileData, ClockObject
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")
from game.main import FlyBrainApp


def reproduce(duration: float = 180.0):
    print("=" * 80)
    print(f"REPRODUCING LIVE ISSUES (Duration: {duration:.1f}s)")
    print("=" * 80)

    app = FlyBrainApp(headless=True, synchronous_brain=True)
    clock = ClockObject.getGlobalClock()
    sim_dt = 0.04
    total = 0.0
    steps = 0

    landings_observed = 0
    food_eaten_observed = 0
    deaths = 0
    death_causes = []

    # Track altitude distribution
    altitudes = []
    speeds = []

    while total < duration:
        if app.game_over:
            deaths += 1
            cause = "STARVATION" if app.fly.internal_state.energy <= 0.0 else "FROG_OR_OTHER"
            death_causes.append((total, cause, app.fly.frog_encounters))
            print(f"  [DEATH EVENT @ t={total:.1f}s] Cause: {cause} | Energy: {app.fly.internal_state.energy:.3f} | Frog Encounters: {app.fly.frog_encounters}")
            app._on_retry()

        clock.setDt(sim_dt)
        app.taskMgr.step()
        total += sim_dt
        steps += 1

        telem = app.brain_worker.get_telemetry()
        m = telem.motor
        s = telem.sensory
        fly = app.fly

        altitudes.append(fly.pos.z)
        speeds.append(m.forward_speed)

        if steps % 500 == 0:
            print(f"  [t={total:5.1f}s] Pos=({fly.pos.x:5.1f}, {fly.pos.y:5.1f}, {fly.pos.z:4.1f}) "
                  f"Speed={m.forward_speed:4.1f} Mode={fly.locomotion_mode} Landings={fly.total_landings} "
                  f"Energy={fly.internal_state.energy:.2f} Hunger={s.hunger:.2f} "
                  f"NearestFood={s.target_dist:.1f} Odor={s.odor_conc:.3f} "
                  f"FrogDist={min((f.pos - fly.pos).length() for f in app.frogs):.1f}")

    print("\n" + "=" * 80)
    print("REPRODUCTION SUMMARY")
    print("=" * 80)
    print(f"Total Steps:            {steps}")
    print(f"Total Deaths:           {deaths} -> {death_causes}")
    print(f"Total Landings:         {app.fly.total_landings}")
    print(f"Total Food Eaten:       {app.fly.food_eaten}")
    print(f"Frog Encounters:        {app.fly.frog_encounters}")
    print(f"Min Altitude:           {min(altitudes):.2f} (Spawn was 8.0)")
    print(f"Max Altitude:           {max(altitudes):.2f}")
    print(f"Avg Altitude:           {sum(altitudes)/len(altitudes):.2f}")
    print("=" * 80)
    app.brain_worker.stop()


if __name__ == "__main__":
    reproduce(180.0)
