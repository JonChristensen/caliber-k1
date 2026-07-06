"""Caliber K2 — whole-movement model + solver (massing before geometry,
the K1 discipline inherited wholesale).

JON'S FROZEN BRIEF (log 0020): 60-180 BPM continuous, hammer tick +
desk thump, chronograph pen-cam pusher, own barrel, >=30 min at 180
per wind (the wind is a BEAT budget: the same wind lasts ~95 min at
largo 60). v2 dream: 1-2 h.

THE MOVEMENT (Jon's correction, July 5): K2 TELLS TIME TOO — it is a
TWO-BARREL, TWO-CROWN caliber: K1's proven clock core (hands, motion
works, indirect minute — minus the moon train) plus the metronome
cluster as its complication. Different crowns wind different barrels.
The clock cluster keeps K1's frozen coordinates verbatim; the
metronome cluster (solved v0) plants east of it; the plate is the
union of two discs (a capsule outline at parts stage).

ENERGY (sizes everything): drum id66 x strip 2.6x7.0 PETG stores
~6.7 J -> ~6700 beats at SAFETY 2.5 = 38 min @180 / 113 min @60 (with
the 10 g x 2.5 mm hammer). Beats per barrel rev = (76/8)(64/8)*2*15 =
2280; usable ~3.5 turns -> ~8000 beats of gearing: spring exhausts
first, as it should.

RATE (the 9:1 problem): rate = sqrt(k/I)/2pi. Two 10g weights sliding
r5 -> r15 give I_weights 9:1; the web adds a floor, so the real span
lands ~2.6-2.8:1 — the hairspring k and web mass are TUNED at parts
stage so 60 and 180 both sit inside the sliders' travel, with margin.
"""
from math import cos, sin, pi, hypot, radians

from caliber_k1.revc import Sweep, MESH_PAIRS, check_all as _core_check
from caliber_k1.revc import spring_model

# --- the K2 plate --------------------------------------------------------------
K2_RIM = 68.0                  # plate Ø140; sweeps stay 2 inside
K2_PLATE_T = 6.5               # same stock as K1: shared print settings

# --- energy budget -------------------------------------------------------------
HAMMER = dict(mass_g=10.0, drop_mm=2.5, note="M3 steel nut in the head")
BEAT_BUDGET = 5400             # 30 min @ 180 BPM
SAFETY = 2.5
K2_SPRING = dict(drum_id=66.0, hub_d=12.0, strip_t=2.6, strip_h=7.0)


def beats_available():
    s = spring_model(**{k: v for k, v in K2_SPRING.items()})
    I_sec = K2_SPRING["strip_h"] * K2_SPRING["strip_t"] ** 3 / 12
    kappa = 2000.0 * I_sec / s["length"]
    theta = s["turns"] * 2 * pi
    energy_J = 0.5 * kappa * theta ** 2 / 1000.0
    per_beat = (HAMMER["mass_g"] / 1000 * 9.81 *
                HAMMER["drop_mm"] / 1000) + 0.15e-3
    return int(energy_J / (per_beat * SAFETY)), energy_J


# --- counts + z-map -------------------------------------------------------------
K2_COUNTS = dict(barrel=76, p1=8, w1=64, p2=8, esc_teeth=15)
# The K1 lesson, reapplied: the lever CANNOT share a band with the
# 64t wheel on this plate (hub + w1 + clearance > any legal spacing).
# The escapement gets its own storey; the escape arbor climbs to it
# (the proven K1 escape-arbor pattern, inverted).
# Jon: "you can go up and DOWN as you add gears." At its northern
# placement the met cluster clears the clock RADIALLY everywhere — so
# it adopts K1's z-grammar VERBATIM: sunken drum, bay escapement,
# plate-level balance, one bridge band. K2 is now exactly as tall as
# K1 (17.7), and both ratchets share one level: the two-position
# clutch becomes a plain horizontal keyless works.
MZ = dict(drum=(2.2, 11.0),            # sunk, like K1's
          trainA=(7.0, 10.5),          # = K1 plane A (drum gear + p1)
          trainB=(11.0, 14.5),         # = K1 plane B (w1 + p2)
          esc=(4.2, 6.7),              # = K1's BAY (recess in the north
          bal=(7.6, 11.0),             #   plate); ring on the plate
          spring=(11.7, 14.2),
          bridge=(14.7, 17.7))         # K2 tops at 17.7 — same as K1
LEVER_SPAN = 30.0


def k2_station_sweeps(kind, x, y):
    C = K2_COUNTS
    S = {
        "barrel": [Sweep("m_drum", x, y, C["barrel"] / 2 - 1.5, *MZ["drum"]),
                   Sweep("m_drum_gear", x, y, C["barrel"] / 2 + 1, *MZ["trainA"]),
                   Sweep("m_arbor", x, y, 2.85, MZ["drum"][0],
                         MZ["bridge"][1] + 1.6)],
        "w1": [Sweep("m_p1", x, y, C["p1"] / 2 + 1, *MZ["trainA"]),
               Sweep("m_w1", x, y, C["w1"] / 2 + 1, *MZ["trainB"])],
        "escape": [Sweep("m_p2", x, y, C["p2"] / 2 + 1, *MZ["trainB"]),
                   Sweep("m_esc_w", x, y, 12.0, *MZ["esc"]),
                   Sweep("m_cam", x, y, 6.0, 7.25, 8.75)],
        "balance": [Sweep("m_ring", x, y, 21.0, *MZ["bal"]),
                    Sweep("m_spring", x, y, 14.0, *MZ["spring"])],
    }
    return S[kind]


for p in [("m_drum_gear", "m_p1"), ("m_drum", "m_p1"), ("m_w1", "m_p2"),
          ("m_esc_w", "m_lever_hub"), ("m_esc_w", "m_lever_fork"),
          ("m_lever_hub", "m_lever_fork"), ("m_lever_fork", "m_ring"),
          ("m_lever_hub", "m_ring"), ("m_lever_fork", "m_spring"),
          ("m_lever_hub", "m_spring"), ("m_cam", "m_esc_w"),
          ("m_cam", "m_lever_hub"), ("m_cam", "m_hammer"),
          ("m_hammer", "m_ring"), ("m_arbor", "m_drum_gear"),
          # coplanar-escapement model overstatements (K1 lesson): the
          # hub CIRCLE overlaps the pinion/cam sweeps, the real lever's
          # nearest material (the stones, r~10.8 from E) never does —
          # the escapement probe owns these interfaces at part level
          ("m_p2", "m_lever_hub"), ("m_p2", "m_lever_fork"),
          ("m_esc_w", "m_p2")]:
    MESH_PAIRS.add(frozenset(p))


def k2_check(sweeps, clearance=2.0):
    bad = [b for b in _core_check(sweeps, clearance) if "past rim" not in b]
    for s in sweeps:
        if hypot(s.x, s.y) + s.r > K2_RIM - 2.0:
            bad.append(f"{s.name}: past K2 rim by "
                       f"{hypot(s.x, s.y) + s.r - (K2_RIM - 2.0):.1f}")
    return bad


def met_free_sweeps(bx, by, w1, e, b):
    """The metronome's stations as FREE placements (the rigid v0
    cluster died with the flat bands: its 21mm barrel-escape spacing
    needs 50.5 once the escape wheel shares z with the drum body).
    Stations interleave among the clock's — the K1 solve, replayed
    with neighbors."""
    s = k2_station_sweeps("barrel", bx, by)
    s += k2_station_sweeps("w1", *w1)
    s += k2_station_sweeps("escape", *e)
    s += k2_station_sweeps("balance", *b)
    ux, uy = ((b[0] - e[0]) / LEVER_SPAN, (b[1] - e[1]) / LEVER_SPAN)
    s += [Sweep("m_lever_hub", e[0] + 15 * ux, e[1] + 15 * uy, 11,
                *MZ["esc"]),
          Sweep("m_lever_fork", e[0] + 25 * ux, e[1] + 25 * uy, 4.5,
                *MZ["esc"]),
          Sweep("m_hammer", e[0] - 14 * ux, e[1] - 14 * uy, 9.0,
                7.25, 10.25),
          Sweep("m_ratchet", bx, by, 13.6, 16.05, 17.65)]
    return s


for p in [("m_ratchet", "m_crown_w"), ("m_ratchet", "m_arbor"),
          ("m_ratchet", "m_drum_gear"), ("m_crown_w", "m_stem")]:
    MESH_PAIRS.add(frozenset(p))


def clock_neighbors():
    """K1's clock core as immovable neighbors — MINUS its private stem
    and crown wheel (K2 re-plumbs winding as ONE crown, TWO positions
    through the shared corridor); its flush ratchet + click stay."""
    from caliber_k1.revc import revc_sweeps, bridge_pillar_xy, cock_layout_c
    s = [x for x in revc_sweeps() if x.name not in ("stem", "crown_w")]
    for px, py in bridge_pillar_xy():
        s.append(Sweep("pillar", px, py, 4.0, 6.5, 14.7, rotating=False))
    for fx, fy in cock_layout_c()["feet"]:
        s.append(Sweep("cock_foot", fx, fy, 5.0, 6.5, 14.7, rotating=False))
    return s


def k2_combined_check(met_sweeps, plate_c, plate_r, clearance=2.0):
    """ONE round plate (Jon: no frankenplates): every sweep inside the
    single circle; pairs by the shared core rules."""
    all_s = clock_neighbors() + met_sweeps
    bad = [b for b in _core_check(all_s, clearance) if "past rim" not in b]
    cx, cy = plate_c
    for s in all_s:
        if s.name in OUTSIDE_OK:
            continue
        if hypot(s.x - cx, s.y - cy) + s.r > plate_r - 2.0:
            bad.append(f"{s.name}: past the round plate")
    return bad


# ONE crown, TWO positions along one stem line (clock arbor -> met
# arbor -> rim): the met barrel may sit anywhere on the northern arc;
# the line is DERIVED from the two arbors and gated with everything.
MET_BARREL_ZONE = dict(x=(-70.0, 70.0), y=(60.0, 125.0))


def winding_line(met_arbor):
    """ONE crown, TWO positions, drawn for real. The stem line runs
    clock-arbor -> met-arbor -> rim. Position 1 (pushed): the clutch
    drives cw1's tall core (contrate at stem z13) into the CLOCK
    ratchet. Position 2 (pulled): it drives cw2, whose idler carries
    the wind to the MET ratchet. Stem passes 1.4 OVER the sunken met
    drum; crown sits outside the rim."""
    from caliber_k1.revc import REVC_LAYOUT
    cb = REVC_LAYOUT["barrel"]
    mx, my = met_arbor
    d = hypot(mx - cb[0], my - cb[1])
    ux, uy = (mx - cb[0]) / d, (my - cb[1]) / d
    s = [Sweep("cw1_core", cb[0] + 24 * ux, cb[1] + 24 * uy, 10.0,
               12.2, 13.8),
         Sweep("cw1_core", cb[0] + 24 * ux, cb[1] + 24 * uy, 13.6,
               16.05, 17.65),                       # spur tier: clock ratchet
         Sweep("cw2_core", mx + 52 * ux, my + 52 * uy, 10.0, 12.2, 13.8),
         Sweep("wind_idler", mx + 26 * ux, my + 26 * uy, 15.0,
               16.05, 17.65, rotating=False),       # met-ratchet transfer
         Sweep("cw2_core", mx + 52 * ux, my + 52 * uy, 8.0, 16.05, 17.65)]
    for k in (66, 78, 90):
        s.append(Sweep("m_stem", mx + k * ux, my + k * uy, 2.7, 10.4, 15.6))
    s.append(Sweep("k2_crown", mx + 102 * ux, my + 102 * uy, 7.0, 8.0, 18.0,
                   rotating=False))
    return s


for p in [("cw1_core", "ratchet"), ("cw1_core", "b_arbor"),
          ("cw1_core", "drum_gear"), ("cw1_core", "drum"),
          ("cw1_core", "click_zone"), ("cw1_core", "m_stem"),
          ("cw2_core", "m_stem"), ("cw2_core", "wind_idler"),
          ("cw2_core", "m_drum"), ("cw2_core", "m_drum_gear"),
          ("wind_idler", "m_ratchet"), ("wind_idler", "m_arbor"),
          ("wind_idler", "m_drum"), ("wind_idler", "m_drum_gear"),
          ("wind_idler", "m_stem"), ("m_stem", "m_drum"),
          ("m_stem", "m_drum_gear"), ("m_stem", "k2_crown"),
          ("m_ratchet", "wind_idler")]:
    MESH_PAIRS.add(frozenset(p))


OUTSIDE_OK = ("stem", "m_stem", "k2_crown",
              "m_knob_line", "m_pusher")   # rim furniture: they exit


def _enclosing_R(sweeps, cx, cy):
    return max(hypot(s.x - cx, s.y - cy) + s.r for s in sweeps
               if s.name not in OUTSIDE_OK)


def solve_k2_round(step=12, barrel_step=6):
    """The joint solve: met stations free among the clock's, flat
    z-grammar (stack 17.7), winding line derived per candidate, plate
    center + radius minimized over full survivors."""
    C = K2_COUNTS
    d_b1 = (C["barrel"] + C["p1"]) / 2
    d_1e = (C["w1"] + C["p2"]) / 2
    clock = clock_neighbors()
    best = None
    for bx in range(-80, 101, barrel_step):
        for by in range(30, 131, barrel_step):
            s0 = k2_station_sweeps("barrel", bx, by) + \
                [Sweep("m_ratchet", bx, by, 13.6, 16.05, 17.65)]
            if [x for x in _core_check(clock + s0, 2.0)
                    if "past rim" not in x]:
                continue
            for a1 in range(0, 360, step):
                w1 = (bx + d_b1 * cos(radians(a1)),
                      by + d_b1 * sin(radians(a1)))
                s1 = s0 + k2_station_sweeps("w1", *w1)
                if [x for x in _core_check(clock + s1, 2.0)
                        if "past rim" not in x]:
                    continue
                for a2 in range(0, 360, step):
                    e = (w1[0] + d_1e * cos(radians(a2)),
                         w1[1] + d_1e * sin(radians(a2)))
                    s2 = s1 + k2_station_sweeps("escape", *e)
                    if [x for x in _core_check(clock + s2, 2.0)
                            if "past rim" not in x]:
                        continue
                    for a3 in range(0, 360, step):
                        b = (e[0] + LEVER_SPAN * cos(radians(a3)),
                             e[1] + LEVER_SPAN * sin(radians(a3)))
                        s3 = met_free_sweeps(bx, by, w1, e, b) \
                            + winding_line((bx, by))
                        if [x for x in _core_check(clock + s3, 2.0)
                                if "past rim" not in x]:
                            continue
                        for pcx in range(-20, 41, 10):
                            for pcy in range(0, 81, 10):
                                R = _enclosing_R(clock + s3, pcx, pcy)
                                if best is not None and R >= best[0]:
                                    continue
                                if k2_combined_check(s3, (pcx, pcy),
                                                     R + 2.0):
                                    continue
                                best = (R, dict(
                                    m_barrel=(bx, by),
                                    m_w1=(round(w1[0], 1), round(w1[1], 1)),
                                    m_escape=(round(e[0], 1), round(e[1], 1)),
                                    m_balance=(round(b[0], 1), round(b[1], 1)),
                                    plate_c=(pcx, pcy),
                                    plate_r=round(R + 2.0, 1)))
    return best


# --- THE K2 LAYOUT (joint free-station solve, frozen; Jon's gate next) --------
# ONE round plate, FLAT stack (17.7 = K1's): the met stations interleave
# among the clock's; one crown, two positions down the derived stem line.
K2_MET = {
    "m_barrel": (40.0, 102.0),
    "m_w1": (82.0, 102.0),
    "m_escape": (93.1, 67.8),
    "m_balance": (123.1, 67.8),
}
K2_PLATE = dict(center=(30.0, 40.0), radius=125.1)


def k2_furniture():
    """Tempo knob line + pen-cam pusher, anchored from the frozen
    stations OUT to the real rim (no more floating zones)."""
    cx, cy = K2_PLATE["center"]
    b = K2_MET["m_balance"]
    e = K2_MET["m_escape"]
    d = hypot(b[0] - cx, b[1] - cy)
    ux, uy = (b[0] - cx) / d, (b[1] - cy) / d
    s = [Sweep("m_knob_line", b[0] + 26 * ux, b[1] + 26 * uy, 5.0,
               *MZ["bal"], rotating=False),
         Sweep("m_knob_line", b[0] + 38 * ux, b[1] + 38 * uy, 5.0,
               *MZ["bal"], rotating=False)]
    de = hypot(e[0] - cx, e[1] - cy)
    ex, ey = (e[0] - cx) / de, (e[1] - cy) / de
    s.append(Sweep("m_pusher", e[0] + 20 * ex, e[1] + 20 * ey, 4.0,
                   *MZ["bal"], rotating=False))
    return s


for p in [("m_knob_line", "m_ring"), ("m_knob_line", "m_spring"),
          ("m_pusher", "m_ring"), ("m_pusher", "m_hammer"),
          ("m_knob_line", "m_stem"), ("m_pusher", "m_lever_fork")]:
    MESH_PAIRS.add(frozenset(p))


def k2_sweeps():
    """The frozen met side + winding line + furniture (the clock side
    is K1's own gated model, joined in k2_combined_check)."""
    s = met_free_sweeps(K2_MET["m_barrel"][0], K2_MET["m_barrel"][1],
                        K2_MET["m_w1"], K2_MET["m_escape"],
                        K2_MET["m_balance"])
    return s + winding_line(K2_MET["m_barrel"]) + k2_furniture()


def k2_gate():
    return k2_combined_check(k2_sweeps(), K2_PLATE["center"],
                             K2_PLATE["radius"])
