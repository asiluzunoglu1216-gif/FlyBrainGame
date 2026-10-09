"""60-Second Diagnostic: Identifies root cause of flight regression after expanded biology."""
from __future__ import annotations
import os, sys, time, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from panda3d.core import loadPrcFileData, ClockObject
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")
from game.main import FlyBrainApp

def run_diagnostic(duration: float = 60.0):
    app = FlyBrainApp(headless=True, synchronous_brain=True)
    clock = ClockObject.getGlobalClock()
    sim_dt = 0.04
    total = 0.0
    
    # Accumulators
    steps = 0
    fwd_hz_sum = 0.0; steer_hz_sum = 0.0; esc_hz_sum = 0.0; bwd_hz_sum = 0.0
    feed_hz_sum = 0.0; land_hz_sum = 0.0
    fwd_speed_sum = 0.0; turn_sum = 0.0
    optic_sum = 0.0; air_sum = 0.0
    odor_l_sum = 0.0; odor_r_sum = 0.0; taste_sum = 0.0; frog_loom_sum = 0.0
    fwd_stim_sum = 0.0; stim_l_sum = 0.0; stim_r_sum = 0.0
    
    moving_fwd = 0; stationary = 0; excessive_turn = 0; escape_steps = 0
    feeding_steps = 0; grounded_steps = 0; airborne_steps = 0
    hover_steps = 0
    
    # Track decision distribution
    decisions = {}
    
    print("=" * 70)
    print(f"60-SECOND REGRESSION DIAGNOSTIC (dt={sim_dt}s)")
    print("=" * 70)
    
    while total < duration:
        if app.game_over:
            app._on_retry()
        clock.setDt(sim_dt)
        app.taskMgr.step()
        total += sim_dt
        steps += 1
        
        telem = app.brain_worker.get_telemetry()
        m = telem.motor
        s = telem.sensory
        
        fwd_hz_sum += m.fwd_pop_hz
        steer_hz_sum += m.steer_pop_hz
        esc_hz_sum += m.esc_pop_hz
        bwd_hz_sum += m.bwd_pop_hz
        feed_hz_sum += m.feeding_pop_hz
        land_hz_sum += m.landing_pop_hz
        fwd_speed_sum += m.forward_speed
        turn_sum += abs(m.turn_rate)
        
        optic_sum += s.optic_flow
        air_sum += s.airspeed
        odor_l_sum += s.odor_conc_l
        odor_r_sum += s.odor_conc_r
        taste_sum += s.taste_sugar
        frog_loom_sum += s.frog_looming
        fwd_stim_sum += s.fwd_stimulus
        stim_l_sum += s.stimulus_l
        stim_r_sum += s.stimulus_r
        
        # Classify step
        if m.forward_speed > 1.0:
            moving_fwd += 1
        elif m.forward_speed < 0.5 and abs(m.turn_rate) < 10.0:
            stationary += 1
            
        if m.forward_speed < 0.5 and abs(m.turn_rate) < 5.0:
            hover_steps += 1
            
        if abs(m.turn_rate) > 50.0:
            excessive_turn += 1
            
        if "ESCAPE" in m.decision:
            escape_steps += 1
        if "FEEDING" in m.decision:
            feeding_steps += 1
            
        if app.fly.locomotion_mode == "GROUNDED":
            grounded_steps += 1
        else:
            airborne_steps += 1
            
        dec = m.decision
        decisions[dec] = decisions.get(dec, 0) + 1
        
        # Progress logging
        if steps % 250 == 0:
            pct = total / duration * 100
            print(f"  [{pct:5.1f}%] fwd_pop={m.fwd_pop_hz:.1f} steer={m.steer_pop_hz:.1f} "
                  f"esc={m.esc_pop_hz:.1f} speed={m.forward_speed:.1f} turn={m.turn_rate:.0f} "
                  f"fwd_stim={s.fwd_stimulus:.3f} air={s.airspeed:.1f} optic={s.optic_flow:.2f} "
                  f"stim_l={s.stimulus_l:.2f} stim_r={s.stimulus_r:.2f} "
                  f"odor_l={s.odor_conc_l:.3f} odor_r={s.odor_conc_r:.3f} "
                  f"hunger={s.hunger:.2f} dec={m.decision}")
    
    n = max(1, steps)
    print("\n" + "=" * 70)
    print("DIAGNOSTIC RESULTS")
    print("=" * 70)
    
    print("\n--- NEURAL POPULATION AVERAGES ---")
    print(f"Forward Pop Hz:   {fwd_hz_sum/n:.2f}")
    print(f"Steering Pop Hz:  {steer_hz_sum/n:.2f}")
    print(f"Escape Pop Hz:    {esc_hz_sum/n:.2f}")
    print(f"Backward Pop Hz:  {bwd_hz_sum/n:.2f}")
    print(f"Feeding Pop Hz:   {feed_hz_sum/n:.2f}")
    print(f"Landing Pop Hz:   {land_hz_sum/n:.2f}")
    
    print("\n--- SENSORY AVERAGES ---")
    print(f"Optic Flow:       {optic_sum/n:.3f}")
    print(f"Airspeed:         {air_sum/n:.2f}")
    print(f"Odor L/R:         {odor_l_sum/n:.4f} / {odor_r_sum/n:.4f}")
    print(f"Taste Sugar:      {taste_sum/n:.4f}")
    print(f"Frog Looming:     {frog_loom_sum/n:.4f}")
    print(f"Fwd Stimulus:     {fwd_stim_sum/n:.4f}")
    print(f"Looming Stim L/R: {stim_l_sum/n:.4f} / {stim_r_sum/n:.4f}")
    
    print("\n--- MOTOR OUTPUT AVERAGES ---")
    print(f"Forward Speed:    {fwd_speed_sum/n:.2f}")
    print(f"|Turn Rate|:      {turn_sum/n:.1f} deg/s")
    
    print("\n--- BEHAVIOR BREAKDOWN ---")
    print(f"Moving Forward:     {moving_fwd/n*100:.1f}%  ({moving_fwd} steps)")
    print(f"Stationary/Hover:   {stationary/n*100:.1f}%  ({stationary} steps)")
    print(f"HOVER_STATIONARY:   {hover_steps/n*100:.1f}%  ({hover_steps} steps)")
    print(f"Excessive Turn:     {excessive_turn/n*100:.1f}%  ({excessive_turn} steps)")
    print(f"Escape Decisions:   {escape_steps/n*100:.1f}%  ({escape_steps} steps)")
    print(f"Feeding Decisions:  {feeding_steps/n*100:.1f}%  ({feeding_steps} steps)")
    print(f"Airborne:           {airborne_steps/n*100:.1f}%  ({airborne_steps} steps)")
    print(f"Grounded:           {grounded_steps/n*100:.1f}%  ({grounded_steps} steps)")
    
    print(f"\nDistance Travelled: {app.fly.distance_travelled:.1f}")
    print(f"Landings: {app.fly.total_landings}")
    print(f"Food Eaten: {app.fly.food_eaten}")
    
    print("\n--- DECISION DISTRIBUTION ---")
    for dec, count in sorted(decisions.items(), key=lambda x: -x[1]):
        print(f"  {dec:40s} {count:5d}  ({count/n*100:.1f}%)")
    
    print("=" * 70)
    
    app.brain_worker.stop()

if __name__ == "__main__":
    run_diagnostic(60.0)
