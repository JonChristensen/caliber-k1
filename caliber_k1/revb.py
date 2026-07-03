"""Caliber K1 rev B — flat two-plate architecture (log 0009).

Two trains, one movement, selected by variant:
- "metal": classic architecture. Barrel 8h/rev -> center wheel exactly
  60 min at movement center -> third -> fourth (60 s) -> escape. This is
  what ships to a CNC factory, and what the geometry is laid out for.
- "print": same LAYOUT, faster barrel (PETG spring torque headroom),
  documented deviation. Swap = barrel tooth count + one wheel pair.

Both trains are exact by construction and tested. Geometry: all wheels
interleave into gear planes P0 (mainplate side) and P1 (bridge side),
target stack 24mm total.
"""

TRAINS = {
    # (barrel_z, center_pinion, center_z, third_pinion, third_z,
    #  fourth_pinion, fourth_z, esc_pinion) at module 1.0
    # metal: barrel 96/12 -> center 60min; center 64/8 -> third 7.5min;
    #        third 60/8 -> fourth 60s; fourth 24/12 -> escape 30s (30t, 1Hz)
    "metal": dict(barrel=72, c_pin=12, center=64, t_pin=8, third=60,
                  f_pin=8, fourth=24, e_pin=12,
                  barrel_hours=6.0, usable_turns=7.0),   # steel spring
    # print: barrel 72/16 -> center: 72/16=4.5 -> center 26.667min?? NO —
    # print keeps center at 60 min too, via barrel 96/12 but accepts the
    # torque tax with a HIGHER-torque spring (thicker strip, fewer turns):
    # runtime = turns x 8h; even 1.5 turns = 12h. Same wheels as metal.
    "print": dict(barrel=72, c_pin=12, center=64, t_pin=8, third=60,
                  f_pin=8, fourth=24, e_pin=12,
                  barrel_hours=6.0, usable_turns=1.5),   # thick PETG spring
}


def train_check(variant: str) -> dict:
    t = TRAINS[variant]
    center_min = t["barrel_hours"] * 60 / (t["barrel"] / t["c_pin"])
    third_min = center_min / (t["center"] / t["t_pin"])
    fourth_s = third_min * 60 / (t["third"] / t["f_pin"])
    esc_s = fourth_s / (t["fourth"] / t["e_pin"])
    runtime_h = t["usable_turns"] * t["barrel_hours"]
    return dict(center_min=center_min, fourth_s=fourth_s, esc_s=esc_s,
                runtime_h=runtime_h)


def revb_layout() -> dict:
    """Flat layout, center wheel at ORIGIN (hands live here). Gear planes:
    P0 z2-7 (barrel gear, center pinion, third wheel, fourth pinion),
    P1 z8-13 (center wheel, third pinion, fourth wheel, escape pinion),
    escapement z14-17, balance over the bridge z18-24. Total 24mm.
    Wave-bridge crest/tube lands on the balance center (0003 contract)."""
    from math import cos, sin, radians
    C = (0.0, 0.0)
    B = (42 * cos(radians(105)), 42 * sin(radians(105)))      # barrel
    T3 = (36 * cos(radians(-30)), 36 * sin(radians(-30)))     # third
    F = (T3[0] + 34 * cos(radians(-100)), T3[1] + 34 * sin(radians(-100)))
    E = (F[0] + 18 * cos(radians(-170)), F[1] + 18 * sin(radians(-170)))
    BAL = (E[0] + 34.5 * cos(radians(160)), E[1] + 34.5 * sin(radians(160)))
    return {"barrel": B, "center": C, "third": T3, "fourth": F,
            "escape": E, "balance": BAL}


# --- Reserved zones (claimed now so no later step squats on them) -----------
# Keyless works: crown/stem enters the plate edge at the barrel azimuth,
# running radially to a crown wheel over the barrel arbor. The edge sector
# az 90-120 and the dial-side annulus around the barrel are RESERVED.
STEM_AZIMUTH_DEG = 105.0
STEM_SECTOR_DEG = (90.0, 120.0)
# Moon phase: dial-side module (disc + aperture) per interface v0. The
# dial side owns a 5mm height budget in front of the mainplate; the moon
# disc sector az 200-280 at r 20-55 is RESERVED on the dial side.
DIAL_SIDE_BUDGET_MM = 5.0
MOON_DIAL_SECTOR = dict(az=(200.0, 280.0), r=(20.0, 55.0))
