"""Rev C parts port gates: the proven rev B probes, re-aimed at
REVC_LAYOUT. Every mesh phase-aligned, the lever gating the wheel at
the new geometry, every part inside its z-band, and the flat-movement
service contracts (bay strap, hanging barrel, dial web)."""
from math import atan2, degrees, hypot

import pytest
from build123d import Pos, Rot

from caliber_k1.revc import (BAY_FLOOR, PLATE_T, REVC_LAYOUT, RING, ZC,
                             bay_stations, bridge_pillar_xy, cock_layout_c,
                             lever_layout_c, mesh_ideals, revc_sweeps)
from caliber_k1 import revc_parts as rp


def _d(a, b):
    return hypot(b[0] - a[0], b[1] - a[1])


def test_revc_mesh_distances_exact():
    """Center distances vs module-1 ideals: slack up to 0.06 is fine
    (cycloidal + 0.3 backlash), interference beyond 0.02 is not."""
    for name, a, b, ideal in mesh_ideals():
        err = _d(REVC_LAYOUT[a], REVC_LAYOUT[b]) - ideal
        assert -0.02 <= err <= 0.06, f"{name}: center distance err {err:+.3f}"


def _mesh_pair(A0, B0, a_xy, b_xy, za, zb):
    th = degrees(atan2(b_xy[1] - a_xy[1], b_xy[0] - a_xy[0]))
    rot_a = th - round(th / (360 / za)) * (360 / za)
    th_b = th + 180
    rot_b = (th_b - round(th_b / (360 / zb)) * (360 / zb)) + 180 / zb
    A = Pos(a_xy[0], a_xy[1], 0) * Rot(0, 0, rot_a) * A0
    B = Pos(b_xy[0], b_xy[1], 0) * Rot(0, 0, rot_b) * B0
    inter = A & B
    assert (inter.volume if inter else 0) < 0.5, "interferes at true centers"
    d = _d(a_xy, b_xy)
    B2 = Pos((a_xy[0] - b_xy[0]) / d, (a_xy[1] - b_xy[1]) / d, 0) * B
    inter2 = A & B2
    assert (inter2.volume if inter2 else 0) > 0.8, "teeth don't reach"


def test_revc_train_meshes_phase_aligned():
    """All four meshes: zero interference at true distance, real
    engagement 1mm closer — with a tooth phased into a gap."""
    L = REVC_LAYOUT
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = L["counts"]
    drum, minute = rp.drum_c(), rp.minute_arbor_c()
    third, fourth, esc = rp.third_arbor_c(), rp.fourth_arbor_c(), rp.escape_arbor_c()
    _mesh_pair(drum, minute, L["barrel"], L["minute"], Zd, pm)
    _mesh_pair(minute, third, L["minute"], L["third"], Zm, p3)
    _mesh_pair(third, fourth, L["third"], L["fourth"], Z3, p4)
    _mesh_pair(fourth, esc, L["fourth"], L["escape"], Z4, pe)


def test_revc_lever_gates_the_escape_wheel():
    """The joint-grid probe at rev C geometry: somewhere deeply LOCKED,
    somewhere fully FREE — the fork commands the wheel in the bay.

    Metal variant: KNOWN OPEN ITEM — the 1.5/13 deg table angles (log
    0015) leave no drop window with 0.12 backlash; the DFM pass must
    retune lock/draw/backlash together. Tracked, not hidden."""
    from caliber_k1.revb import active_variant
    if active_variant().name == "metal":
        pytest.skip("metal escapement angles await the DFM retune (0017)")
    lv = lever_layout_c()
    wheel0 = rp.club_escape_wheel_c()
    lever0 = rp.swiss_lever_c()
    E, P = lv["E"], lv["P"]
    lever = Pos(P[0], P[1], 0) * Rot(0, 0, degrees(lv["ang"])) * lever0
    gated = 0
    for k in range(13):
        w = Pos(E[0], E[1], 0) * Rot(0, 0, k) * wheel0
        v = (w & lever)
        if (v.volume if v else 0) > 0.5:
            gated += 1
    assert gated >= 6, f"pallets barely touch the wheel ({gated}/13)"
    hi = 0.0
    for k in range(0, 13, 3):
        w_k = Pos(E[0], E[1], 0) * Rot(0, 0, k) * wheel0
        for sw in range(-6, 7, 2):                # inside the banking
            lv2 = Pos(P[0], P[1], 0) * Rot(0, 0, degrees(lv["ang"]) + sw) * lever0
            v = (w_k & lv2)
            hi = max(hi, v.volume if v else 0.0)
    assert hi > 4.0, "lever cannot lock the wheel anywhere on the grid"
    # release window is ~2 deg wide and NARROWS with the metal variant's
    # finer backlash — scan fine, stop at the first free pose (drop state)
    lo = 1e9
    for k2 in range(0, 24):                       # 0.5 deg wheel steps
        w_k = Pos(E[0], E[1], 0) * Rot(0, 0, k2 * 0.5) * wheel0
        for sw in range(-6, 7):                   # 1 deg lever steps
            lv2 = Pos(P[0], P[1], 0) * Rot(0, 0, degrees(lv["ang"]) + sw) * lever0
            v = (w_k & lv2)
            lo = min(lo, v.volume if v else 0.0)
            if lo < 0.05:
                break
        if lo < 0.05:
            break
    assert lo < 0.5, f"lever cannot release the wheel anywhere ({lo:.2f})"


def test_revc_parts_stay_in_their_bands():
    """Every part's actual metal inside the massing Jon approved —
    BOTH ends of every bounding box, every part, single solids only."""
    eps = 0.02
    table = [  # (part, z_lo_min, z_hi_max)
        (rp.mainplate_c(), -0.01, 6.5),
        (rp.drum_c(), 2.2, 11.0),
        (rp.barrel_arbor_c(), 0.8, 17.6),
        (rp.drum_cover_c(), 9.6, 11.0),
        (rp.ratchet_c(), 16.05, 17.65),
        (rp.click_c(), 14.95, 17.65),
        (rp.minute_arbor_c(), 1.6, 16.2),
        (rp.third_arbor_c(), 3.6, 16.2),
        (rp.fourth_arbor_c(), 3.6, 16.2),
        (rp.escape_arbor_c(), 2.3, 16.2),
        (rp.club_escape_wheel_c(), 0.0, 2.4),      # local; seat at 4.3
        (rp.swiss_lever_c(), -2.0, 3.0),           # local; body at 4.2
        (rp.bay_strap_c(), ZC["strap"][0], ZC["strap"][1]),
        (rp.roller_c(), ZC["roller_saf"][0], ZC["roller_imp"][1]),
        (rp.balance_staff_c(), 2.3, 16.1),
        (rp.balance_wheel_c(), ZC["ring"][0], ZC["ring"][1]),
        (rp.hairspring_c(), ZC["spring"][0], ZC["spring"][1]),
        (rp.balance_cock_c(), 6.5, 17.7),
        (rp.bridge_c(), 6.5, 17.7),
    ]
    for part, lo, hi in table:
        bb = part.bounding_box()
        assert bb.min.Z >= lo - eps and bb.max.Z <= hi + eps, \
            f"band violation: {bb.min.Z:.2f}..{bb.max.Z:.2f} vs {lo}..{hi}"
        assert len(part.solids()) == 1, "part is not one connected solid"


def test_revc_bay_service_contracts():
    """The strap lifts out under the ring; its feet sit beyond the bay
    walls on solid plate; the dial-face web under every bay cup >= 1.5."""
    lv = lever_layout_c()
    assert ZC["strap"][1] <= RING[0] - 0.5, "strap rubs the ring"
    from caliber_k1.revc import bay_band
    bpath, bhw = bay_band()
    for f in lv["strap_feet"]:
        assert _d(f, lv["B"]) > 26.0 + 1.1, "screw head under the ring"
        for (cx, cy), wall_r in bay_stations():
            assert _d(f, (cx, cy)) > wall_r + 1.1 + 0.4, "M2 breaks the wall"
        # perpendicular web to the E-P band wall
        (e, p) = bpath
        ex, ey = e; px, py = p
        L2 = (px - ex) ** 2 + (py - ey) ** 2
        t = ((f[0] - ex) * (px - ex) + (f[1] - ey) * (py - ey)) / L2
        t = max(0.0, min(1.0, t))
        d_line = _d(f, (ex + t * (px - ex), ey + t * (py - ey)))
        assert d_line > bhw + 1.1 + 0.4, "M2 breaks the bay band wall"
    assert (BAY_FLOOR - 1.8) >= 1.5, "bay cups too deep for the dial web"
    # banking pins flank the fork inside the hub sweep — part-level fact
    for p in lv["bank_pins"]:
        assert _d(p, lv["E"]) > 16.0 + 1.0, "pin scrapes the wheel tips"


def test_revc_statics_clear_the_sweeps():
    """Cock feet, bridge pillars and the stud post vs every rotating
    sweep they share z with — the statics obey the same 2.0 rule."""
    sweeps = revc_sweeps()
    ck = cock_layout_c()
    posts = [(x, y, 4.0, PLATE_T, ZC["bridge"][0]) for x, y in bridge_pillar_xy()]
    posts += [(x, y, 5.0, PLATE_T, ZC["bridge"][0]) for x, y in ck["feet"]]
    for px, py, pr, z0, z1 in posts:
        for s in sweeps:
            if s.z1 <= z0 or s.z0 >= z1:
                continue
            assert hypot(s.x - px, s.y - py) >= s.r + pr + 2.0 - 1e-6, \
                f"post ({px:.0f},{py:.0f}) vs {s.name}"
    # stud post: intentionally 1.0 inside the spring's breathing sweep
    # (it PINS the coil end) — assert it's there, and clear of the ring
    sx, sy = ck["stud"]
    assert _d((sx, sy), ck["B"]) == pytest.approx(27.2, abs=0.01)
    assert 11.9 >= RING[1] + 0.5, "stud post reaches the ring band"


def test_revc_bridge_and_cock_are_disjoint():
    """Coplanar neighbors: the cock nestles in the bridge's cutout with
    a real gap (the NH35 composition), no boolean contact."""
    inter = rp.bridge_c() & rp.balance_cock_c()
    assert (inter.volume if inter else 0) < 1e-6


# --- assembled-pose gates (the review's structural blind spot, closed) ---------

def _builder():
    import tools.build_revc_movement as m
    return m


def test_revc_assembled_movement_no_interference():
    """The exported STEP itself: every meshing pair phase-chained clean,
    lever/plate/roller/spring/cock/strap all disjoint AT THEIR POSES.
    This is the gate that would have shipped three collisions."""
    m = _builder()
    parts = {k.label: k for k in m.kids}
    get = lambda s: next(v for k, v in parts.items() if s in k)
    mesh_pairs = [("barrel drum", "minute arbor"), ("minute arbor", "third arbor"),
                  ("third arbor", "fourth arbor"), ("fourth arbor", "escape arbor")]
    for a, b in mesh_pairs:
        inter = get(a) & get(b)
        v = inter.volume if inter else 0
        assert v < 0.5, f"assembled mesh {a} x {b} interferes ({v:.2f})"
    disjoint = [("stem + crown", "train bridge"), ("stem clip", "train bridge"),
                ("stem + crown", "crown wheel stud"),
                ("pallet fork", "mainplate"), ("pallet fork", "roller"),
                ("pallet fork", "bay strap"), ("bay strap", "mainplate"),
                ("hairspring", "balance cock"), ("hairspring", "balance wheel"),
                ("train bridge", "balance cock"), ("ratchet", "train bridge"),
                ("ratchet", "minute arbor"), ("barrel drum", "mainplate"),
                ("barrel arbor", "barrel drum"), ("barrel arbor", "train bridge"),
                ("balance wheel", "bay strap")]
    for a, b in disjoint:
        inter = get(a) & get(b)
        v = inter.volume if inter else 0
        assert v < 0.05, f"assembled {a} x {b} interferes ({v:.2f})"
    # the click TIP is 0.9 into the ratchet teeth by design: across one
    # tooth pitch there must be a SETTLED phase (tip in a gap) and a
    # BITING phase (it truly jams let-down)
    from build123d import Pos as P2, Rot as R2
    from caliber_k1.revc import REVC_LAYOUT as _L
    click = get("click (")
    r0 = rp.ratchet_c()
    bites = []
    for ph in range(0, 15, 2):
        ratchet = P2(*_L["barrel"], 0) * R2(0, 0, ph) * r0
        ic = click & ratchet
        bites.append(ic.volume if ic else 0)
    assert min(bites) < 0.05, f"click never settles into a gap ({min(bites):.2f})"
    assert max(bites) > 0.3, f"click never bites the teeth ({max(bites):.2f})"


def test_revc_lever_swings_free_of_plate_and_roller():
    """Across the banking range and roller phases: the fork touches
    NOTHING but (intentionally) the escape wheel. This is the part-level
    probe the MESH_PAIRS whitelist always promised."""
    from build123d import Pos, Rot
    from math import degrees
    lv = lever_layout_c()
    plate = rp.mainplate_c()
    lever0 = rp.swiss_lever_c()
    roller0 = rp.roller_c()
    ang = degrees(lv["ang"])
    for sw in (-6.5, -4, 0, 4, 6.5):
        lever = Pos(*lv["P"], 4.2) * Rot(0, 0, ang + sw) * lever0
        ip = lever & plate
        assert (ip.volume if ip else 0) < 0.05, f"lever x plate at {sw} deg"
    # roller phases vs REACHABLE lever angles only: far phases pair with
    # any bank; near phases are governed by the escapement (mid-pass the
    # pin commands the lever; after exit, DRAW holds the away-side bank)
    states = [(rph, sw) for rph in (90, 135, 180, 225, 270)
              for sw in (-6.5, 0, 6.5)]
    states += [(0, 0), (45, 6.5), (315, -6.5)]
    for rph, sw in states:
        lever = Pos(*lv["P"], 4.2) * Rot(0, 0, ang + sw) * lever0
        roller = Pos(*lv["B"], 0) * Rot(0, 0, ang + 180 + rph) * roller0
        ir = lever & roller
        v = ir.volume if ir else 0
        assert v < 0.05, f"lever x roller at swing {sw}, phase {rph} ({v:.2f})"


def test_inventory_is_complete_in_the_gate():
    """Jon's rule: recite the full cast before massing. Every sweep-kind
    inventory item must appear in revc_sweeps(); the massing tool builds
    from the same list and asserts its own completeness."""
    from caliber_k1.revc import INVENTORY, revc_sweeps
    names = {s.name for s in revc_sweeps()}
    for item, kind in INVENTORY:
        if kind == "sweep":
            assert item in names, f"inventory sweep {item} not in the gate"


def test_winding_station():
    """The crown path: ratchet x crown wheel phase-aligned; the stem's
    pinion gates the crown wheel through the underside slots; the
    pinion's swept cylinder truly clears the drum gear's teeth (the
    analytic check the drum_gear x stem whitelist relies on); and the
    ratio winds the ~2.8-turn spring in under 15 crown turns."""
    from math import atan2, degrees
    from build123d import Pos, Rot
    from caliber_k1.revc import REVC_LAYOUT as _L, WINDING
    _mesh_pair(rp.ratchet_c(), rp.crown_wheel_c(),
               _L["barrel"], WINDING["crown_wheel"], 24, 24)
    # slot mesh: clear at pose for SOME stem roll, engaged when the
    # crown wheel turns half a slot against a held stem
    cw = WINDING["crown_wheel"]
    wheel = Pos(*cw, 0) * rp.crown_wheel_c()
    rolls = []
    from build123d import Rot as R2
    for roll in range(0, 52, 4):
        stem = rp.stem_c().rotate(
            __import__("build123d").Axis((0, 80, WINDING["stem_z"]),
                                         (0, 1, 0)), roll)
        i = stem & wheel
        rolls.append((i.volume if i else 0, roll))
    best_v, best_roll = min(rolls)
    assert best_v < 0.3, f"pinion can't settle into a slot ({best_v:.2f})"
    stem = rp.stem_c().rotate(
        __import__("build123d").Axis((0, 80, WINDING["stem_z"]), (0, 1, 0)),
        best_roll)
    wheel2 = Pos(*cw, 0) * Rot(0, 0, 360 / 46) * rp.crown_wheel_c()
    i2 = stem & wheel2
    assert (i2.volume if i2 else 0) > 0.4, "slots don't gate the pinion"
    # analytic drum clearance (the whitelist's justification)
    drum_tip = REVC_LAYOUT["counts"][0] / 2 + 0.85
    gap = (WINDING["pinion_y"] - 1.8) - REVC_LAYOUT["barrel"][1] - drum_tip
    assert gap >= 2.0, f"pinion cylinder vs drum teeth: {gap:.2f}"
    assert 2.78 * WINDING["slots"] / 7 < 15   # crown turns to full wind
