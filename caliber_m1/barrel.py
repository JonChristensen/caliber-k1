"""Caliber M1 — Milestone 1: going barrel group.

Parts: drum, cover, arbor, mainspring, ratchet wheel, click, winding key,
drum-lock pin. All geometry derives from parameters.py.

Conventions:
- Each part is modeled in its own local frame, sitting on z=0 where that is
  the natural print orientation (flat face down on the plate).
- Rotation sense: viewed from above (dial side), WINDING IS CLOCKWISE.
  The mainspring spiral opens counterclockwise outward, so turning the
  arbor clockwise pulls coils tighter onto the hub. The ratchet therefore
  permits CW and the click blocks CCW return.
"""

from math import cos, sin, pi, tau

from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Compound,
    Cylinder,
    Polygon,
    Pos,
    Rectangle,
    RegularPolygon,
    Rot,
    extrude,
)

from .parameters import ARBOR, BARREL, RATCHET, SPRING, STAND, TOL

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


# ---------------------------------------------------------------------------
# Drum
# ---------------------------------------------------------------------------

def drum():
    b = BARREL
    body_h = b.floor_t + b.inner_h
    outer_r = b.drum_outer_d / 2
    inner_r = b.inner_d / 2

    part = Cylinder(outer_r, body_h, align=BOTTOM)
    # hollow out the spring chamber
    part -= Pos(0, 0, b.floor_t) * Cylinder(inner_r, b.inner_h + 1, align=BOTTOM)
    # floor bore rides the arbor's lower journal (hub_d is inside the chamber)
    journal_r = ARBOR.pivot_d / 2 + 1.0  # journal = pivot + 2mm shoulder
    part -= Cylinder(journal_r + TOL.pivot_clearance, b.floor_t * 3)
    # through-wall slot for the mainspring outer tab (at angle 0 = +X)
    slot = Pos((inner_r + outer_r) / 2 + 1, 0, b.floor_t) * Box(
        b.wall_t + 4, b.spring_slot_w, b.spring_slot_h, align=BOTTOM
    )
    part -= slot
    # two notches in the wall top rim: the cover's tabs key into these so
    # the lock pin (through cover) locks the whole drum
    for ang in (90, 270):
        notch = Rot(0, 0, ang) * (
            Pos((inner_r + outer_r) / 2, 0, body_h - 2.2)
            * Box(b.wall_t + 2, 4.4, 3, align=BOTTOM)
        )
        part -= notch
    return part


# ---------------------------------------------------------------------------
# Cover — with viewing windows so the spring is visible (and filmable)
# ---------------------------------------------------------------------------

def _sector(r_out: float, a0: float, a1: float, n: int = 24):
    """Filled pie-sector polygon from angle a0 to a1 (degrees)."""
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = (a0 + (a1 - a0) * i / n) * pi / 180
        pts.append((r_out * cos(a), r_out * sin(a)))
    return Polygon(*pts, align=None)


def cover():
    b = BARREL
    outer_r = b.drum_outer_d / 2
    journal_r = ARBOR.pivot_d / 2 + 1.0

    face = Circle(outer_r)
    # pointer tab: extends past the rim so drum rotation reads from above.
    # Kept under r=37.5 so it clears the stand pillars (at r=43, Ø10 → r38).
    face += Polygon((outer_r - 2, -3), (outer_r - 2, 3), (37.5, 0), align=None)
    # three annular viewing windows, r15..23.5, leaving 3 spokes
    ring = Circle(23.5) - Circle(15.0)
    for ang in (30, 150, 270):
        face -= ring & _sector(30.0, ang - 47, ang + 47)
    part = extrude(face, b.cover_t)
    # center bore rides the arbor's upper journal
    part -= Cylinder(journal_r + TOL.pivot_clearance, b.cover_t * 3)
    # lock-pin hole at r=30 (solid land between windows and rim)
    part -= Pos(0, 30, 0) * Cylinder(b.lock_pin_hole_d / 2 + 0.1, b.cover_t * 3)
    # keying tabs on the underside: engage the drum wall notches at 90/270
    inner_r = b.inner_d / 2
    for ang in (90, 270):
        tab = Rot(0, 0, ang) * (
            Pos((inner_r + outer_r) / 2, 0, -2)
            * Box(b.wall_t + 1, 4.0, 2, align=BOTTOM)
        )
        part += tab
    return part


# ---------------------------------------------------------------------------
# Arbor
# ---------------------------------------------------------------------------

def arbor():
    a = ARBOR
    b = BARREL
    journal_r = a.pivot_d / 2 + 1.0
    # section lengths, bottom to top. The spring's breathing room
    # (inner_h - spring height) splits evenly above and below the hub.
    breathing = (b.inner_h - SPRING.height) / 2
    lower_pivot = a.pivot_len
    lower_journal = b.floor_t + breathing
    hub = SPRING.height
    upper_journal = breathing + b.cover_t + TOL.endshake
    upper_pivot = a.pivot_len
    square = a.square_len

    z = 0.0
    part = Cylinder(a.pivot_d / 2, lower_pivot, align=BOTTOM)
    z += lower_pivot
    part += Pos(0, 0, z) * Cylinder(journal_r, lower_journal, align=BOTTOM)
    z += lower_journal
    # hub with D-flat: drives the mainspring's inner ring
    hub_cyl = Pos(0, 0, z) * Cylinder(a.hub_d / 2, hub, align=BOTTOM)
    flat_x = a.hub_d / 2 - a.hub_flat_depth
    hub_cyl -= Pos(flat_x + 15, 0, z) * Box(30, 30, hub + 2, align=BOTTOM)
    part += hub_cyl
    z += hub
    part += Pos(0, 0, z) * Cylinder(journal_r, upper_journal, align=BOTTOM)
    z += upper_journal
    part += Pos(0, 0, z) * Cylinder(a.pivot_d / 2, upper_pivot, align=BOTTOM)
    z += upper_pivot
    part += Pos(0, 0, z) * Box(a.square_side, a.square_side, square, align=BOTTOM)
    return part


def arbor_total_length() -> float:
    a, b = ARBOR, BARREL
    breathing = (b.inner_h - SPRING.height) / 2
    return (
        a.pivot_len
        + (b.floor_t + breathing)
        + SPRING.height
        + (breathing + b.cover_t + TOL.endshake)
        + a.pivot_len
        + a.square_len
    )


# ---------------------------------------------------------------------------
# Mainspring — printed PETG spiral with D-ring inner end, tab outer end
# ---------------------------------------------------------------------------

def mainspring():
    s = SPRING
    ring_bore_r = ARBOR.hub_d / 2 + TOL.drive_clearance
    ring_outer_r = ring_bore_r + 2.0
    r_start = ring_outer_r - 0.5          # weld the spiral root into the ring
    r_end = BARREL.inner_d / 2 - 2.5      # relaxed outer coil near the wall
    theta_end = s.coils * tau
    b_coef = (r_end - r_start) / theta_end
    half_t = s.thickness / 2

    n = s.coils * 48
    outer_pts = []
    inner_pts = []
    for i in range(n + 1):
        th = theta_end * i / n
        r = r_start + b_coef * th
        outer_pts.append(((r + half_t) * cos(th), (r + half_t) * sin(th)))
        inner_pts.append(((r - half_t) * cos(th), (r - half_t) * sin(th)))
    face = Polygon(*(outer_pts + inner_pts[::-1]), align=None)

    # inner ring with D-bore matching the arbor hub flat
    flat_x = ARBOR.hub_d / 2 - ARBOR.hub_flat_depth + TOL.drive_clearance
    d_hole = Circle(ring_bore_r) - Pos(flat_x + 15, 0) * Rectangle(30, 30)
    face += Circle(ring_outer_r) - d_hole

    # outer tab: radial, pokes through the drum wall slot (at spiral end angle 0)
    tab_r0 = r_end - 0.8
    tab_r1 = BARREL.inner_d / 2 + 2.5     # engages 2.5mm into the 3mm wall slot
    face += Pos((tab_r0 + tab_r1) / 2, 0) * Rectangle(tab_r1 - tab_r0, s.outer_tab_w)

    return extrude(face, s.height)


def spring_strip_length() -> float:
    """Arc length of the printed spiral (for the README / material estimate)."""
    s = SPRING
    ring_outer_r = ARBOR.hub_d / 2 + TOL.drive_clearance + 2.0
    r_start = ring_outer_r - 0.5
    r_end = BARREL.inner_d / 2 - 2.5
    theta_end = s.coils * tau
    # mean radius * total angle is accurate to <1% for gentle spirals
    return (r_start + r_end) / 2 * theta_end


# ---------------------------------------------------------------------------
# Ratchet wheel + click (flexure pawl)
# ---------------------------------------------------------------------------

def ratchet_wheel():
    r = RATCHET
    tip_r = r.wheel_d / 2
    root_r = tip_r - r.tooth_depth
    step = 360 / r.tooth_count
    pts = []
    for i in range(r.tooth_count):
        a0 = i * step
        a1 = a0 + step * 0.93
        pts.append((root_r * cos(a0 * pi / 180), root_r * sin(a0 * pi / 180)))
        pts.append((tip_r * cos(a1 * pi / 180), tip_r * sin(a1 * pi / 180)))
    face = Polygon(*pts, align=None)
    part = extrude(face, r.wheel_t)
    # square bore over the arbor winding square
    sq = ARBOR.square_side + 2 * TOL.drive_clearance
    part -= Box(sq, sq, r.wheel_t * 3)
    return part


def click():
    """Flexure click, modeled in the ratchet wheel's frame (wheel at origin).

    Mount block at x≈26..34 with two Ø4 pegs + one M3 into the top plate;
    a ~2mm-thick arm reaches tangentially to a wedge tip engaging the teeth.
    Rides the ramps on CW (wind), butts the radial faces on CCW (blocked).
    """
    r = RATCHET
    face = Polygon(
        (26, -2), (34, -2), (34, 8), (26, 8),      # mount block
        (26, 6.5), (6.2, 20.8),                    # arm outer edge
        (4.4, 18.1),                               # wedge tip (r ≈ 18.6)
        (7.0, 18.6), (26, 4.5),                    # arm inner edge
        align=None,
    )
    part = extrude(face, r.click_t)
    # M3 through-hole with counterbore for a socket head
    part -= Pos(30, 3, 0) * Cylinder(1.7, r.click_t * 3)
    part -= Pos(30, 3, r.click_t - 3.2) * Cylinder(3.1, 5, align=BOTTOM)
    # two anti-rotation pegs on the underside
    for y in (0, 6):
        part += Pos(30, y, -3.8) * Cylinder(2.0, 3.8, align=BOTTOM)
    return part


CLICK_M3_XY = (30, 3)
CLICK_PEG_XY = ((30, 0), (30, 6))


# ---------------------------------------------------------------------------
# Winding key + drum-lock pin
# ---------------------------------------------------------------------------

def winding_key():
    sq = ARBOR.square_side + 2 * TOL.snug_clearance
    shaft = Cylinder(8, 22, align=BOTTOM)
    shaft -= Box(sq, sq, 9, align=BOTTOM)  # socket at the bottom
    handle = Pos(0, 0, 22) * Rot(90, 0, 0) * Cylinder(6, 80)
    return shaft + handle


def lock_pin():
    b = BARREL
    shaft_len = STAND.plate_t + TOL.endshake + b.cover_t + 1.5
    part = Cylinder(b.lock_pin_hole_d / 2 - 0.1, shaft_len, align=BOTTOM)
    part += Pos(0, 0, shaft_len) * Cylinder(5.5, 3.5, align=BOTTOM)
    return part
