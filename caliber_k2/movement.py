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
# BOTH drums sink into the plate (Jon's call — no floating barrels):
# the met drum gets a K1-style recess (z2.2-11) in the virgin northern
# plate; its cluster placement must therefore clear the clock's planes
# RADIALLY (the north is empty once the clock's private stem yields).
MZ = dict(drum=(2.2, 11.0),            # SUNK, like K1's
          trainA=(11.5, 12.65),        # drum-top gear band + p1
          trainB=(12.85, 14.1),        # w1 + p2 interleave above
          esc=(14.3, 16.9),            # club wheel + lever, own storey
          bal=(17.1, 21.1),            # the variable-inertia ring
          spring=(21.6, 24.1),
          bridge=(24.6, 27.6))         # K2 tops at 27.6
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
                   Sweep("m_cam", x, y, 6.0, MZ["esc"][1] + 0.1,
                         MZ["esc"][1] + 1.6)],
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


CLUSTER = {          # the metronome cluster, LOCAL coordinates (v0 solve)
    "balance": (14.0, 0.0),
    "escape": (-14.2, 10.3),
    "w1": (21.8, 10.3),
    "barrel": (-14.6, -10.7),
    "lever_span": 30.0,
}
M_CLUSTER_RIM = 60.0        # local reach 57.1 + margin


def cluster_sweeps(dx=0.0, dy=0.0, rot_deg=0.0):
    """The metronome cluster as sweeps, rotated then translated."""
    from math import cos as c_, sin as s_
    ca, sa = c_(radians(rot_deg)), s_(radians(rot_deg))

    def T(p):
        return (p[0] * ca - p[1] * sa + dx, p[0] * sa + p[1] * ca + dy)

    L = {k: (T(v) if isinstance(v, tuple) else v) for k, v in CLUSTER.items()}
    s = []
    for kind, key in (("barrel", "barrel"), ("w1", "w1"),
                      ("escape", "escape"), ("balance", "balance")):
        s += k2_station_sweeps(kind, *L[key])
    e, b = L["escape"], L["balance"]
    ux, uy = ((b[0] - e[0]) / 30.0, (b[1] - e[1]) / 30.0)
    s += [Sweep("m_lever_hub", e[0] + 15 * ux, e[1] + 15 * uy, 11, *MZ["esc"]),
          Sweep("m_lever_fork", e[0] + 25 * ux, e[1] + 25 * uy, 4.5, *MZ["esc"]),
          Sweep("m_hammer", e[0] - 14 * ux, e[1] - 14 * uy, 9.0,
                MZ["esc"][1] + 0.1, MZ["esc"][1] + 2.6),
          # instrument furniture, riding the cluster frame:
          Sweep("m_knob_line", *T((52.0, 0.0)), 5.0, *MZ["bal"]),
          Sweep("m_pusher", *T((14.0, 48.0)), 4.0, *MZ["bal"], rotating=False),
          # the metronome's OWN winding station (flush ratchet + crown
          # wheel over its bridge; its crown exits the east rim)
          Sweep("m_ratchet", *L["barrel"], 13.6,
                MZ["bridge"][0] + 1.3, MZ["bridge"][1]),
          Sweep("m_crown_w", *T((-14.6 + 24.0, -10.7 - 8.0)), 13.6,
                MZ["bridge"][0] + 1.3, MZ["bridge"][1])]
    return s, L


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
               MZ["bridge"][0] + 1.3, MZ["bridge"][1] + 1.6,
               rotating=False),                     # met-ratchet transfer zone
         Sweep("cw2_core", mx + 52 * ux, my + 52 * uy, 8.0,
               MZ["bridge"][0] + 1.3, MZ["bridge"][1] + 1.6)]
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


OUTSIDE_OK = ("stem", "m_stem", "k2_crown")   # they exit/live past the rim


def _enclosing_R(sweeps, cx, cy):
    return max(hypot(s.x - cx, s.y - cy) + s.r for s in sweeps
               if s.name not in OUTSIDE_OK)


def solve_k2_round(step_d=3,
                   rots=(0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180,
                         202.5, 225, 247.5, 270, 292.5, 315, 337.5)):
    """One round plate, minimum radius. The met cluster slides under
    two constraints: the joint gate (with the winding corridor), and
    its BARREL inside the north corridor zone."""
    best = None
    clock = clock_neighbors()
    for rot in rots:
        for dx in range(-70, 71, step_d):
            for dy in range(50, 141, step_d):
                s, L = cluster_sweeps(dx, dy, rot)
                mb = L["barrel"]
                zx, zy = MET_BARREL_ZONE["x"], MET_BARREL_ZONE["y"]
                if not (zx[0] <= mb[0] <= zx[1] and zy[0] <= mb[1] <= zy[1]):
                    continue
                s = s + winding_line(mb)
                # find a near-optimal plate center for THIS placement
                for pcx in range(-16, 17, 8):
                    for pcy in range(0, 81, 8):
                        R = _enclosing_R(clock + s, pcx, pcy)
                        if best is not None and R >= best[0]:
                            continue
                        if k2_combined_check(s, (pcx, pcy), R + 2.0):
                            continue
                        best = (R, dict(offset=(dx, dy), rot_deg=rot,
                                        plate_c=(pcx, pcy),
                                        plate_r=round(R + 2.0, 1)))
    return best
# --- THE K2 PLACEMENT (solver output, frozen; Jon's massing gate next) ---------
# ONE round plate O215: clock south (frozen K1 coordinates), metronome
# a storey higher in the north, ONE crown / TWO positions down the
# shared corridor. Plate center (12,30) in clock coordinates.
K2_PLACEMENT = dict(offset=(38.0, 95.0), rot_deg=135.0)
K2_PLATE = dict(center=(16.0, 48.0), radius=125.8)


def k2_sweeps():
    """The frozen metronome side + the real winding line (the clock
    side is K1's own gated model, joined in k2_combined_check)."""
    s, L = cluster_sweeps(K2_PLACEMENT["offset"][0],
                          K2_PLACEMENT["offset"][1],
                          K2_PLACEMENT["rot_deg"])
    return s + winding_line(L["barrel"])


def k2_gate():
    return k2_combined_check(k2_sweeps(), K2_PLATE["center"],
                             K2_PLATE["radius"])
