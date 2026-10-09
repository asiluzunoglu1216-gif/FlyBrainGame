"""Motor Decoder for Drosophila Connectome Descending Neurons.

Translates real spikes from identified descending neurons (MaleCNS connectome)
into physical control signals (turn rate, forward drive, escape impulses).

Neurons:
- DNa02 (L/R): Steering command neurons (yaw rate)
- DNp01 (L/R): Giant Fiber neurons (escape take-off / emergency veer)
- DNg100 (L/R): Forward propulsion command neurons
- MDN (L/R): Moonwalker descending neurons (backward braking)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class MotorState:
    # Individual descending neuron firing rates (Hz)
    dna02_l_hz: float = 0.0
    dna02_r_hz: float = 0.0
    dnp01_l_hz: float = 0.0
    dnp01_r_hz: float = 0.0
    dng100_l_hz: float = 0.0
    dng100_r_hz: float = 0.0
    dng100_hz: float = 0.0
    mdn_l_hz: float = 0.0
    mdn_r_hz: float = 0.0
    mdn_hz: float = 0.0

    # Motor Population Pools (Hz per cell)
    fwd_pop_l_hz: float = 0.0      # DNg100 + DNp09 (L)
    fwd_pop_r_hz: float = 0.0      # DNg100 + DNp09 (R)
    fwd_pop_hz: float = 0.0        # Combined forward population
    steer_pop_l_hz: float = 0.0    # DNa02 + DNa01 (L)
    steer_pop_r_hz: float = 0.0    # DNa02 + DNa01 (R)
    steer_pop_hz: float = 0.0      # Combined steering population
    esc_pop_l_hz: float = 0.0      # DNp01 (L)
    esc_pop_r_hz: float = 0.0      # DNp01 (R)
    esc_pop_hz: float = 0.0        # Combined escape population
    bwd_pop_l_hz: float = 0.0      # MDN (L)
    bwd_pop_r_hz: float = 0.0      # MDN (R)
    bwd_pop_hz: float = 0.0        # Combined backward population

    # Feeding & Proboscis Extension Motor Population (CEM, MN10, cb_motor)
    feeding_pop_hz: float = 0.0
    proboscis_extension: float = 0.0  # 0.0 = retracted, 1.0 = fully extended

    # Landing / Deceleration Population (DNp02)
    landing_pop_hz: float = 0.0
    landing_readiness: float = 0.0

    # Defensive Motor Populations (DNg11 punch, pIP10 kick)
    punch_pop_hz: float = 0.0
    kick_pop_hz: float = 0.0

    # Asynchronous Flight Power (DLMn downstroke + DVMn upstroke)
    flight_power_hz: float = 0.0

    # Wing Steering Motor Neurons (b1 MN, b2 MN, i1 MN)
    wing_steer_l_hz: float = 0.0
    wing_steer_r_hz: float = 0.0

    # Central Complex Steering (PFL3 L/R)
    cx_steer_l_hz: float = 0.0
    cx_steer_r_hz: float = 0.0

    # Grooming Population (DNg12)
    groom_pop_hz: float = 0.0
    is_grooming: bool = False

    # Decoded physical motions
    turn_rate: float = 0.0          # Positive = Turn Right, Negative = Turn Left (degrees/s)
    forward_speed: float = 0.0      # Forward movement units/s
    escape_impulse: float = 0.0     # Sudden upward/veer acceleration
    decision: str = "RESTING"       # Current biological state string
    locomotion_mode: str = "AIRBORNE" # "AIRBORNE" or "GROUNDED (PHYSICS-ASSISTED)"

    @property
    def escape_pop_hz(self) -> float:
        return self.esc_pop_hz

    @property
    def escape_pop_l_hz(self) -> float:
        return self.esc_pop_l_hz

    @property
    def escape_pop_r_hz(self) -> float:
        return self.esc_pop_r_hz

    @property
    def back_pop_hz(self) -> float:
        return self.bwd_pop_hz

    @property
    def back_pop_l_hz(self) -> float:
        return self.bwd_pop_l_hz

    @property
    def back_pop_r_hz(self) -> float:
        return self.bwd_pop_r_hz


class MotorDecoder:
    def __init__(self, base_speed: float = 8.0, max_turn_rate: float = 90.0):
        self.base_speed = base_speed
        self.max_turn_rate = max_turn_rate

    def decode(self, rates: Optional[Dict[str, float]] = None, **kwargs) -> MotorState:
        """Decodes population firing rates (Hz) into physical flight parameters.

        Accepts either a dictionary or keyword arguments with:
          Individual: 'dna02_l', 'dna02_r', 'dnp01_l', 'dnp01_r', 'dng100_l', 'dng100_r', 'mdn_l', 'mdn_r'
          Populations: 'fwd_pop_l', 'fwd_pop_r', 'steer_pop_l', 'steer_pop_r', 'esc_pop_l', 'esc_pop_r', 'bwd_pop_l', 'bwd_pop_r'
          (Also supports '_hz' suffix variants, e.g. 'dng100_l_hz' or 'fwd_pop_l_hz')
        """
        combined: Dict[str, float] = {}
        if rates:
            combined.update(rates)
        if kwargs:
            combined.update(kwargs)

        # Normalize keys by removing _hz suffix
        norm_rates: Dict[str, float] = {}
        for k, v in combined.items():
            norm_rates[k] = float(v)
            if k.endswith("_hz"):
                norm_rates[k[:-3]] = float(v)
        rates = norm_rates
        # 1. Population Pools (with fallback to individual readouts if not present)
        fwd_pop_l = rates.get("fwd_pop_l", rates.get("dng100_l", 0.0))
        fwd_pop_r = rates.get("fwd_pop_r", rates.get("dng100_r", 0.0))
        fwd_pop_hz = (fwd_pop_l + fwd_pop_r) / 2.0

        steer_pop_l = rates.get("steer_pop_l", rates.get("dna02_l", 0.0))
        steer_pop_r = rates.get("steer_pop_r", rates.get("dna02_r", 0.0))
        steer_pop_hz = (steer_pop_l + steer_pop_r) / 2.0

        esc_pop_l = rates.get("esc_pop_l", rates.get("dnp01_l", 0.0))
        esc_pop_r = rates.get("esc_pop_r", rates.get("dnp01_r", 0.0))
        esc_pop_hz = (esc_pop_l + esc_pop_r) / 2.0

        bwd_pop_l = rates.get("bwd_pop_l", rates.get("mdn_l", 0.0))
        bwd_pop_r = rates.get("bwd_pop_r", rates.get("mdn_r", 0.0))
        bwd_pop_hz = (bwd_pop_l + bwd_pop_r) / 2.0

        # Feeding / Proboscis Motor Population (CEM, MN10, CB0700-0918)
        # Biological gating: In active flight (fwd_pop_hz > 1.0), proboscis extension is naturally inhibited.
        # Resting baseline is ~5.0 Hz; genuine gustatory-evoked PER occurs when feeding_pop_hz > 6.0 Hz.
        feeding_pop_hz = float(rates.get("feeding_pop", rates.get("feeding_pop_hz", 0.0)))
        if fwd_pop_hz <= 1.0 and feeding_pop_hz > 6.0 and esc_pop_hz < 6.0:
            proboscis_extension = min(1.0, max(0.0, feeding_pop_hz - 6.0) * 0.35)
        else:
            proboscis_extension = 0.0

        # Landing / Approach Deceleration Population (DNp02)
        landing_pop_hz = float(rates.get("landing_pop", rates.get("landing_pop_hz", 0.0)))
        landing_readiness = min(1.0, landing_pop_hz * 0.20) if landing_pop_hz > 0.0 else 0.0

        # Defensive Motor Populations (DNg11 punch, pIP10 kick)
        punch_pop_hz = float(rates.get("punch_pop", rates.get("punch_pop_hz", 0.0)))
        kick_pop_hz = float(rates.get("kick_pop", rates.get("kick_pop_hz", 0.0)))

        # Asynchronous Flight Power (DLMn downstroke + DVMn upstroke)
        flight_power_hz = float(rates.get("flight_power_pop", rates.get("flight_power_hz", 0.0)))

        # Wing Steering Motor Neurons (b1 MN, b2 MN, i1 MN)
        wing_steer_l = float(rates.get("wing_steer_l", rates.get("wing_steer_l_hz", 0.0)))
        wing_steer_r = float(rates.get("wing_steer_r", rates.get("wing_steer_r_hz", 0.0)))

        # Central Complex Steering (PFL3 L/R)
        cx_steer_l = float(rates.get("cx_steer_l", rates.get("cx_steer_l_hz", 0.0)))
        cx_steer_r = float(rates.get("cx_steer_r", rates.get("cx_steer_r_hz", 0.0)))

        # Grooming Motor Population (DNg12)
        groom_pop_hz = float(rates.get("groom_pop", rates.get("groom_pop_hz", 0.0)))
        is_grooming = (fwd_pop_hz <= 0.8 and groom_pop_hz > 2.0)

        # Individual readouts for backward compatibility and test verification
        dna02_l = rates.get("dna02_l", 0.0)
        dna02_r = rates.get("dna02_r", 0.0)
        dnp01_l = rates.get("dnp01_l", 0.0)
        dnp01_r = rates.get("dnp01_r", 0.0)
        dng100_l = rates.get("dng100_l", 0.0)
        dng100_r = rates.get("dng100_r", 0.0)
        dng100 = (dng100_l + dng100_r) / 2.0
        mdn_l = rates.get("mdn_l", 0.0)
        mdn_r = rates.get("mdn_r", 0.0)
        mdn = (mdn_l + mdn_r) / 2.0

        turn_rate = 0.0
        # Pure biological forward propulsion: derived strictly from forward population (DNg100 + DNp09).
        # When fwd_pop_hz = 0.0 Hz -> forward_speed = 0.0 (strictly zero artificial or baseline cruise speed).
        if fwd_pop_hz > 0.0:
            power_mod = (0.85 + 0.30 * min(2.0, flight_power_hz / 4.0)) if flight_power_hz > 0.0 else 1.0
            forward_speed = min(16.0, fwd_pop_hz * 2.4 * power_mod)
            # Biological feeding motor arrest: proboscis extension suppresses forward locomotion
            if proboscis_extension > 0.15:
                forward_speed *= max(0.0, 1.0 - proboscis_extension * 1.5)
        else:
            forward_speed = 0.0
        escape_impulse = 0.0
        decision = "HOVER_STATIONARY" if fwd_pop_hz == 0.0 else "FORWARD_PROPULSION"

        # 1. Emergency Escape via Escape Population (DNp01 Giant Fiber + DNp02)
        escape_threshold = 6.0  # Hz population rate
        if esc_pop_l > escape_threshold or esc_pop_r > escape_threshold or dnp01_l > 8.0 or dnp01_r > 8.0:
            diff_escape = esc_pop_l - esc_pop_r
            if diff_escape > 3.0:
                # Unilateral looming danger on left -> steer away to the right
                turn_rate = self.max_turn_rate * 1.5
                escape_impulse = 0.5
                decision = "ESCAPE_STEER_RIGHT"
            elif diff_escape < -3.0:
                # Unilateral looming danger on right -> steer away to the left
                turn_rate = -self.max_turn_rate * 1.5
                escape_impulse = 0.5
                decision = "ESCAPE_STEER_LEFT"
            else:
                # Bilateral / head-on looming -> pure upward escape climb (no yaw spin)
                turn_rate = 0.0
                escape_impulse = 10.0
                decision = "ESCAPE_HEADON_CLIMB"

        # 2. Visual & Locomotor Steering via Steering Population (DNa02 + DNa01, PFL3, b1/b2 MN)
        else:
            diff_steer_dn = steer_pop_l - steer_pop_r
            diff_steer_cx = cx_steer_l - cx_steer_r
            diff_steer_wing = wing_steer_l - wing_steer_r
            diff_steer = diff_steer_dn + diff_steer_cx * 0.75 + diff_steer_wing * 1.2
            steer_threshold = 1.5  # Hz differential
            if abs(diff_steer) >= steer_threshold:
                # Biological pursuit turn towards target
                # Left steering population -> turn left (+yaw_rate)
                # Right steering population -> turn right (-yaw_rate)
                sign = 1.0 if diff_steer > 0 else -1.0
                turn_rate = sign * min(55.0, (abs(diff_steer) - 1.2) * 14.0)
                decision = "TRACK_TARGET_LEFT" if diff_steer > 0 else "TRACK_TARGET_RIGHT"
            else:
                decision = "FORWARD_PROPULSION" if fwd_pop_hz > 0.0 else "HOVER_STATIONARY"

        # 3. Speed modulation via Backward Population (MDN Moonwalker brake)
        if bwd_pop_hz > 2.5 or mdn > 3.0:
            forward_speed *= 0.3
            decision += "+BRAKE"

        # 4. Proboscis Feeding Response
        if proboscis_extension > 0.20 and fwd_pop_hz < 3.0 and not decision.startswith("ESCAPE"):
            decision = "FEEDING_PROBOSCIS_ACTIVE"

        # 5. Grooming Behavior Response
        if is_grooming and not decision.startswith("ESCAPE"):
            decision = "GROOMING_FRONT_LEGS"

        return MotorState(
            dna02_l_hz=dna02_l,
            dna02_r_hz=dna02_r,
            dnp01_l_hz=dnp01_l,
            dnp01_r_hz=dnp01_r,
            dng100_l_hz=dng100_l,
            dng100_r_hz=dng100_r,
            dng100_hz=dng100,
            mdn_l_hz=mdn_l,
            mdn_r_hz=mdn_r,
            mdn_hz=mdn,
            fwd_pop_l_hz=fwd_pop_l,
            fwd_pop_r_hz=fwd_pop_r,
            fwd_pop_hz=fwd_pop_hz,
            steer_pop_l_hz=steer_pop_l,
            steer_pop_r_hz=steer_pop_r,
            steer_pop_hz=steer_pop_hz,
            esc_pop_l_hz=esc_pop_l,
            esc_pop_r_hz=esc_pop_r,
            esc_pop_hz=esc_pop_hz,
            bwd_pop_l_hz=bwd_pop_l,
            bwd_pop_r_hz=bwd_pop_r,
            bwd_pop_hz=bwd_pop_hz,
            feeding_pop_hz=feeding_pop_hz,
            proboscis_extension=proboscis_extension,
            landing_pop_hz=landing_pop_hz,
            landing_readiness=landing_readiness,
            punch_pop_hz=punch_pop_hz,
            kick_pop_hz=kick_pop_hz,
            flight_power_hz=flight_power_hz,
            wing_steer_l_hz=wing_steer_l,
            wing_steer_r_hz=wing_steer_r,
            cx_steer_l_hz=cx_steer_l,
            cx_steer_r_hz=cx_steer_r,
            groom_pop_hz=groom_pop_hz,
            is_grooming=is_grooming,
            turn_rate=turn_rate,
            forward_speed=forward_speed,
            escape_impulse=escape_impulse,
            decision=decision
        )
