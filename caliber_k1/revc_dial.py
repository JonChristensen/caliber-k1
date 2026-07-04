"""Rev C dial side — the whole-face model and solver (no geometry here;
parts wait for a solved, gated layout, same discipline as revc.py).

WHAT LIVES HERE: hands at center via INDIRECT MINUTE (a 1:1 transfer
chain from the minute arbor), classic motion works (12:1), and the moon
train — all pocketed into the plate's dial face (log 0013: never floating).

THE DEPTH GAME (what makes rev C's dial side hard): the plate is 6.5
thick but its bridge side is already carved — the drum recess floor is
z2.2 (its plan edge only 12mm from center!), the escapement bay floor is
z4.0, blind bushings bottom at z3.5, strap pilots at z2.5. A dial pocket
may only go as deep as the local ceiling minus 0.6 web. So parts live in
four bands, big wheels shallow. AND one axis theorem rules the center:
the hour pipe SURROUNDS the cannon, so the cannon's gears must sit ABOVE
the hour pipe's top — the moon pinion therefore rides LOW on a short
hour pipe (B2), which also keeps the moon's first wheel out of the
motion wheel's band (they otherwise fight for the same SW plate):
  B1 (0.30-1.05): hour 40t m0.96, motion pinion 10t, w2 pinion, disc
  B2 (1.15-1.75): moon pinion 24t m0.75 (on the hour pipe), w1 wheel
  B3 (1.85-2.70): cannon 12t m1, motion wheel 36t, w1 pinion, w2 wheel
  B4 (2.80-3.60): the transfer chain 16t-24t-24t-16t m0.8 [strictest]

THE TRANSFER CHAIN (why 3 meshes, not 1): a direct 1:1 pair needs two
r13+ wheels; the one on the cannon would overhang the drum recess plan
where only 1.6 of depth exists — impossible at any band. A 16/24-24-24/16
chain (10-24-24-10) keeps every member deep-band legal and its ODD mesh
count preserves hand direction.

CHIRALITY CHAIN (documented, bench-verified at M-next): club tooth lock
leads CCW (bridge view) -> escape CCW -> fourth CW -> third CCW ->
minute wheel CW (bridge) = CCW (dial view) -> 3 transfer meshes ->
cannon CW in DIAL view: hands run clockwise. Motion works' two meshes
cancel: hour co-rotates with cannon.

RATIOS (all exact): transfer (24/16)(24/24)(16/24) = 1; motion works
(36/12)(40/10) = 12; moon: THREE stages (36/24)(54/12)(70/8) =
1.5 x 4.5 x 8.75 = 59.0625 rev of the 12h hour wheel per disc rev =
29.53125 days (1 day error per ~122 years). Why three stages: any wheel
meshing a pinion at the ORIGIN puts its rim at d/(1+ratio) from center,
and the cannon needs 7.8 clear — a 2-stage train's 4.5 ratio lands the
first wheel's rim at ~4 (rev B carried this collision silently; the
dial gate caught it). Ratio 1.5 first = rim at 8.3. QED three stages.
"""
from math import cos, sin, hypot, radians, pi

from .revc import BAY_FLOOR, PLATE_T, REVC_LAYOUT, RIM, ZC, bay_band, \
    bay_stations, bridge_pillar_xy, cock_layout_c, lever_layout_c

# --- bands: (z_lo, z_hi) measured INTO the plate from the dial face ----------
DIAL_BANDS = {
    "B1": (0.30, 1.05),
    "B2": (1.15, 1.75),
    "B3": (1.85, 2.70),
    "B4": (2.80, 3.60),
}
POCKET_AIR = 0.15          # pocket floor sits this far past the band top
WALL = 0.5                 # pocket radial wall clearance around a tip circle
WEB = 0.6                  # minimum plate web between a pocket floor and any
                           # bridge-side feature floor above it

# tooth counts / modules (see ratio table in the module docstring)
DIAL_TRAIN = dict(
    cannon=(12, 1.0), motion_w=(36, 1.0), motion_p=(10, 0.96),
    hour=(40, 0.96), moon_p=(24, 0.75), w1_w=(36, 0.75), w1_p=(12, 0.6),
    w2_w=(54, 0.6), w2_p=(8, 0.6), disc=(70, 0.6),
    transfer=(10, 0.8), idler=(24, 0.8),
)

D_MOTION = 24.0            # cannon-motion AND motion-hour (the module trick)
D_MOON1 = (24 + 36) / 2 * 0.75     # 22.5 moon pinion -> w1
D_MOON2 = (12 + 54) / 2 * 0.6      # 19.8 w1 pinion -> w2
D_MOON3 = (8 + 70) / 2 * 0.6       # 23.4 w2 pinion -> disc
D_XFER_END = (10 + 24) / 2 * 0.8   # 13.6 chain end meshes
D_XFER_MID = (24 + 24) / 2 * 0.8   # 19.2 idler-idler

TIP = dict(hour=20.1, motion_p=5.8, cannon=7.0, motion_w=19.0,
           moon_p=9.7, w1_w=14.2, w1_p=4.1, w2_w=16.8, w2_p=3.0,
           disc=21.6, transfer=4.7, idler=10.4)

DIAL_MESHES = {frozenset(p) for p in [
    ("hour", "motion_p"), ("cannon", "motion_w"), ("moon_p", "w1_w"),
    ("w1_p", "w2_w"), ("w2_p", "disc"),
    ("xfer_a", "i1"), ("i1", "i2"), ("i2", "xfer_c"),
]}


def _features():
    """Bridge-side carvings the dial pockets must respect: (x, y, plan_r,
    floor_z). floor_z <= WEB means 'never overlap'."""
    L = REVC_LAYOUT
    lv = lever_layout_c()
    Zd = L["counts"][0]
    f = [(L["barrel"][0], L["barrel"][1], Zd / 2 - 1.0, 2.2),  # drum recess
         (L["barrel"][0], L["barrel"][1], 3.5, 0.7)]           # arbor cup
    for (cx, cy), wall_r in bay_stations():
        f.append((cx, cy, wall_r, BAY_FLOOR))                  # bay recess
    (e, p), bhw = bay_band()
    for t in (0.25, 0.5, 0.75):                                # bay band, sampled
        f.append((e[0] + t * (p[0] - e[0]), e[1] + t * (p[1] - e[1]),
                  bhw, BAY_FLOOR))
    for (cx, cy) in (lv["E"], lv["P"], lv["B"]):
        f.append((cx, cy, 3.0, BAY_FLOOR - 1.8))               # bay cups
    for k in ("third", "fourth"):
        f.append((L[k][0], L[k][1], 3.0, PLATE_T - 3.0))       # bushings
    for fx, fy in lv["strap_feet"]:
        f.append((fx, fy, 2.5, PLATE_T - 4.0))                 # strap pilots
    for ax, ay in list(cock_layout_c()["feet"]) + bridge_pillar_xy():
        f.append((ax, ay, 5.5, 0.0))                           # M3 + hex: forbid
    for az in (30, 150, 270):
        f.append((78 * cos(radians(az)), 78 * sin(radians(az)),
                  4.0, 0.0))                                   # stand feet
    return f


def _depth_ok(x, y, tip_r, band, feats):
    depth = DIAL_BANDS[band][1] + POCKET_AIR
    pr = tip_r + WALL
    if hypot(x, y) + pr > RIM:
        return False
    for fx, fy, fr, floor in feats:
        if hypot(x - fx, y - fy) < pr + fr:
            if depth > floor - WEB:
                return False
    return True


def _pair_ok(a, b):
    (na, xa, ya, ra, ba), (nb, xb, yb, rb, bb) = a, b
    if ba != bb:
        return True
    d = hypot(xa - xb, ya - yb)
    if d < 0.01:                       # same axis (stacked on one pipe)
        return True
    if frozenset((na, nb)) in DIAL_MESHES:
        return True
    return d >= ra + rb + 0.8


def _shaft_ok(x, y, band, parts):
    """A r1.8 shaft/pipe crossing `band` at (x, y) vs that band's parts."""
    for (n, px, py, r, b) in parts:
        if b != band:
            continue
        d = hypot(x - px, y - py)
        if 0.01 < d < r + 1.8 + 0.8:
            return False
    return True


def solve_dial(step_deg=15):
    """Staged compass walk over the four free azimuths; every candidate
    passes the same-band clearances, the shaft crossings, and the depth
    rules before the next stage opens. Returns the most compact face."""
    L = REVC_LAYOUT
    mx, my = L["minute"]
    feats = _features()
    fixed = [("hour", 0.0, 0.0, TIP["hour"], "B1"),
             ("cannon", 0.0, 0.0, TIP["cannon"], "B3"),
             ("moon_p", 0.0, 0.0, TIP["moon_p"], "B2"),
             ("xfer_c", 0.0, 0.0, TIP["transfer"], "B4"),
             ("xfer_a", mx, my, TIP["transfer"], "B4")]
    for p in fixed:
        if not _depth_ok(p[1], p[2], p[3], p[4], feats):
            return None
    best = None
    angles = [radians(a) for a in range(0, 360, step_deg)]
    for tw1 in angles:
      w1 = (D_MOON1 * cos(tw1), D_MOON1 * sin(tw1))
      w1p = [("w1_w", w1[0], w1[1], TIP["w1_w"], "B2"),
             ("w1_p", w1[0], w1[1], TIP["w1_p"], "B3")]
      if not all(_depth_ok(p[1], p[2], p[3], p[4], feats) for p in w1p):
          continue
      if not all(_pair_ok(a, b) for a in w1p for b in fixed):
          continue
      for tw2 in angles:
        w2 = (w1[0] + D_MOON2 * cos(tw2), w1[1] + D_MOON2 * sin(tw2))
        w2p = [("w2_w", w2[0], w2[1], TIP["w2_w"], "B3"),
               ("w2_p", w2[0], w2[1], TIP["w2_p"], "B1")]
        if not all(_depth_ok(p[1], p[2], p[3], p[4], feats) for p in w2p):
            continue
        if not all(_pair_ok(a, b) for a in w2p for b in fixed + w1p):
            continue
        for td in angles:
            dc = (w2[0] + D_MOON3 * cos(td), w2[1] + D_MOON3 * sin(td))
            disc = ("disc", dc[0], dc[1], TIP["disc"], "B1")
            if not _depth_ok(dc[0], dc[1], TIP["disc"], "B1", feats):
                continue
            if not all(_pair_ok(disc, b) for b in fixed + w1p + w2p):
                continue
            if not _shaft_ok(w2[0], w2[1], "B2", fixed + w1p):
                continue                       # w2 shaft crosses B2
            for tm in angles:
                mo = (D_MOTION * cos(tm), D_MOTION * sin(tm))
                mop = [("motion_w", mo[0], mo[1], TIP["motion_w"], "B3"),
                       ("motion_p", mo[0], mo[1], TIP["motion_p"], "B1")]
                so_far = fixed + w1p + w2p + [disc]
                if not all(_depth_ok(p[1], p[2], p[3], p[4], feats)
                           for p in mop):
                    continue
                if not all(_pair_ok(a, b) for a in mop for b in so_far):
                    continue
                if not _shaft_ok(mo[0], mo[1], "B2", so_far):
                    continue                       # motion shaft crosses B2
                # the i2 ring's legal windows can be <10 deg wide
                # (squeezed between the drum plan, the bay and a strap
                # pilot) — walk it finer than the outer stages
                for ti2 in range(0, 360 * 3, step_deg):
                    ti = radians(ti2 / 3)
                    i2 = (D_XFER_END * cos(ti), D_XFER_END * sin(ti))
                    # i1 = circle(i2, 19.2) x circle(minute arbor, 16.0)
                    ddx, ddy = mx - i2[0], my - i2[1]
                    dd = hypot(ddx, ddy)
                    if not (abs(D_XFER_MID - D_XFER_END) + 0.5 < dd
                            < D_XFER_MID + D_XFER_END - 0.5):
                        continue
                    a_ = (D_XFER_MID**2 - D_XFER_END**2 + dd**2) / (2 * dd)
                    h2 = D_XFER_MID**2 - a_**2
                    if h2 <= 0:
                        continue
                    h = h2 ** 0.5
                    for sgn in (+1, -1):
                        i1 = (i2[0] + a_ * ddx / dd - sgn * h * ddy / dd,
                              i2[1] + a_ * ddy / dd + sgn * h * ddx / dd)
                        chain = [("i2", i2[0], i2[1], TIP["idler"], "B4"),
                                 ("i1", i1[0], i1[1], TIP["idler"], "B4")]
                        parts = so_far + mop
                        if not all(_depth_ok(p[1], p[2], p[3], p[4], feats)
                                   for p in chain):
                            continue
                        if not all(_pair_ok(a, b) for a in chain
                                   for b in parts):
                            continue
                        if not _pair_ok(chain[0], chain[1]):
                            continue
                        allp = parts + chain
                        reach = max(hypot(p[1], p[2]) + p[3] for p in allp)
                        cand = (reach, dict(
                            w1=(round(w1[0], 2), round(w1[1], 2)),
                            w2=(round(w2[0], 2), round(w2[1], 2)),
                            disc=(round(dc[0], 2), round(dc[1], 2)),
                            motion=(round(mo[0], 2), round(mo[1], 2)),
                            i1=(round(i1[0], 2), round(i1[1], 2)),
                            i2=(round(i2[0], 2), round(i2[1], 2))))
                        if best is None or cand[0] < best[0]:
                            best = cand
    return best


# --- THE DIAL LAYOUT (solver output, frozen; reach 64.3 of 83) ----------------
DIAL_LAYOUT = {
    "w1": (21.73, -5.82),      # moon stage 1 (B2 wheel / B3 pinion)
    "w2": (40.86, -10.95),     # moon stage 2 (B3 wheel / B1 pinion)
    "disc": (29.16, -31.21),   # 70t moon disc, B1 — window ~6 o'clock
    "motion": (-23.18, -6.21), # motion arbor (B1 pinion / B3 wheel)
    "i1": (-31.04, 9.92),      # transfer idlers, B4
    "i2": (-13.39, 2.36),
}


def dial_parts_list(layout=None):
    """The face as (name, x, y, tip_r, band) — THE dial gate's input."""
    L = layout or DIAL_LAYOUT
    mx, my = REVC_LAYOUT["minute"]
    return [
        ("hour", 0.0, 0.0, TIP["hour"], "B1"),
        ("cannon", 0.0, 0.0, TIP["cannon"], "B3"),
        ("moon_p", 0.0, 0.0, TIP["moon_p"], "B2"),
        ("xfer_c", 0.0, 0.0, TIP["transfer"], "B4"),
        ("xfer_a", mx, my, TIP["transfer"], "B4"),
        ("w1_w", *L["w1"], TIP["w1_w"], "B2"),
        ("w1_p", *L["w1"], TIP["w1_p"], "B3"),
        ("w2_w", *L["w2"], TIP["w2_w"], "B3"),
        ("w2_p", *L["w2"], TIP["w2_p"], "B1"),
        ("disc", *L["disc"], TIP["disc"], "B1"),
        ("motion_w", *L["motion"], TIP["motion_w"], "B3"),
        ("motion_p", *L["motion"], TIP["motion_p"], "B1"),
        ("i1", *L["i1"], TIP["idler"], "B4"),
        ("i2", *L["i2"], TIP["idler"], "B4"),
    ]


DIAL_SHEET = (-1.9, -0.9)   # reserved: the dial sheet rides the platform;
                            # hour hand seat -2.4, minute -3.4 clear it

POST_ARBORS = {"motion": "B3", "w1": "B3", "w2": "B3",
               "disc": "B1", "i1": "B4", "i2": "B4"}


def post_specs(layout=None):
    """(name, x, y, tip_z, bore_top): each Ø2 register post runs from
    z-0.7 (a platform support/locating pin, the dial-feet analog) up
    into a press bore whose depth respects the SAME feature rules as
    the pockets (the disc post caps at the bay floor - 0.6)."""
    L = layout or DIAL_LAYOUT
    feats = _features()
    out = []
    for name, band in POST_ARBORS.items():
        x, y = L[name]
        top = 5.9
        for fx, fy, fr, floor in feats:
            if hypot(x - fx, y - fy) < 1.0 + 1.0 + fr:
                top = min(top, floor - WEB)
        assert top >= DIAL_BANDS[band][1] + 0.5, f"post {name} can't anchor"
        out.append((name, x, y, -0.7, top))
    return out


def check_dial(layout=None):
    """THE dial gate: every part depth-legal and pairwise clear."""
    feats = _features()
    parts = dial_parts_list(layout)
    bad = []
    for (n, x, y, r, b) in parts:
        if not _depth_ok(x, y, r, b, feats):
            bad.append(f"{n}: depth/feature violation at ({x:.1f},{y:.1f})")
    for i, a in enumerate(parts):
        for b in parts[i + 1:]:
            if not _pair_ok(a, b):
                bad.append(f"{a[0]} x {b[0]}: same-band clash")
    for name, x, y, tip, top in post_specs(layout):
        pass                    # post_specs asserts its own feasibility
    mo = layout or DIAL_LAYOUT
    for shaft_of in ("motion", "w2"):
        sx, sy = mo[shaft_of]
        others = [p for p in parts if hypot(p[1] - sx, p[2] - sy) > 0.01]
        if not _shaft_ok(sx, sy, "B2", others):
            bad.append(f"{shaft_of} shaft x B2")
    return bad
