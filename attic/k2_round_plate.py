"""K2's ROUND-PLATE era — the one-plate interleave, SUPERSEDED.

Before the two-sided call (Jon, July 5; log 0022), K2 tried to interleave
the metronome cluster among K1's clock stations on ONE round plate. The
solve worked (massing r1-r5, see exports/k2/massing_r5.step + git
history) but the plate grew to O250 and the winding got ugly — the
two-sided architecture dissolved both problems.

Kept for the record of HOW the round solve worked. NOTE: metal_scale()
and k2_extra_envelopes() reference r5-era globals (K2_MET, k2_sweeps,
k2_gate) that no longer exist anywhere — they stopped being callable
when the two-sided layout replaced the r5 constants. The active K2
lives in calibers/k2/{brief,layout,winding}.py.
"""
from math import cos, sin, hypot, radians

from movement.solver import Sweep
from calibers.k1.revc import check_all as _core_check
from calibers.k2.brief import K2_COUNTS, LEVER_SPAN, OUTSIDE_OK, K2_METAL
from calibers.k2.layout import MZ, K2_PLATE  # mesh pairs register on import

K2_RIM = 68.0                  # plate Ø140; sweeps stay 2 inside
K2_PLATE_T = 6.5               # same stock as K1: shared print settings


def metal_scale():
    """Print reach -> metal module. (r5-era: needs k2_sweeps, gone.)"""
    cx, cy = K2_PLATE["center"]
    reach = max(hypot(s.x - cx, s.y - cy) + s.r for s in k2_sweeps()  # noqa: F821
                if s.name not in OUTSIDE_OK)
    return (K2_METAL["movement_d"] / 2) / reach       # x mm(metal)/mm(print)


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


def clock_neighbors():
    """K1's clock core as immovable neighbors — MINUS its private stem
    and crown wheel (K2 re-plumbs winding as ONE crown, TWO positions
    through the shared corridor); its flush ratchet + click stay."""
    from calibers.k1.revc import revc_sweeps, bridge_pillar_xy, cock_layout_c
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
    from calibers.k1.revc import REVC_LAYOUT
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


def _cb():
    from calibers.k1.revc import REVC_LAYOUT
    return REVC_LAYOUT["barrel"]


def k2_extra_envelopes():
    """The massing-relevant parts the r5 model forgot — reserved as real
    envelopes. (r5-era: reads K2_MET, gone; see the module header.)"""
    from math import hypot as _h
    B = K2_MET["m_barrel"]; E = K2_MET["m_escape"]; Bd = K2_MET["m_balance"]  # noqa: F821
    W = K2_MET["m_w1"]; cx, cy = K2_PLATE["center"]  # noqa: F821
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
        s.append(Sweep("m_pillar", mid[0] + 30*cos(radians(ang)),
                       mid[1] + 30*sin(radians(ang)), 4.0, 6.5, 14.7,
                       rotating=False))
    return s
