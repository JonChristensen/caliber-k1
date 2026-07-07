"""Caliber K1 — Milestone 4 parts: upper-deck motion works + dial.

Storeys per M4_LEVELS; XY per m4_layout(). v0.1 has no keyless works:
set time by moving the hands with the drum locked (friction cannon in v2).
"""
from build123d import Align, Circle, Cylinder, Pos, Rectangle, extrude
from calibers.k1 import gears
from calibers.k1.decor import _ccw_polygon, _polyline_band
from calibers.k1.parameters import BAL, M4_LEVELS as LV, MOTION, TOL, m4_layout, STAND

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def _stack(sections):
    part, z = None, 0.0
    for spec, h in sections:
        layer = Pos(0, 0, z) * (Cylinder(float(spec), h, align=BOTTOM)
                                if isinstance(spec, (int, float)) else extrude(spec, h))
        part = layer if part is None else part + layer
        z += h
    return part


def r1_arbor():
    """Ground 24t wheel -> tall climb -> 10-leaf pinion on the deck."""
    return _stack([
        (1.5, 4.0),                                    # plate bushing pivot
        (2.5, 10.5),
        (gears.wheel_face(MOTION.r1_wheel, 16), 5.0),  # z10.5-15.5
        (2.5, LV["mesh1_z"] - 15.5),                   # the climb
        (gears.pinion_face(MOTION.r1_pinion), 5.0),    # z30.5-35.5
        (2.5, LV["dial_cock_z"] - (LV["mesh1_z"] + 5.0)),
        (1.5, LV["dial_cock_t"]),                      # dial-cock pivot
    ])


def r2_arbor():
    return _stack([
        (1.5, 1.5),                                    # deck-plate seat
        (2.5, LV["mesh1_z"] - (LV["deck_plate_z"] + LV["deck_plate_t"])),
        (gears.wheel_face(MOTION.r2_wheel, MOTION.r1_pinion), 5.0),
        (2.5, 0.5),
        (gears.pinion_face(MOTION.r2_pinion), 5.0),    # z36-41
        (2.5, LV["dial_cock_z"] - (LV["mesh2_z"] + 5.0)),
        (1.5, LV["dial_cock_t"]),
    ])


def t_arbor():
    """Dial center: 30t wheel + 12t cannon + tube to the minute hand."""
    part = _stack([
        (1.5, 1.5),
        (2.5, LV["mesh2_z"] - (LV["deck_plate_z"] + LV["deck_plate_t"])),
        (gears.wheel_face(MOTION.t_wheel, MOTION.r2_pinion), 5.0),
        (gears.pinion_face(MOTION.cannon), 5.0),       # cannon z41.5-46.5
        (3.0, LV["hands_z"] - (LV["mesh3_z"] + 5.0)),  # tube through cock
    ])
    flat = Pos(2.2 + 15, 0, 0) * extrude(Rectangle(30, 30), 200)
    return part - Pos(0, 0, LV["hands_z"] - LV["deck_plate_z"] - 3.0) * flat


def m_arbor():
    return _stack([
        (1.5, 1.5),
        (2.5, LV["mesh3_z"] - (LV["deck_plate_z"] + LV["deck_plate_t"])),
        (gears.wheel_face(MOTION.m_wheel, MOTION.cannon), 5.0),
        (gears.pinion_face(MOTION.m_pinion), 5.0),     # z47-52
        (1.5, LV["dial_cock_z"] - (LV["mesh4_z"] + 5.0) + LV["dial_cock_t"]),
    ])


def hour_wheel():
    """40t, rides loose on the T tube; hour hand mounts on its pipe."""
    face = gears.wheel_face(MOTION.hour_wheel, MOTION.m_pinion)
    face -= Circle(3.0 + TOL.pivot_clearance)
    part = extrude(face, 5.0)
    pipe = Circle(4.5) - Circle(3.0 + TOL.pivot_clearance)
    return part + Pos(0, 0, 5.0) * extrude(pipe, 3.0)


def deck_plate():
    m = m4_layout()
    path = [m["deck_pillar_a"], m["M"], m["T"], m["R2"], m["deck_pillar_b"]]
    face = _ccw_polygon(_polyline_band(path, 5.0))
    part = extrude(face, LV["deck_plate_t"])
    for k in ("R2", "T", "M"):
        part -= Pos(m[k][0], m[k][1], LV["deck_plate_t"] - 1.5) * \
            Cylinder(1.5 + TOL.pivot_clearance, 3, align=BOTTOM)
    for k in ("deck_pillar_a", "deck_pillar_b"):
        part -= Pos(*m[k]) * Cylinder(1.6 + TOL.snug_clearance, 20)
    return part


def dial_cock():
    m = m4_layout()
    path = [m["deck_pillar_a"], m["M"], m["T"], m["R2"], m["R1"],
            m["deck_pillar_b"]]
    face = _ccw_polygon(_polyline_band(path, 5.0))
    face += Pos(*m["T"]) * Circle(9.0)
    part = extrude(face, LV["dial_cock_t"])
    for k in ("R1", "R2", "M"):
        part -= Pos(m[k][0], m[k][1], 0) * Cylinder(
            1.5 + TOL.pivot_clearance, LV["dial_cock_t"] - 1.0, align=BOTTOM)
    # T hole passes the hour wheel's Ø9 pipe, which journals in the cock
    # (bug caught in M5 design review: was sized for the cannon tube only)
    part -= Pos(*m["T"]) * Cylinder(4.5 + TOL.pivot_clearance, 20)
    for k in ("deck_pillar_a", "deck_pillar_b"):
        part -= Pos(*m[k]) * Cylinder(1.6 + TOL.snug_clearance, 20)
    return part


def winding_knob():
    """Low-profile knob replacing the T-handle key (sweep r<=22)."""
    from calibers.k1.parameters import ARBOR
    sq = ARBOR.square_side + 2 * TOL.snug_clearance
    part = Cylinder(22, 9, align=BOTTOM)
    for k in range(24):
        from math import cos, pi, sin
        a = 2 * pi * k / 24
        part -= Pos(23.5 * cos(a), 23.5 * sin(a), 0) * Cylinder(2.2, 30)
    part -= extrude(Rectangle(sq, sq), 6.5)
    return part


def minute_hand():
    face = _ccw_polygon([(-4, -2.2), (26, -0.7), (26, 0.7), (-4, 2.2)])
    face += Circle(4.5)
    bore = Circle(3.0 + TOL.drive_clearance) - \
        Pos(2.2 + TOL.drive_clearance + 15, 0) * Rectangle(30, 30)
    return extrude(face - bore, 2.0)


def hour_hand():
    face = _ccw_polygon([(-4, -2.6), (17, -1.0), (17, 1.0), (-4, 2.6)])
    face += Circle(6.0)
    return extrude(face - Circle(4.5 + TOL.drive_clearance), 2.0)
