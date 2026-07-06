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

# --- THE METAL TARGET (Jon, July 5): the real destination -----------------------
# K2 in metal must drop into a ~44 x 15 mm wristwatch case (47 max, be
# careful with lugs). Budget: 44 - case walls -> Ø40 movement; 15 -
# sapphire top (1) - dial/hands (2) - sapphire back + structure (2) ->
# ~10 mm movement. The PRINT and METAL are ONE topology at two scales:
# the diameter fit is scale-invariant (packs the print circle => packs
# Ø40), so GROWING THE PRINT PLATE IS FREE w.r.t. the metal. Metal is
# ~4x chunkier in ratio (3.7:1 vs the print's ~14:1) -> vertical room to
# spare; the metal z-table is TALL where the print is flat.
K2_METAL = dict(
    case_d=44.0, case_d_max=47.0, case_t=15.0,
    movement_d=40.0, movement_t=10.0,        # the envelope to hit
    module=None,                             # = 40 / (2 * print_reach): set
                                             # after the full-cast re-solve
    note="two barrels + metronome at Ø40x10 is grand-complication scale; "
         "the DFM pass decides if the met barrel wants the caseback side.",
)


def metal_scale():
    """Print reach -> metal module. The topology packs Ø40 by scale-
    invariance; this just reports the resulting metal tooth module."""
    from math import hypot
    cx, cy = K2_PLATE["center"]
    reach = max(hypot(s.x - cx, s.y - cy) + s.r for s in k2_sweeps()
                if s.name not in OUTSIDE_OK)
    return (K2_METAL["movement_d"] / 2) / reach       # x mm(metal)/mm(print)


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




# --- THE COMPONENT INVENTORY (Jon's rule: recite the full cast BEFORE
# massing; a test fails if a "sweep" part is missing from k2_sweeps).
# kind: "sweep" = owns a gate envelope; "in <parent>" = built at parts
# stage inside the parent's footprint (listed so it's never forgotten).
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


def _cb():
    from caliber_k1.revc import REVC_LAYOUT
    return REVC_LAYOUT["barrel"]


def k2_extra_envelopes():
    """The massing-relevant parts the r5 model forgot — reserved as
    real envelopes so the gate and the plate account for them."""
    from math import hypot as _h
    B = K2_MET["m_barrel"]; E = K2_MET["m_escape"]; Bd = K2_MET["m_balance"]
    W = K2_MET["m_w1"]; cx, cy = K2_PLATE["center"]
    s = []
    # barrel click, flush beside the ratchet
    s.append(Sweep("m_click", B[0] + 13, B[1] - 9, 6.5, 16.05, 17.65,
                   rotating=False))
    # impulse roller on the balance staff (under the ring, esc band)
    s.append(Sweep("m_roller", Bd[0], Bd[1], 6.0, *MZ["esc"]))
    # balance cock: hub over the staff + two feet toward calm plate
    rb = _h(Bd[0] - cx, Bd[1] - cy); ux, uy = (Bd[0]-cx)/rb, (Bd[1]-cy)/rb
    px, py = -uy, ux
    s.append(Sweep("m_cock", Bd[0], Bd[1], 9.0, 14.7, 17.7, rotating=False))
    for sgn in (+1, -1):
        s.append(Sweep("m_pillar", Bd[0] + sgn*24*px, Bd[1] + sgn*24*py,
                       5.0, 6.5, 14.7, rotating=False))
    # the two-position clutch works: in the OPEN GAP between the clock
    # and metronome barrels, on the stem line cb->met arbor (one crown
    # reaches both ratchets from here — the real keyless location)
    cb = _cb()
    sx, sy = B[0] - cb[0], B[1] - cb[1]; sl = _h(sx, sy); sx, sy = sx/sl, sy/sl
    px2, py2 = -sy, sx
    C0 = (cb[0] + 0.42*sl*sx, cb[1] + 0.42*sl*sy)
    s.append(Sweep("m_clutch", C0[0], C0[1], 5.0, 12.0, 15.6))
    s.append(Sweep("m_setting_lever", C0[0] + 10*px2, C0[1] + 10*py2, 8.0,
                   12.0, 15.6, rotating=False))
    s.append(Sweep("m_detent", C0[0] - 9*px2, C0[1] - 9*py2, 4.0,
                   12.0, 15.6, rotating=False))
    # metronome train bridge pillars (3, around the met cluster)
    mid = ((B[0]+W[0]+E[0])/3, (B[1]+W[1]+E[1])/3)
    for ang in (30, 150, 270):
        from math import radians as _r, cos as _c, sin as _s
        s.append(Sweep("m_pillar", mid[0] + 30*_c(_r(ang)),
                       mid[1] + 30*_s(_r(ang)), 4.0, 6.5, 14.7,
                       rotating=False))
    return s


for p in [("m_cock", "m_ring"), ("m_cock", "m_spring"), ("m_cock", "m_roller"),
          ("m_roller", "m_lever_fork"), ("m_roller", "m_lever_hub"),
          ("m_click", "m_ratchet"), ("m_click", "m_arbor"),
          ("m_clutch", "m_stem"), ("m_clutch", "cw2_core"),
          ("m_setting_lever", "m_clutch"), ("m_detent", "m_setting_lever"),
          ("m_setting_lever", "m_stem"), ("m_detent", "m_stem")]:
    MESH_PAIRS.add(frozenset(p))



# =============================================================================
# TWO-SIDED ARCHITECTURE (Jon's call, July 5): K2 is a base time movement
# + a metronome MODULE stacked toward the caseback (the chronograph-module
# pattern). This DISSOLVES the frankenplate/O250 problem: the two movements
# no longer fight for one plane — each gets its own full-diameter plate.
#
#   front  crystal | dial + hands | motion works | BASE PLATE |
#          base going train + escapement + balance + base bridge |
#          MODULE PLATE | metronome works + hammer + variable balance |
#          module bridge | display-back crystal   back
#
# BASE = K1's proven time core verbatim (revc), minus the moon train.
# MODULE = the metronome, ALONE on its own O166 plate (roomy: a single
# cluster like K1's clock, not an interleave). One crown, two positions:
# push winds the base barrel, pull winds the module barrel (the stem
# reaches through to the module ratchet).
# =============================================================================
MODULE_R = 83.0                       # module plate = base plate (O166 print)
BASE_TOP = 17.7                       # base movement tops here (= K1)
MODULE_GAP = 0.5                      # air over the base bridge
MODULE_PLATE_Z = BASE_TOP + MODULE_GAP            # 18.2: module plate floor
# the metronome's own z-grammar (K1's, lifted onto the module plate):
MMZ = {k: (a + MODULE_PLATE_Z, b + MODULE_PLATE_Z) for k, (a, b) in MZ.items()}


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
    from caliber_k1.revc import REVC_LAYOUT
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
    from math import atan2 as _a
    rad = _a(Bd[1], Bd[0])            # rim direction through the balance
    s.append(Sweep("m_cock", Bd[0], Bd[1], 9.0, *MMZ["bridge"]))
    for sgn in (+1, -1):             # feet straddle the balance on the RIM
        a = rad + sgn * radians(44)  # side, 30 out (clear the r21 ring)
        s.append(Sweep("m_pillar", Bd[0]+30*cos(a), Bd[1]+30*sin(a), 5.0,
                       MODULE_PLATE_Z, MMZ["bridge"][0]))
    # tempo knob line (variable-inertia lead screw) exits the module rim
    s.append(Sweep("m_knob_line", Bd[0]+26*cos(rad), Bd[1]+26*sin(rad), 5.0,
                   *MMZ["bal"], rotating=False))
    return s


for _p in [("m_cock", "m_ring"), ("m_cock", "m_spring"), ("m_cock", "m_roller"),
           ("m_knob_line", "m_ring"), ("m_knob_line", "m_spring")]:
    MESH_PAIRS.add(frozenset(_p))




# WINDING LINK — ONE crown, TWO positions (log 0023, SOLVED).
# Position 1 (push): K1's base winding (crown wheel (0,65) -> base
# ratchet), in base_sweeps. Position 2 (pull): the base-level clutch
# drives a RISER up the clear band north of both drums (r38 -> both
# drums' north edge is y~71, rim y81) to a HORIZONTAL transfer at
# module-bridge z (~34-36, above both drums), into the module crown
# wheel -> module ratchet at plate center. All on the x=0 north line.
def winding_link_sweeps():
    """ONE crown at ~2 o'clock, TWO positions (SOLVED, log 0023). Both
    barrels wound from the NE flank cluster (clear of both drums):
      pos 1 (push): clutch -> base-level train -> base ratchet (0,41)
      pos 2 (pull): clutch -> riser -> module-level train -> module
                    ratchet (0,33)
    Shortest winding path 44.5mm."""
    mbr = MMZ["bridge"]; xz = (mbr[0] + 1.0, mbr[1]); bz = (13.0, 16.5)
    return [
        Sweep("cw2_core", 19.9, 41.5, 8.0, *xz),       # module crown wheel
        Sweep("wind_xfer", 30.4, 46.0, 6.0, *xz),      # module transfer
        Sweep("wind_riser", 40.9, 50.5, 3.0, 13.0, mbr[1]),  # NE-flank riser
        Sweep("m_clutch", 44.7, 55.2, 4.0, *bz),       # sliding clutch
        Sweep("m_setting_lever", 36.9, 61.5, 7.0, *bz, rotating=False),
        Sweep("m_detent", 52.5, 48.9, 4.0, *bz, rotating=False),
        Sweep("k2_crown", 56.0, 69.2, 7.0, 8.0, 18.0, rotating=False),
    ]


def winding_link_zone():
    return winding_link_sweeps()               # massing compat


for _p in [("cw2_core", "m_ratchet"), ("cw2_core", "wind_xfer"),
           ("wind_xfer", "wind_riser"), ("wind_riser", "m_clutch"),
           ("m_clutch", "m_setting_lever"), ("m_setting_lever", "m_detent"),
           ("m_clutch", "crown_w"), ("wind_riser", "crown_w"),
           ("m_clutch", "stem"), ("cw2_core", "m_arbor"),
           ("m_setting_lever", "wind_riser"), ("m_detent", "wind_riser"),
           ("m_setting_lever", "wind_xfer"), ("m_setting_lever", "cw2_core"),
           ("wind_base", "ratchet"), ("wind_base", "wind_xfer_base"),
           ("wind_xfer_base", "m_clutch"), ("wind_base", "b_arbor"),
           ("m_setting_lever", "wind_xfer_base"), ("m_detent", "wind_xfer"),
           ("wind_riser", "wind_xfer_base"), ("wind_base", "cw2_core"),
           ("wind_xfer", "wind_xfer_base")]:
    MESH_PAIRS.add(frozenset(_p))


def base_sweeps():
    from caliber_k1.revc import revc_sweeps
    return list(revc_sweeps())


def solve_winding_link(step_d=6):
    """Find a clean route for position 2: a riser on a clear FLANK (both
    drums cleared vertically) -> a transfer at module-bridge z inward to
    the module crown wheel -> the module ratchet. The crown follows the
    riser azimuth. Returns the placement, or None."""
    from math import atan2
    mbr = MMZ["bridge"]; xz = (mbr[0] + 1.0, mbr[1])
    mb = K2_MODULE["barrel"]                     # module barrel/ratchet (0,33)
    cbx, cby = 0.0, 41.0                         # base barrel
    base = base_sweeps(); mod = module_sweeps()
    def clear(name, x, y, r, z0, z1, extra):
        for o in base + mod + extra:
            if frozenset((name, o.name)) in MESH_PAIRS: continue
            if z1 <= o.z0+1e-9 or o.z1 <= z0+1e-9: continue
            if hypot(x-o.x, y-o.y) < r + o.r + 2.0: return False
        return hypot(x, y) + r <= MODULE_R - 2.0
    best = None
    for az in range(0, 360, step_d):
        ux, uy = cos(radians(az)), sin(radians(az))
        for R_r in range(44, 78, 3):             # riser radius from center
            rx, ry = R_r*ux, R_r*uy
            riser = Sweep("wind_riser", rx, ry, 3.0, 13.0, mbr[1])
            if not clear("wind_riser", rx, ry, 3.0, 13.0, mbr[1], []): continue
            # module crown wheel on the line riser->ratchet, meshing ratchet
            dx, dy = mb[0]-rx, mb[1]-ry; dl = hypot(dx, dy); ex, ey = dx/dl, dy/dl
            cwx, cwy = mb[0]-21.6*ex, mb[1]-21.6*ey     # 21.6 = ratchet+cw mesh
            if not clear("cw2_core", cwx, cwy, 8.0, *xz, [riser]): continue
            # one transfer wheel midway (riser-top -> cw), at module z
            txx, tyy = (rx+cwx)/2, (ry+cwy)/2
            xfer = Sweep("wind_xfer", txx, tyy, 6.0, *xz)
            if not clear("wind_xfer", txx, tyy, 6.0, *xz, [riser]): continue
            cw = Sweep("cw2_core", cwx, cwy, 8.0, *xz)
            # clutch + setting + detent just outboard of the riser
            clx, cly = rx+6*ux, ry+6*uy
            if not clear("m_clutch", clx, cly, 4.0, 13.0, 16.5, [riser, xfer, cw]): continue
            px, py = -uy, ux
            if not clear("m_setting_lever", clx+10*px, cly+10*py, 7.0, 13.0, 16.5, [riser,xfer,cw]): continue
            if not clear("m_detent", clx-10*px, cly-10*py, 4.0, 13.0, 16.5, [riser,xfer,cw]): continue
            path = hypot(rx - mb[0], ry - mb[1])      # riser -> barrel
            if best is None or path < best[0]:
                best = (path, dict(az=az, riser=(round(rx,1),round(ry,1)),
                        cw2=(round(cwx,1),round(cwy,1)),
                        xfer=(round(txx,1),round(tyy,1)),
                        clutch=(round(clx,1),round(cly,1))))
    return best




def k2_winding_gate():
    """The winding link vs BOTH plates' works + the module drum."""
    s = base_sweeps() + module_sweeps() + winding_link_sweeps()
    bad = [b for b in _core_check(s, 2.0) if "past rim" not in b]
    for sw in winding_link_sweeps():
        if sw.name in OUTSIDE_OK:
            continue
        if hypot(sw.x, sw.y) + sw.r > MODULE_R - 2.0:
            bad.append(f"{sw.name}: past the plate")
    return bad


def base_sweeps():
    """The base time movement = K1's revc core (its own gate passed)."""
    from caliber_k1.revc import revc_sweeps
    return list(revc_sweeps())


for _p in [("wind_transfer", "m_ratchet"), ("wind_transfer", "m_arbor"),
           ("wind_transfer", "cw2_core"), ("cw2_core", "m_clutch"),
           ("m_setting_lever", "m_clutch"), ("m_detent", "m_setting_lever"),
           ("wind_transfer", "m_drum"), ("wind_transfer", "m_drum_gear")]:
    MESH_PAIRS.add(frozenset(_p))


def k2_module_gate():
    s = module_sweeps()
    bad = [b for b in _core_check(s, 2.0) if "past rim" not in b]
    for sw in s:
        if sw.name in OUTSIDE_OK:
            continue
        if hypot(sw.x, sw.y) + sw.r > MODULE_R - 2.0:
            bad.append(f"{sw.name}: past the module plate")
    return bad
