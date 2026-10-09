"""Live Onscreen HUD & Life Statistics for FlyBrainGame Living Ecosystem.

Displays:
- Real-time Engine FPS & Connectome Step Hz (Latency ms)
- Life Statistics: Alive Time, Food Eaten, Distance, Landings, Frog Encounters/Escapes, Altitude
- Internal Physiological State: Energy, Hunger, Hydration
- Clean Mode (Default) vs Detailed Neural Mode ([F4] toggle)
- Detailed Neural Mode:
  - Sensory Stimuli: Looming (LC4/LPLC2), Target (LC10a), Bilateral Odor (ORN/ALPN), Taste (BM_Taste), Legs (LgLG)
  - Motor Populations: FWD, STEER, ESCAPE, BRAKE, FEEDING (CEM/MN10), LANDING (DNp02)
  - Mushroom Body Plastic Memory: KC->MBON Synapses, PAM Reward, PPL1 Threat
- Honest Scientific Labels: [BIOLOGICAL-CONNECTOME], [PHYSICS-ASSISTED], [EXPERIMENTAL]
"""
from __future__ import annotations

import time
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, Vec4
from .brain_worker import BrainTelemetry


def make_bar(value: float, length: int = 10) -> str:
    """Generates ASCII progress bar [████░░░░░░] for 0.0 to 1.0 value."""
    clamped = max(0.0, min(1.0, value))
    filled = int(round(clamped * length))
    return "█" * filled + "░" * (length - filled)


class DebugHUD:
    def __init__(self):
        self.detailed_mode = False

        # 1. Title Banner
        self.title_text = OnscreenText(
            text="FlyBrainGame | 'A Day in the Life of a Fly' Connectome Ecosystem",
            pos=(-1.3, 0.94),
            scale=0.044,
            fg=Vec4(1.0, 0.85, 0.2, 1.0),
            align=TextNode.ALeft,
            mayChange=False
        )

        # 2. Performance & Engine Block
        self.perf_text = OnscreenText(
            text="FPS: -- | Brain Step Hz: -- (Latency: -- ms)",
            pos=(-1.3, 0.89),
            scale=0.036,
            fg=Vec4(0.3, 0.95, 0.4, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )

        # 3. Internal Physiological State Bar (Energy, Hunger, Hydration)
        self.physio_text = OnscreenText(
            text="PHYSIO: ENERGY: [██████████] 100% | HUNGER:   0% | HYDRATION: [██████████] 100%",
            pos=(-1.3, 0.84),
            scale=0.035,
            fg=Vec4(0.2, 0.9, 1.0, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )

        # 4. Life Statistics Block (Alive Time, Food, Distance, Landings, Predators)
        self.life_text = OnscreenText(
            text="ALIVE: 0.0s | FOOD: 0 | DIST: 0.0u | LANDINGS: 0 | FROG: 0 enc / 0 esc | ALT: 0.0u",
            pos=(-1.3, 0.79),
            scale=0.035,
            fg=Vec4(1.0, 0.95, 0.35, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )

        # 5. Biological Locomotion State & Decision Block
        self.state_text = OnscreenText(
            text="LOCOMOTION: AIRBORNE | Decision: SEARCH_EXPLORE | Proboscis: RETRACTED",
            pos=(-1.3, 0.74),
            scale=0.035,
            fg=Vec4(0.95, 0.95, 0.95, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )

        # 6. Mode & Safeguard Block
        self.mode_text = OnscreenText(
            text="MODE: [F1: CONNECTOME ACTIVE] | CAM: [CHASE] | HUD: CLEAN [F4 for Details]",
            pos=(-1.3, 0.69),
            scale=0.035,
            fg=Vec4(0.3, 1.0, 0.7, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )

        # --- DETAILED NEURAL HUD (Toggled via [F4]) ---
        self.sensory_text = OnscreenText(
            text="",
            pos=(-1.3, 0.63),
            scale=0.033,
            fg=Vec4(0.4, 0.85, 1.0, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )
        self.sensory_chem_text = OnscreenText(
            text="",
            pos=(-1.3, 0.58),
            scale=0.033,
            fg=Vec4(0.6, 0.85, 0.95, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )
        self.motor_text = OnscreenText(
            text="",
            pos=(-1.3, 0.53),
            scale=0.033,
            fg=Vec4(1.0, 0.65, 0.2, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )
        self.motor_sub_text = OnscreenText(
            text="",
            pos=(-1.3, 0.48),
            scale=0.033,
            fg=Vec4(1.0, 0.50, 0.2, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )
        self.memory_text = OnscreenText(
            text="",
            pos=(-1.3, 0.43),
            scale=0.033,
            fg=Vec4(0.95, 0.55, 0.95, 1.0),
            align=TextNode.ALeft,
            mayChange=True
        )

        # Temporary Food Notification Banner
        self.food_banner = OnscreenText(
            text="",
            pos=(0.0, 0.35),
            scale=0.065,
            fg=Vec4(1.0, 0.95, 0.1, 1.0),
            align=TextNode.ACenter,
            mayChange=True
        )
        self._food_banner_timer = 0.0

        # Keybindings Footer
        self.footer_text = OnscreenText(
            text="[F] Cam   [F1] Connectome   [F2] Bot   [F3] Eye Mode   [F4] Toggle Neural Details   [Space] Reset   [R] Retry   [Esc] Quit",
            pos=(0.0, -0.95),
            scale=0.033,
            fg=Vec4(0.75, 0.8, 0.85, 0.9),
            align=TextNode.ACenter,
            mayChange=False
        )

    def toggle_detailed_mode(self):
        """Toggles between clean view and detailed connectome breakdown."""
        self.detailed_mode = not self.detailed_mode
        if not self.detailed_mode:
            self.sensory_text.setText("")
            self.sensory_chem_text.setText("")
            self.motor_text.setText("")
            self.motor_sub_text.setText("")
            self.memory_text.setText("")

    def trigger_food_eaten_banner(self, food_name: str):
        self.food_banner.setText(f"★ ATE: {food_name}! (+1 Food) ★")
        self._food_banner_timer = time.time() + 3.0

    def update(
        self,
        fps: float,
        telem: BrainTelemetry,
        control_mode: str,
        fallback_active: bool,
        fly_controller,
        cam_mode: str = "CHASE",
        nearest_food: str | None = None
    ):
        if self._food_banner_timer > 0 and time.time() > self._food_banner_timer:
            self.food_banner.setText("")
            self._food_banner_timer = 0.0

        fc = fly_controller
        istate = getattr(fc, "internal_state", None)
        energy_val = istate.energy if istate else 0.85
        hunger_val = istate.hunger if istate else 0.15
        hydra_val = istate.hydration if istate else 0.90

        # 1. Performance & Connectome Status
        self.perf_text.setText(
            f"Render FPS: {fps:5.1f} | Brain: {telem.brain_step_hz:5.1f} Hz ({telem.step_latency_ms:4.1f} ms) | MaleCNS v1.0 [166,700 NEURONS ACTIVE]"
        )

        # 2. Internal Physiological State
        e_bar = make_bar(energy_val, 8)
        h_bar = make_bar(hydra_val, 8)
        self.physio_text.setText(
            f"PHYSIO: ENERGY: [{e_bar}] {energy_val*100:3.0f}% | HUNGER: {hunger_val*100:3.0f}% (Gain {istate.olfactory_gain:.1f}x) | HYDRATION: [{h_bar}] {hydra_val*100:3.0f}%"
        )

        # 3. Life statistics
        self.life_text.setText(
            f"ALIVE: {fc.alive_time:5.1f}s | FOOD: {fc.food_eaten:2d} | DIST: {fc.distance_travelled:6.1f}u | "
            f"LANDINGS: {fc.total_landings:2d} | FROG: {fc.frog_encounters:2d} enc / {fc.frog_escapes:2d} esc | "
            f"ALT: {fc.pos.z:4.1f}u"
        )

        # 4. Biological locomotion state & decision
        m = telem.motor
        prob_str = f"EXTENDED ({m.proboscis_extension:.2f})" if m.proboscis_extension > 0.05 else "RETRACTED"
        groom_str = " [GROOMING]" if m.is_grooming else ""
        self.state_text.setText(
            f"LOCOMOTION: {fc.landing_state_label} | Decision: {m.decision}{groom_str} | Proboscis: {prob_str}"
        )

        # 5. Mode, Neural Control Purity & Safeguard
        safeguard_str = "FALLBACK_SAFEGUARD [ACTIVE]" if fallback_active else "NORMAL"
        safeguard_color = Vec4(1.0, 0.3, 0.3, 1.0) if fallback_active else Vec4(0.3, 1.0, 0.7, 1.0)
        hud_view_str = "DETAILED [F4 to Clean]" if self.detailed_mode else "CLEAN [F4 for Details]"

        mode_str = "[F1: CONNECTOME ACTIVE]" if control_mode == "CONNECTOME" else "[F2: SCRIPTED BOT]"
        self.mode_text.setText(
            f"MODE: {mode_str} | CAM: [{cam_mode}] | HUD: {hud_view_str} | SAFEGUARD: [{safeguard_str}]"
        )
        self.mode_text.setFg(safeguard_color if fallback_active else Vec4(0.3, 1.0, 0.7, 1.0))

        # 6. Detailed Neural Blocks (Only shown if detailed_mode == True)
        if self.detailed_mode:
            s = telem.sensory
            target_str = f"Target: [{nearest_food}] (Az: {s.target_azimuth:+.2f})" if s.target_visible else "Target: NONE"
            self.sensory_text.setText(
                f"[CONNECTOME SENSORY] Looming(L:{s.stimulus_l:.2f}, R:{s.stimulus_r:.2f}) | {target_str} | Air: {s.airspeed:.1f}u/s | OpticFlow: {s.optic_flow:.2f}"
            )

            # Chemical & Leg Mechanosensory
            leg_c_str = "".join(["T" if c else "." for c in s.leg_contacts])
            self.sensory_chem_text.setText(
                f"[CHEMO & TACTILE] Odor: {s.odor_type}(L:{s.odor_conc_l:.2f}, R:{s.odor_conc_r:.2f}) | Taste: {s.taste_sugar:.2f} | LegTaste: {s.leg_taste:.2f} | Legs: [{leg_c_str}]"
            )

            # Motor population firing rates
            self.motor_text.setText(
                f"[POPULATION RATES Hz] FWD(DNg100/p09): {m.fwd_pop_hz:4.1f} | PWR(DLM/DVM): {m.flight_power_hz:4.1f} | STEER(DNa02): {m.steer_pop_hz:4.1f} | ESC: {m.escape_pop_hz:4.1f}"
            )
            self.motor_sub_text.setText(
                f"[MOTOR READOUTS Hz] BRAKE(MDN): {m.back_pop_hz:4.1f} | CX(PFL3): {m.cx_steer_l_hz:3.1f}/{m.cx_steer_r_hz:3.1f} | FEEDING: {m.feeding_pop_hz:4.1f} | GROOM: {m.groom_pop_hz:3.1f}"
            )

            # Persistent Mushroom Body Memory
            self.memory_text.setText(
                f"[MUSHROOM BODY MEMORY] Assoc: {telem.memory_associations:2d} | PAM(Reward): {telem.memory_appetitive_events:2d} | PPL1(Threat): {telem.memory_aversive_events:2d} | Drive: App {telem.appetitive_mbon_drive:.2f} / Av {telem.aversive_mbon_drive:.2f}"
            )
