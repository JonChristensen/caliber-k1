"""Caliber K1 — Milestone 1 test stand.

Two plates + four pillars, bolted with M3×40. The top plate is a 3-spoke
"spider" so the barrel drum and its pointer stay visible (and filmable).

The click mounts on one spoke; the drum-lock pin drops through another.
"""

from math import atan2, degrees

from build123d import (
    Align,
    Box,
    Circle,
    Cylinder,
    Polygon,
    Pos,
    RegularPolygon,
    Rot,
    extrude,
)
from math import cos, sin, pi

from calibers.k1.parameters import ARBOR, BARREL, RATCHET, STAND, TOL, pillar_height
from .barrel import CLICK_M3_XY, CLICK_PEG_XY, _sector

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

# Spoke layout: the click's mount block centroid sits at (30, 3) in the
# ratchet frame → angle ≈ 5.7°. One spoke is centered there; the other two
# every 120°. The lock pin lives on the second spoke at r=30.
CLICK_SPOKE_ANGLE = degrees(atan2(CLICK_M3_XY[1], CLICK_M3_XY[0]))
SPOKE_ANGLES = [CLICK_SPOKE_ANGLE, CLICK_SPOKE_ANGLE + 120, CLICK_SPOKE_ANGLE + 240]
SPOKE_HALF_WIDTH_DEG = 13
PIN_ANGLE = SPOKE_ANGLES[1]
PIN_R = 30.0


def _pillar_positions():
    """Three pillars, 120° apart — a tripod.

    History note: v1 generated four positions of which two coincided
    (5.7°+180° == 125.7°+60° == 185.7°), so printed plates only ever had
    three unique holes. Three points define a plane; the tripod is the
    honest design. Guarded by test_pillar_positions_distinct.
    """
    r = STAND.pillar_circle_d / 2
    return [
        (r * cos((a + 60) * pi / 180), r * sin((a + 60) * pi / 180))
        for a in SPOKE_ANGLES
    ]


def bottom_plate():
    s = STAND
    part = Cylinder(s.plate_d / 2, s.plate_t, align=BOTTOM)
    # center bushing: arbor lower pivot
    part -= Cylinder(ARBOR.pivot_d / 2 + TOL.pivot_clearance, s.plate_t * 3)
    for x, y in _pillar_positions():
        part -= Pos(x, y, 0) * Cylinder(s.bolt_clear_d / 2, s.plate_t * 3)
        # hex nut pocket on the underside
        part -= Pos(x, y, 0) * extrude(
            RegularPolygon(s.nut_pocket_w / 3**0.5, 6), s.nut_pocket_t
        )
    return part


def top_plate():
    s = STAND
    face = Circle(s.plate_d / 2)
    # three windows between the spokes, from r16 out to the rim ring at r40
    window = Circle(40.0) - Circle(16.0)
    for i in range(3):
        a0 = SPOKE_ANGLES[i] + SPOKE_HALF_WIDTH_DEG
        a1 = SPOKE_ANGLES[(i + 1) % 3] - SPOKE_HALF_WIDTH_DEG + (120 * 3 if i == 2 else 0)
        # normalize the wrap-around on the last gap
        if a1 <= a0:
            a1 += 360
        face -= window & _sector(55.0, a0, a1)
    part = extrude(face, s.plate_t)
    # center bushing: arbor upper pivot
    part -= Cylinder(ARBOR.pivot_d / 2 + TOL.pivot_clearance, s.plate_t * 3)
    # pillar bolt holes, counterbored for M3 socket heads
    for x, y in _pillar_positions():
        part -= Pos(x, y, 0) * Cylinder(s.bolt_clear_d / 2, s.plate_t * 3)
        part -= Pos(x, y, s.plate_t - 3.2) * Cylinder(3.1, 5, align=BOTTOM)
    # click mount: M3 clear hole + nut pocket underneath + two peg sockets
    mx, my = CLICK_M3_XY
    part -= Pos(mx, my, 0) * Cylinder(s.bolt_clear_d / 2, s.plate_t * 3)
    part -= Pos(mx, my, 0) * extrude(
        RegularPolygon(s.nut_pocket_w / 3**0.5, 6), s.nut_pocket_t
    )
    for px, py in CLICK_PEG_XY:
        part -= Pos(px, py, s.plate_t - 4.0) * Cylinder(
            2.0 + TOL.snug_clearance, 6, align=BOTTOM
        )
    # lock-pin hole
    part -= Pos(PIN_R * cos(PIN_ANGLE * pi / 180),
                PIN_R * sin(PIN_ANGLE * pi / 180), 0) * Cylinder(
        BARREL.lock_pin_hole_d / 2 + 0.15, s.plate_t * 3
    )
    return part


def pillar():
    s = STAND
    part = Cylinder(s.pillar_d / 2, pillar_height(), align=BOTTOM)
    part -= Cylinder(s.bolt_clear_d / 2, pillar_height() * 3)
    return part
