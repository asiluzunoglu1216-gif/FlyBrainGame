"""Test flight with Connectome disabled (OFF)."""
import sys
sys.path.insert(0, ".")
import time
from game.brain_worker import BrainWorker
from game.environment import Environment
from game.fly_controller import FlyController
from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase

def run_disabled_test():
    loadPrcFileData("", "window-type none")
    loadPrcFileData("", "audio-library-name null")
    base = ShowBase()

    env = Environment(base.render)
    worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=False)
    worker.start()

    fly = FlyController(base.render, env, worker)
    # Turn Connectome completely OFF
    fly.set_mode("CONNECTOME")
    worker.set_connectome_enabled(False)

    print("[Disabled Test] Running 5 seconds with connectome disabled...")
    t_start = time.time()
    dt = 0.02
    while time.time() - t_start < 5.0:
        env.update(dt)
        fly.update(dt)
        time.sleep(dt)

    telem = worker.get_telemetry()
    worker.stop()

    print(f"Connectome Enabled: {telem.enabled}")
    print(f"Brain Step: {telem.brain_step}")
    print(f"DNp01_L: {telem.motor.dnp01_l_hz:.1f} Hz, DNp01_R: {telem.motor.dnp01_r_hz:.1f} Hz")
    print(f"DNa02_L: {telem.motor.dna02_l_hz:.1f} Hz, DNa02_R: {telem.motor.dna02_r_hz:.1f} Hz")
    print(f"Turn Rate: {telem.motor.turn_rate:.1f} deg/s")
    print(f"Escape Impulse: {telem.motor.escape_impulse:.1f}")
    print(f"Decision: {telem.motor.decision}")

if __name__ == "__main__":
    run_disabled_test()
