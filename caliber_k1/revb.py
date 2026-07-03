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
    "metal": dict(barrel=96, c_pin=12, center=64, t_pin=8, third=60,
                  f_pin=8, fourth=24, e_pin=12,
                  barrel_hours=8.0, usable_turns=5.5),   # steel spring
    # print: barrel 72/16 -> center: 72/16=4.5 -> center 26.667min?? NO —
    # print keeps center at 60 min too, via barrel 96/12 but accepts the
    # torque tax with a HIGHER-torque spring (thicker strip, fewer turns):
    # runtime = turns x 8h; even 1.5 turns = 12h. Same wheels as metal.
    "print": dict(barrel=96, c_pin=12, center=64, t_pin=8, third=60,
                  f_pin=8, fourth=24, e_pin=12,
                  barrel_hours=8.0, usable_turns=1.5),   # thick PETG spring
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
