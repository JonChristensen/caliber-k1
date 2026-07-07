"""Caliber K2 — the TWO-SIDED layout (the architecture of record).

TWO-SIDED ARCHITECTURE (Jon's call, July 5): K2 is a base time movement
+ a metronome MODULE stacked toward the caseback (the chronograph-module
pattern). This DISSOLVES the frankenplate/O250 problem: the two movements
no longer fight for one plane — each gets its own full-diameter plate.

  front  crystal | dial + hands | motion works | BASE PLATE |
         base going train + escapement + balance + base bridge |
         MODULE PLATE | metronome works + hammer + variable balance |
         module bridge | display-back crystal   back

BASE = K1's proven time core verbatim (revc), minus the moon train.
MODULE = the metronome, ALONE on its own O166 plate (roomy: a single
cluster like K1's clock, not an interleave). One crown, two positions:
push winds the base barrel, pull winds the module barrel — the winding
link lives in winding.py (log 0023, SOLVED).

The superseded one-round-plate interleave lives in attic/k2_round_plate.py.
"""
from math import atan2, cos, sin, hypot, radians

from movement.solver import Sweep
from calibers.k1.revc import MESH_PAIRS, check_all as _core_check

from .brief import K2_COUNTS, LEVER_SPAN, OUTSIDE_OK

# --- the z-grammar ---------------------------------------------------------------
# The K1 lesson, reapplied. Jon: "you can go up and DOWN as you add
# gears." The metronome adopts K1's z-grammar VERBATIM: sunken drum, bay
# escapement, plate-level balance, one bridge band — 17.7 tall, same as K1.
MZ = dict(drum=(2.2, 11.0),            # sunk, like K1's
          trainA=(7.0, 10.5),          # = K1 plane A (drum gear + p1)
          trainB=(11.0, 14.5),         # = K1 plane B (w1 + p2)
          esc=(4.2, 6.7),              # = K1's BAY (recess in the plate)
          bal=(7.6, 11.0),             #   ring on the plate
          spring=(11.7, 14.2),
          bridge=(14.7, 17.7))

MODULE_R = 83.0                       # module plate = base plate (O166 print)
BASE_TOP = 17.7                       # base movement tops here (= K1)
MODULE_GAP = 0.5                      # air over the base bridge
MODULE_PLATE_Z = BASE_TOP + MODULE_GAP            # 18.2: module plate floor
# the metronome's own z-grammar (K1's, lifted onto the module plate):
MMZ = {k: (a + MODULE_PLATE_Z, b + MODULE_PLATE_Z) for k, (a, b) in MZ.items()}


# --- K2's mesh-pair exemptions, consolidated --------------------------------------
# Every intentional engagement (and modeled-overstatement exemption) the
# K2 gates rely on, registered once on import. Grouped by mechanism; the
# escapement probe owns the real interfaces at part level (the K1 lesson).
for _p in [
    # metronome train + escapement + haptic works
    ("m_drum_gear", "m_p1"), ("m_drum", "m_p1"), ("m_w1", "m_p2"),
    ("m_esc_w", "m_lever_hub"), ("m_esc_w", "m_lever_fork"),
    ("m_lever_hub", "m_lever_fork"), ("m_lever_fork", "m_ring"),
    ("m_lever_hub", "m_ring"), ("m_lever_fork", "m_spring"),
    ("m_lever_hub", "m_spring"), ("m_cam", "m_esc_w"),
    ("m_cam", "m_lever_hub"), ("m_cam", "m_hammer"),
    ("m_hammer", "m_ring"), ("m_arbor", "m_drum_gear"),
    ("m_p2", "m_lever_hub"), ("m_p2", "m_lever_fork"), ("m_esc_w", "m_p2"),
    # metronome power + winding furniture
    ("m_ratchet", "m_crown_w"), ("m_ratchet", "m_arbor"),
    ("m_ratchet", "m_drum_gear"), ("m_crown_w", "m_stem"),
    ("cw1_core", "ratchet"), ("cw1_core", "b_arbor"),
    ("cw1_core", "drum_gear"), ("cw1_core", "drum"),
    ("cw1_core", "click_zone"), ("cw1_core", "m_stem"),
    ("cw2_core", "m_stem"), ("cw2_core", "wind_idler"),
    ("cw2_core", "m_drum"), ("cw2_core", "m_drum_gear"),
    ("wind_idler", "m_ratchet"), ("wind_idler", "m_arbor"),
    ("wind_idler", "m_drum"), ("wind_idler", "m_drum_gear"),
    ("wind_idler", "m_stem"), ("m_stem", "m_drum"),
    ("m_stem", "m_drum_gear"), ("m_stem", "k2_crown"),
    # cock, roller, click, clutch works
    ("m_cock", "m_ring"), ("m_cock", "m_spring"), ("m_cock", "m_roller"),
    ("m_roller", "m_lever_fork"), ("m_roller", "m_lever_hub"),
    ("m_click", "m_ratchet"), ("m_click", "m_arbor"),
    ("m_clutch", "m_stem"), ("m_clutch", "cw2_core"),
    ("m_setting_lever", "m_clutch"), ("m_detent", "m_setting_lever"),
    ("m_setting_lever", "m_stem"), ("m_detent", "m_stem"),
    ("m_knob_line", "m_ring"), ("m_knob_line", "m_spring"),
    # winding link (position 2, log 0023)
    ("cw2_core", "m_ratchet"), ("cw2_core", "wind_xfer"),
    ("wind_xfer", "wind_riser"), ("wind_riser", "m_clutch"),
    ("m_clutch", "crown_w"), ("wind_riser", "crown_w"),
    ("m_clutch", "stem"), ("cw2_core", "m_arbor"),
    ("m_setting_lever", "wind_riser"), ("m_detent", "wind_riser"),
    ("m_setting_lever", "wind_xfer"), ("m_setting_lever", "cw2_core"),
    ("wind_base", "ratchet"), ("wind_base", "wind_xfer_base"),
    ("wind_xfer_base", "m_clutch"), ("wind_base", "b_arbor"),
    ("m_setting_lever", "wind_xfer_base"), ("m_detent", "wind_xfer"),
    ("wind_riser", "wind_xfer_base"), ("wind_base", "cw2_core"),
    ("wind_xfer", "wind_xfer_base"),
    ("wind_transfer", "m_ratchet"), ("wind_transfer", "m_arbor"),
    ("wind_transfer", "cw2_core"), ("wind_transfer", "m_drum"),
    ("wind_transfer", "m_drum_gear"),
]:
    MESH_PAIRS.add(frozenset(_p))


def module_station_sweeps(kind, x, y):
    """Metronome stations on the MODULE plate (K1 z-grammar, lifted)."""
    C = K2_COUNTS
    S = {
        "barrel": [Sweep("m_drum", x, y, C["barrel"]/2 - 1.5, *MMZ["drum"]),
                   Sweep("m_drum_gear", x, y, C["barrel"]/2 + 1, *MMZ["trainA"]),
                   Sweep("m_arbor", x, y, 2.85, MMZ["drum"][0], MMZ["bridge"][1])],
        "w1": [Sweep("m_p1", x, y, C["p1"]/2 + 1, *MMZ["trainA"]),
               Sweep("m_w1", x, y, C["w1"]/2 + 1, *MMZ["trainB"])],
        "escape": [Sweep("m_p2", x, y, C["p2"]/2 + 1, *MMZ["trainB"]),
                   Sweep("m_esc_w", x, y, 12.0, *MMZ["esc"]),
                   Sweep("m_cam", x, y, 6.0, MMZ["esc"][1]+0.05, MMZ["esc"][1]+1.55)],
        "balance": [Sweep("m_ring", x, y, 21.0, *MMZ["bal"]),
                    Sweep("m_spring", x, y, 14.0, *MMZ["spring"])],
    }
    return S[kind]


def module_free_sweeps(bx, by, w1, e, b):
    s = module_station_sweeps("barrel", bx, by)
    s += module_station_sweeps("w1", *w1)
    s += module_station_sweeps("escape", *e)
    s += module_station_sweeps("balance", *b)
    ux, uy = ((b[0]-e[0])/LEVER_SPAN, (b[1]-e[1])/LEVER_SPAN)
    s += [Sweep("m_lever_hub", e[0]+15*ux, e[1]+15*uy, 11, *MMZ["esc"]),
          Sweep("m_lever_fork", e[0]+25*ux, e[1]+25*uy, 4.5, *MMZ["esc"]),
          Sweep("m_hammer", e[0]-14*ux, e[1]-14*uy, 9.0,
                MMZ["esc"][1]+0.05, MMZ["esc"][1]+3.05),
          Sweep("m_roller", b[0], b[1], 6.0, *MMZ["esc"]),
          Sweep("m_ratchet", bx, by, 13.6, MMZ["bridge"][0]+1.35, MMZ["bridge"][1]),
          Sweep("m_click", bx+13, by-9, 6.5, MMZ["bridge"][0]+1.35, MMZ["bridge"][1])]
    return s


def solve_module_alone(step=12, barrel_step=8):
    """The metronome ALONE on its O166 module plate — a compact single-
    cluster solve (no clock to dodge). Minimize reach from plate center."""
    C = K2_COUNTS
    d_b1 = (C["barrel"] + C["p1"]) / 2
    d_1e = (C["w1"] + C["p2"]) / 2
    from calibers.k1.revc import REVC_LAYOUT
    cbx, cby = REVC_LAYOUT["barrel"]     # base barrel: one crown winds both
    best = None
    for bx in range(int(cbx)-8, int(cbx)+9, 4):
        for by in range(int(cby)-8, int(cby)+9, 4):
            s0 = module_station_sweeps("barrel", bx, by)
            if [x for x in _core_check(s0, 2.0) if "past rim" not in x]:
                continue
            for a1 in range(0, 360, step):
                w1 = (bx + d_b1*cos(radians(a1)), by + d_b1*sin(radians(a1)))
                s1 = s0 + module_station_sweeps("w1", *w1)
                if [x for x in _core_check(s1, 2.0) if "past rim" not in x]:
                    continue
                for a2 in range(0, 360, step):
                    e = (w1[0] + d_1e*cos(radians(a2)), w1[1] + d_1e*sin(radians(a2)))
                    s2 = s1 + module_station_sweeps("escape", *e)
                    if [x for x in _core_check(s2, 2.0) if "past rim" not in x]:
                        continue
                    for a3 in range(0, 360, step):
                        b = (e[0] + LEVER_SPAN*cos(radians(a3)),
                             e[1] + LEVER_SPAN*sin(radians(a3)))
                        s3 = module_free_sweeps(bx, by, w1, e, b)
                        if [x for x in _core_check(s3, 2.0) if "past rim" not in x]:
                            continue
                        reach = max(hypot(sx.x, sx.y) + sx.r for sx in s3)
                        if reach > MODULE_R - 2:
                            continue
                        if best is None or reach < best[0]:
                            best = (reach, dict(
                                barrel=(bx, by),
                                w1=(round(w1[0],1), round(w1[1],1)),
                                escape=(round(e[0],1), round(e[1],1)),
                                balance=(round(b[0],1), round(b[1],1))))
    return best


# --- THE K2 TWO-SIDED LAYOUT (frozen; Jon's gate next) -------------------------
# BASE = K1 time core (revc) verbatim, minus moon. MODULE = the metronome
# ALONE on its own O166 plate, stacked toward the caseback. Plate does NOT
# grow — same O166 as K1. One crown, two positions winds the two barrels.
K2_MODULE = dict(barrel=(0.0, 33.0), w1=(-34.0, 8.3),
                 escape=(-45.1, -25.9), balance=(-20.8, -43.6))
K2_PLATE = dict(radius=MODULE_R, center=(0.0, 0.0))  # O166, concentric


def module_sweeps():
    M = K2_MODULE
    s = module_free_sweeps(M["barrel"][0], M["barrel"][1], M["w1"],
                           M["escape"], M["balance"])
    # balance cock + its feet-pillars, on the module plate
    Bd = M["balance"]
    rad = atan2(Bd[1], Bd[0])            # rim direction through the balance
    s.append(Sweep("m_cock", Bd[0], Bd[1], 9.0, *MMZ["bridge"]))
    for sgn in (+1, -1):             # feet straddle the balance on the RIM
        a = rad + sgn * radians(44)  # side, 30 out (clear the r21 ring)
        s.append(Sweep("m_pillar", Bd[0]+30*cos(a), Bd[1]+30*sin(a), 5.0,
                       MODULE_PLATE_Z, MMZ["bridge"][0]))
    # tempo knob line (variable-inertia lead screw) exits the module rim
    s.append(Sweep("m_knob_line", Bd[0]+26*cos(rad), Bd[1]+26*sin(rad), 5.0,
                   *MMZ["bal"], rotating=False))
    return s


def base_sweeps():
    """The base time movement = K1's revc core (its own gate passed)."""
    from calibers.k1.revc import revc_sweeps
    return list(revc_sweeps())


def k2_module_gate():
    s = module_sweeps()
    bad = [b for b in _core_check(s, 2.0) if "past rim" not in b]
    for sw in s:
        if sw.name in OUTSIDE_OK:
            continue
        if hypot(sw.x, sw.y) + sw.r > MODULE_R - 2.0:
            bad.append(f"{sw.name}: past the module plate")
    return bad


# --- THE COMPONENT INVENTORY (Jon's rule: recite the full cast BEFORE
# massing; a test fails if a "sweep" part is missing from the placed
# envelopes). kind: "sweep" = owns a gate envelope; "in <parent>" = built
# at parts stage inside the parent's footprint (listed so it's never
# forgotten); "pending" = awaiting its solve.
K2_INVENTORY = [
    # power
    ("m_drum", "sweep"), ("m_drum_gear", "sweep"), ("m_arbor", "sweep"),
    ("m_ratchet", "sweep"), ("m_click", "sweep"),
    ("m_mainspring", "in m_drum"), ("m_drum_cover", "in m_drum"),
    # train
    ("m_p1", "sweep"), ("m_w1", "sweep"), ("m_p2", "sweep"),
    # escapement
    ("m_esc_w", "sweep"), ("m_lever_hub", "sweep"), ("m_lever_fork", "sweep"),
    ("m_roller", "sweep"),
    ("m_staff", "in m_ring"), ("m_banking", "in m_lever_hub"),
    ("m_pallet_strap", "in m_lever_hub"),
    # oscillator + the variable-inertia tempo works
    ("m_ring", "sweep"), ("m_spring", "sweep"), ("m_cock", "sweep"),
    ("m_weights", "in m_ring"), ("m_leadscrew", "in m_knob_line"),
    ("m_tempo_knob", "in m_knob_line"), ("m_knob_line", "sweep"),
    # haptic
    ("m_cam", "sweep"), ("m_hammer", "sweep"),
    ("m_hammer_spring", "in m_hammer"), ("m_hammer_pivot", "in m_hammer"),
    # winding: ONE crown, TWO positions (the novel keyless works)
    ("k2_crown", "sweep"), ("cw2_core", "sweep"), ("wind_riser", "sweep"),
    ("wind_xfer", "sweep"), ("m_clutch", "sweep"),
    ("m_setting_lever", "sweep"), ("m_detent", "sweep"),
    ("cw1_core", "pending"), ("m_stem", "pending"),      # pos-1 base branch
    ("wind_base", "pending"), ("wind_xfer_base", "pending"),
    ("m_clutch_spring", "in m_setting_lever"),
    # chronograph pusher (run/stop the pen-cam)
    ("m_pusher", "pending"), ("m_pusher_spring", "in m_pusher"),
    ("m_penstop", "in m_pusher"),
    # skeleton
    ("m_pillar", "sweep"), ("m_bridge", "in m_pillar"),
    ("m_train_cock", "in m_pillar"),
]
