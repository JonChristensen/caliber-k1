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
MZ = dict(drum=(7.0, 15.5),            # tall drum: the energy wants it
          trainA=(16.0, 17.15),        # drum gear + p1 (K1's plane trick:
          trainB=(17.35, 18.6),        #  w1 + p2 interleave above)
          esc=(18.8, 21.4),            # club wheel + lever, own storey
          bal=(21.6, 25.6),            # the variable-inertia ring
          spring=(26.1, 28.6),
          bridge=(29.1, 32.1))         # K2 tops at 32.1
LEVER_SPAN = 30.0


def k2_station_sweeps(kind, x, y):
    C = K2_COUNTS
    S = {
        "barrel": [Sweep("m_drum", x, y, C["barrel"] / 2 - 1.5, *MZ["drum"]),
                   Sweep("m_drum_gear", x, y, C["barrel"] / 2 + 1, *MZ["trainA"]),
                   Sweep("m_arbor", x, y, 2.85, MZ["drum"][0], MZ["bridge"][1])],
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
    """K1's clock core as immovable neighbors (moon lives dial-side and
    doesn't reach the bridge side; statics included)."""
    from caliber_k1.revc import revc_sweeps, bridge_pillar_xy, cock_layout_c
    s = list(revc_sweeps())
    for px, py in bridge_pillar_xy():
        s.append(Sweep("pillar", px, py, 4.0, 6.5, 14.7, rotating=False))
    for fx, fy in cock_layout_c()["feet"]:
        s.append(Sweep("cock_foot", fx, fy, 5.0, 6.5, 14.7, rotating=False))
    return s


def k2_combined_check(met_sweeps, met_center, clearance=2.0):
    """Union-of-discs plate: every sweep inside the clock disc (r83@0,0)
    OR the metronome disc; pairs by the shared core rules."""
    all_s = clock_neighbors() + met_sweeps
    bad = [b for b in _core_check(all_s, clearance) if "past rim" not in b]
    mx, my = met_center
    for s in all_s:
        if s.name == "stem":
            continue
        in_clock = hypot(s.x, s.y) + s.r <= 83.0
        in_met = hypot(s.x - mx, s.y - my) + s.r <= M_CLUSTER_RIM + 6.0
        if not (in_clock or in_met):
            bad.append(f"{s.name}: outside both plate discs")
    return bad


def solve_k2_placement(step_d=4, rots=(0, 30, 60, 90, -30, -60, -90, 180)):
    """Slide + rotate the metronome cluster against the frozen clock."""
    best = None
    for rot in rots:
        for dx in range(84, 121, step_d):
            for dy in range(-24, 25, 8):
                s, L = cluster_sweeps(dx, dy, rot)
                bad = k2_combined_check(s, (dx, dy))
                if bad:
                    continue
                span = dx + M_CLUSTER_RIM       # total east extent
                cand = (span, dict(offset=(dx, dy), rot_deg=rot))
                if best is None or cand[0] < best[0]:
                    best = cand
    return best


# --- THE K2 PLACEMENT (solver output, frozen; Jon's massing gate next) ---------
K2_PLACEMENT = dict(offset=(88.0, -16.0), rot_deg=90.0)
K2_PLATE = dict(clock=(0.0, 0.0, 85.0),          # disc center + radius
                metronome=(88.0, -16.0, 66.0))   # capsule at parts stage


def k2_sweeps():
    """The frozen combined movement (metronome side only — the clock
    side is K1's own gated model, joined in k2_combined_check)."""
    s, L = cluster_sweeps(K2_PLACEMENT["offset"][0],
                          K2_PLACEMENT["offset"][1],
                          K2_PLACEMENT["rot_deg"])
    return s


def k2_gate():
    return k2_combined_check(k2_sweeps(), K2_PLACEMENT["offset"])
