"""Caliber K2 — whole-movement model + solver (massing before geometry,
the K1 discipline inherited wholesale).

JON'S FROZEN BRIEF (log 0020): 60-180 BPM continuous, hammer tick +
desk thump, chronograph pen-cam pusher, own barrel, >=30 min at 180
per wind (the wind is a BEAT budget: the same wind lasts ~95 min at
largo 60). v2 dream: 1-2 h.

THE MOVEMENT: a standalone round caliber. Center stage belongs to the
VARIABLE-INERTIA BALANCE (the tempo mechanism is the face of this
instrument); the big barrel sits west; a two-stage train links them;
the hammer strikes an anvil boss near the south rim; the tempo knob
crowns the east rim; the pusher enters at the north.

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


def solve_k2(step=10):
    """BALANCE AT CENTER STAGE (the tempo mechanism is the face):
    balance fixed near the origin, escape at lever-span from it, w1 and
    the barrel folding west, hammer + anvil trailing the escape."""
    C = K2_COUNTS
    d_b1 = (C["barrel"] + C["p1"]) / 2
    d_1e = (C["w1"] + C["p2"]) / 2
    best = None
    bal = (14.0, 0.0)                    # slightly east: knob line short
    s_bal = k2_station_sweeps("balance", *bal)
    for a3 in range(90, 271, step):      # escape somewhere west of it
        e = (bal[0] + LEVER_SPAN * cos(radians(a3)),
             bal[1] + LEVER_SPAN * sin(radians(a3)))
        ux, uy = ((bal[0] - e[0]) / LEVER_SPAN, (bal[1] - e[1]) / LEVER_SPAN)
        s_esc = (k2_station_sweeps("escape", *e) + s_bal +
                 [Sweep("m_lever_hub", e[0] + 15 * ux, e[1] + 15 * uy,
                        11, *MZ["esc"]),
                  Sweep("m_lever_fork", e[0] + 25 * ux, e[1] + 25 * uy,
                        4.5, *MZ["esc"]),
                  # the hammer: pivot beside the cam, head arcing to an
                  # anvil boss toward the rim
                  Sweep("m_hammer", e[0] - 14 * ux, e[1] - 14 * uy,
                        9.0, MZ["esc"][1] + 0.1, MZ["esc"][1] + 2.6)])
        if k2_check(s_esc):
            continue
        for a2 in range(0, 360, step):
            w1 = (e[0] + d_1e * cos(radians(a2)),
                  e[1] + d_1e * sin(radians(a2)))
            s_w1 = s_esc + k2_station_sweeps("w1", *w1)
            if k2_check(s_w1):
                continue
            for a1 in range(0, 360, step):
                b = (w1[0] + d_b1 * cos(radians(a1)),
                     w1[1] + d_b1 * sin(radians(a1)))
                s_all = s_w1 + k2_station_sweeps("barrel", *b)
                if k2_check(s_all):
                    continue
                reach = max(hypot(s.x, s.y) + s.r for s in s_all)
                cand = (reach, dict(balance=bal,
                                    escape=(round(e[0], 1), round(e[1], 1)),
                                    w1=(round(w1[0], 1), round(w1[1], 1)),
                                    barrel=(round(b[0], 1), round(b[1], 1)),
                                    lever_span=LEVER_SPAN))
                if best is None or cand[0] < best[0]:
                    best = cand
    return best


# --- THE K2 LAYOUT (solver output, frozen; Jon's massing gate next) ------------
K2_LAYOUT = {
    "balance": (14.0, 0.0),        # center stage: the tempo mechanism
    "escape": (-14.2, 10.3),
    "w1": (21.8, 10.3),            # trainB, z-interleaved under the ring
    "barrel": (-14.6, -10.7),      # the BASEMENT drum, z7-15.5
    "lever_span": 30.0,
    # instrument furniture (massing zones; parts stage refines):
    "knob": (52.0, 0.0),           # tempo knob, east rim, lead screw to
                                   #  the balance weights
    "pusher": (0.0, 62.0),         # pen-cam run/stop, north rim
    "anvil": (-44.0, 28.0),        # hammer strikes here (plate boss)
    "winding": "key socket in the K2 bridge over the barrel arbor",
}


def k2_sweeps():
    """The frozen K2 layout as swept volumes — the K2 global gate."""
    L = K2_LAYOUT
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
          Sweep("m_knob_line", 52.0, 0.0, 5.0, *MZ["bal"]),
          Sweep("m_pusher", 0.0, 62.0, 4.0, *MZ["bal"], rotating=False)]
    return s
