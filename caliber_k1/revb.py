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
    "metal": dict(barrel=72, c_pin=12, center=80, t_pin=8, third=48,
                  f_pin=8, fourth=24, e_pin=12,
                  barrel_hours=6.0, usable_turns=7.0),   # steel spring
    # print: barrel 72/16 -> center: 72/16=4.5 -> center 26.667min?? NO —
    # print keeps center at 60 min too, via barrel 96/12 but accepts the
    # torque tax with a HIGHER-torque spring (thicker strip, fewer turns):
    # runtime = turns x 8h; even 1.5 turns = 12h. Same wheels as metal.
    "print": dict(barrel=72, c_pin=12, center=80, t_pin=8, third=48,
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
    t = TRAINS["metal"]
    d1 = (t["barrel"] + t["c_pin"]) / 2
    d2 = (t["center"] + t["t_pin"]) / 2
    d3 = (t["third"] + t["f_pin"]) / 2
    d4 = (t["fourth"] + t["e_pin"]) / 2
    C = (0.0, 0.0)
    B = (d1 * cos(radians(105)), d1 * sin(radians(105)))      # barrel
    T3 = (d2 * cos(radians(-30)), d2 * sin(radians(-30)))     # third
    F = (T3[0] + d3 * cos(radians(-100)), T3[1] + d3 * sin(radians(-100)))
    E = (F[0] + d4 * cos(radians(-170)), F[1] + d4 * sin(radians(-170)))
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


# --- 2c: escapement + balance z-stack (rel mainplate top) --------------------
ZB = {
    "esc_wheel": (12.5, 15.5), "lever": (12.5, 15.5),   # coplanar, clock-style
    "pallet_cock": (16.5, 18.0),                        # under the ring
    "ring": (18.5, 23.5),                               # swims in the well
    "hairspring": (24.5, 28.5),
    "cock_arm": (29.0, 32.0),                           # jewel on top
}


def escapement_layout_b() -> dict:
    """Pin-pallet geometry on rev B positions. The pallet arbor lands
    under the balance ring (dist to BAL ~21 < ring r25) — intentional:
    fork below, ring above, classic watch stacking."""
    from math import atan2, cos, sin, radians
    m = revb_layout()
    E, B = m["escape"], m["balance"]
    ang_EB = atan2(B[1] - E[1], B[0] - E[0])
    rho = 16.0 + 1.0 - 1.6                      # tip + pin_r - engage
    a = rho / cos(radians(21))
    ang_EP = ang_EB + radians(25)
    P = (E[0] + a * cos(ang_EP), E[1] + a * sin(ang_EP))
    pins = [(E[0] + rho * cos(ang_EP + s * radians(21)),
             E[1] + rho * sin(ang_EP + s * radians(21))) for s in (1, -1)]
    u_pe = ((P[0] - E[0]) / a, (P[1] - E[1]) / a)
    perp = (-u_pe[1], u_pe[0])
    feet = [(P[0] + 8 * perp[0], P[1] + 8 * perp[1]),
            (P[0] - 8 * perp[0], P[1] - 8 * perp[1])]
    return {"E": E, "B": B, "P": P, "pins": pins, "pallet_feet": feet}


def keyless_layout_b() -> dict:
    """2d: winding path. Stem enters the rim at the barrel azimuth (105 deg,
    inside the reserved 90-120 sector), axis aimed at the barrel arbor at
    z26.25 (crown-wheel mid-plane). Ratchet + crown wheel ride ABOVE the
    broad bridge (z24.5-28); click mounts on the bridge top. The crown
    wheel is a FACE GEAR (printable) meshing the stem's 10t spur pinion.
    Hand-setting: deferred to 2e (friction cannon on the center arbor)."""
    from math import cos, sin, radians
    m = revb_layout()
    bx, by = m["barrel"]
    az = radians(105)
    stem_dir = (-cos(az), -sin(az))              # rim -> inward
    crown_wheel = (bx + 24 * cos(az), by + 24 * sin(az))  # 24 = ratchet(24t)+crown(24t) mesh c-c
    stem_tip = (crown_wheel[0], crown_wheel[1])
    return {"stem_az_deg": 105.0, "stem_z": 26.25,
            "crown_wheel": crown_wheel, "ratchet": (bx, by),
            "crown_knob_r": (85.0, "at the rim, az 105"),
            "z_ratchet": (24.5, 28.0), "z_crown": (24.5, 28.0)}


def click_geometry_b() -> dict:
    """Click in the RATCHET frame (origin = ratchet center), M1's proven
    jamming layout scaled to the 24t/Ø26 wheel: block at r~20, tangential
    arm, wedge tip at r12.1 (0.9 into the teeth). CCW push runs along the
    arm axis -> tip digs in (blocks let-down); CW lifts it (winding).
    Mounted rotated -30 deg about the ratchet, SE of the wheel."""
    outline = [(16.9, -1.3), (22.1, -1.3), (22.1, 5.2), (16.9, 5.2),
               (16.9, 4.2), (4.0, 13.5), (2.9, 11.8), (4.6, 12.1),
               (16.9, 2.9)]
    pegs = [(18.0, 1.5), (21.5, 1.5)]
    return {"outline": outline, "pegs": pegs, "angle_deg": -30.0,
            "tip_r": (2.9**2 + 11.8**2) ** 0.5}


def click_peg_points_global() -> list:
    """Peg positions in movement coordinates (shared by click + bridge)."""
    from math import cos, sin, radians
    g = click_geometry_b()
    bx, by = revb_layout()["barrel"]
    a = radians(g["angle_deg"])
    return [(bx + x * cos(a) - y * sin(a), by + x * sin(a) + y * cos(a))
            for x, y in g["pegs"]]


# --- The variant switch: one geometry, two material worlds ------------------
# Set K1_VARIANT=metal (env) or pass variant= explicitly. Print and metal
# share ALL layout coordinates and wheel counts; they differ only in the
# dimension tables below — and every derived height (like the stem line)
# is computed FROM these, so flipping the switch reflows the movement.
from dataclasses import dataclass as _dc
import os as _os


@_dc(frozen=True)
class Variant:
    name: str
    drum_h: float           # barrel drum height (spring volume driver)
    usable_turns: float
    pivot_clearance: float  # running fits
    endshake: float
    spring: str             # mainspring spec
    escapement: str         # swiss_lever both worlds (log 0015); pin_pallet = fallback
    lock_deg: float         # pallet lock: deep for print error, fine for metal
    draw_deg: float
    backlash: float = 0.30  # train mesh backlash (probe-tuned print default)
    press_r: float = 0.03   # radial press-fit interference on the O3 staff


VARIANTS = {
    "print": Variant("print", 17.0, 1.5, 0.20, 0.50,
                     "PETG strip 1.6x16", "swiss_lever", 3.0, 15.0,
                     backlash=0.30, press_r=0.03),
    "metal": Variant("metal", 4.5, 7.0, 0.04, 0.10,
                     "steel 0.30x14 (spec at DFM pass)", "swiss_lever", 1.5, 13.0,
                     backlash=0.12, press_r=0.01),
}


def active_variant() -> Variant:
    return VARIANTS[_os.environ.get("K1_VARIANT", "print")]


def drum_top_z(variant: Variant = None) -> float:
    """Real drum top: plate + endshake + floor + spring space + cover."""
    v = variant or active_variant()
    return PLATE_T + 0.5 + (2.4 + v.drum_h + 2.4)


def bridge_z(variant: Variant = None) -> float:
    """Broad bridge underside: 0.5 over the tallest resident — which is
    now the high center wheel, itself 0.5 over the drum top."""
    return p1_high(variant)[1] + 0.5


def winding_wheels_z(variant: Variant = None) -> float:
    """Ratchet + crown wheel seat: recessed 1.0 into the bridge top."""
    return bridge_z(variant) + 3.0 - 1.0 + 0.5


def stem_line_z(variant: Variant = None) -> float:
    """Stem axis: face-slot mesh height above the winding wheels."""
    return winding_wheels_z(variant) + 3.5 + 2.5


# --- 2e-r: dial side, pocketed into the plate (log 0013) ---------------------
# z here = depth INTO the plate from its dial face (face = 0, going up).
# One 2.8mm pocket hosts both motion planes AND the moon train; a 0.8mm
# retaining platform closes it (date-platform analog, doubles as moon
# guard). Only pipes + hands stand proud of the face.
PLATE_T = 6.5
M2E = {
    "pocket_depth": 2.8,
    "planeA": (1.6, 2.8),        # cannon 12t + minute wheel 36t (h1.2)
    "planeB": (0.4, 1.6),        # minute pinion 10t + hour wheel 40t
    "moon_p": (1.6, 2.8),        # hour-pipe 14t + s1 63t (share plane A band)
    "moon_d": (0.2, 1.4),        # s1 pinion 8t + 105t disc, own recess
    "platform": (0.0, -0.8),     # retaining platform, proud below the face
    "dial_z": (-1.0, -1.8),
    "hour_hand_z": -2.6, "minute_hand_z": -3.4,
    "hour_mesh_module": 0.96,    # (12+36)/2*1.0 == (10+40)/2*0.96 == 24.0
    "moon_module": 0.6,
    # where dial + platform both open to show the moon (on the r18 orbit)
    "moon_aperture_az_deg": 240.0,
}


def motion_layout_b() -> dict:
    """Dial-side arbor centers. Minute arbor at r24 serves BOTH meshes
    (cannon m1.0, hour m0.96 — the classic motion-works module trick).
    Moon: pipe 14t -> s1 63t -> s1 pinion 8t -> disc 105t, all m0.6;
    the Ø64 disc tucks in the SW sector, clear of the center stack."""
    from math import cos, sin, radians
    minute = (24 * cos(radians(90)), 24 * sin(radians(90)))
    m_moon = M2E["moon_module"]
    s1 = ((14 + 63) / 2 * m_moon * cos(radians(240)),
          (14 + 63) / 2 * m_moon * sin(radians(240)))
    d = (8 + 105) / 2 * m_moon
    disc = (s1[0] + d * cos(radians(170)), s1[1] + d * sin(radians(170)))
    return {"minute": minute, "s1": s1, "disc": disc}


# --- 2e-half: gear planes (ABSOLUTE z over the plate) -------------------------
# Mesh chain: drum band(P0)->center pinion(P0); center wheel(P1)->third
# pinion(P1); third wheel(P0)->fourth pinion(P0); fourth wheel(P1)->escape
# pinion(P1); escape wheel up in its own plane under the bridge bosses.
GEAR_PLANES = {"P0": (7.0, 12.0), "P1": (13.0, 18.0), "ESC": (19.0, 22.0)}
REVB_BACKLASH = 0.30      # print-train mesh backlash (probe-tuned)


def p1_high(variant: Variant = None) -> tuple:
    """The center wheel's plane: ABOVE the drum top (the Ø66 wheel sits
    only 9mm from the barrel axis — inside the drum body's shadow at any
    lower plane; the 862mm3 probe hit). Third pinion climbs to meet it."""
    lo = drum_top_z(variant) + 1.2      # +0.7 so the ring clears below
    return (lo, lo + 5.0)


def train_upper_bearing_z(variant: Variant = None) -> float:
    """Bridge bosses hang 5 under the bridge; pivots seat from there."""
    return bridge_z(variant) - 5.0


def osc_stack(variant: Variant = None) -> dict:
    """The oscillator's homes (print variant; metal re-derives at DFM):
    ring UNDER the bridge in the well (Jon's placement — between strap
    top 23.7 and the high center wheel), hairspring + cock above."""
    v = variant or active_variant()
    bz = bridge_z(v)
    # Jon's low-profile arrangement: hairspring NESTED IN THE WELL
    # (inside the bridge's thickness, clear of the center wheel band
    # below), cock arm nearly coplanar with the bridge (1.3 riser)
    return {"ring_lo": 24.3, "ring_hi": 29.3,
            "hs_lo": bz + 0.2, "arm_lo": bz + 4.3,
            "staff_top": bz + 4.3 + 2.0}


def lever_layout_b(variant: Variant = None) -> dict:
    """Swiss lever geometry (log 0015): E, P, B COLINEAR (classic straight
    lever). Pallets embrace 2.5 tooth-spaces (+-15 deg of the 30t wheel);
    lock/draw angles come from the variant. All in movement coords."""
    from math import atan2, cos, sin, radians
    v = variant or active_variant()
    m = revb_layout()
    E, B = m["escape"], m["balance"]
    ang = atan2(B[1] - E[1], B[0] - E[0])
    r_esc = 16.0
    # pallets embrace 6.5 tooth-spaces (+-39 deg): CLOCK-scale span, so
    # the pallet arbor clears the wheel rim (2.5-space watch span put the
    # hub 0.56mm from the rim — the gating probe caught it colliding)
    span = radians(39)
    a = r_esc / cos(span)                     # 20.6
    P = (E[0] + a * cos(ang), E[1] + a * sin(ang))
    contacts = []
    r_eng = r_esc - 1.2                       # stones DIP inside the tip
    for s in (+1, -1):                        # circle by the lock depth
        th = ang + s * span
        contacts.append((E[0] + r_eng * cos(th), E[1] + r_eng * sin(th)))
    perp = (-sin(ang), cos(ang))
    feet = [(P[0] + 9 * perp[0], P[1] + 9 * perp[1]),
            (P[0] - 9 * perp[0], P[1] - 9 * perp[1])]
    return {"E": E, "P": P, "B": B, "ang": ang, "a": a, "r_esc": r_esc,
            "contacts": contacts, "span_deg": 39.0, "lock_deg": v.lock_deg,
            "draw_deg": v.draw_deg, "fork_len": (34.5 - a),
            "bridge_feet": feet}
