"""Caliber K1 — Milestone 2 parts: train wheels, wave bridge, rig plate.

The going train lives UNDER the Milestone 1 spider plate, on a new Ø150
rig plate that replaces the Ø100 bottom plate. The barrel cartridge,
pillars, spider, ratchet, click, key and pin are all reused unchanged.

Arbors are monolithic prints (pivot-pinion-wheel-pivot in one part),
running in printed bushings for rig v1; steel pivots are a parameter
change away when we chase runtime.
"""

from math import cos, pi, sin

from build123d import (
    Align, Box, Circle, Compound, Cylinder, Polygon, Pos, RegularPolygon,
    Rot, extrude,
)

from . import gears
from .decor import swirl_windows, wave_bridge_face
from .parameters import (
    ARBOR, BARREL, MOVEMENT_DIAMETER, STAND, TOL, TRAIN, TRAIN_LEVELS,
    train_layout,
)

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)
LV = TRAIN_LEVELS


def _arbor_stack(sections):
    """Stack (face_or_radius, height) sections bottom-up into one solid.
    A number means a plain cylinder of that radius; a face is extruded."""
    part = None
    z = 0.0
    for spec, h in sections:
        if isinstance(spec, (int, float)):
            layer = Pos(0, 0, z) * Cylinder(float(spec), h, align=BOTTOM)
        else:
            layer = Pos(0, 0, z) * extrude(spec, h)
        part = layer if part is None else part + layer
        z += h
    return part


def w1_arbor():
    """First train wheel: 16-leaf pinion (meshes drum) + 50t wheel.

    Arbor-local z0 = bottom pivot tip. Assembled, the pivot sits in the
    rig plate's 4mm-deep bushing, so local 4.0 = rig plate top = global 0.
    """
    t = TRAIN
    pivot_r = t.pivot_d / 2
    wheel = gears.wheel_face(t.w1_wheel, t.w4_pinion)
    root_r = t.module * t.w1_wheel / 2 - t.wheel_dedendum * t.module
    for w in swirl_windows(7.0, root_r - 2.5):
        wheel -= w
    pinion = gears.pinion_face(t.w1_pinion)

    sections = [
        (pivot_r, 4.0),                                   # plate bushing
        (3.5, LV["w1_pinion_z"]),                         # neck (0.5)
        (pinion, t.pinion_h),                             # 16-leaf pinion
        (4.0, LV["w1_wheel_z"] - LV["w1_pinion_z"] - t.pinion_h),  # spacer
        (wheel, t.wheel_h),                               # 50t wave wheel
        (3.5, LV["bridge_z"] - (LV["w1_wheel_z"] + t.wheel_h)),
        (pivot_r, 4.0),                                   # bridge bushing
    ]
    return _arbor_stack(sections)


def w4_arbor():
    """Seconds arbor: 12-leaf pinion (meshes W1 wheel) + 24t wheel.
    Rotates exactly once per 60 s."""
    t = TRAIN
    pivot_r = t.pivot_d / 2
    wheel = gears.wheel_face(t.w4_wheel, t.esc_pinion)
    pinion = gears.pinion_face(t.w4_pinion)
    sections = [
        (pivot_r, 4.0),
        (2.5, LV["w4_pinion_z"]),                         # lower shaft (6.0)
        (pinion, t.pinion_h),
        (2.5, LV["w4_wheel_z"] - LV["w4_pinion_z"] - t.pinion_h),
        (wheel, t.wheel_h),
        (2.5, LV["bridge_z"] - (LV["w4_wheel_z"] + t.wheel_h)),
        (pivot_r, 4.0),
    ]
    return _arbor_stack(sections)


def esc_arbor():
    """Escape-pinion arbor: terminates the train for the M2 spin test.
    Milestone 3 replaces this part with pinion + escape wheel."""
    t = TRAIN
    pivot_r = t.pivot_d / 2
    pinion = gears.pinion_face(t.esc_pinion)
    sections = [
        (pivot_r, 4.0),
        (2.5, LV["esc_pinion_z"]),                        # lower shaft (11.5)
        (pinion, t.pinion_h),
        (2.5, LV["bridge_z"] - (LV["esc_pinion_z"] + t.pinion_h)),
        (pivot_r, 4.0),
    ]
    return _arbor_stack(sections)


def wave_bridge():
    """The train bridge as a breaking wave (see decor.wave_bridge_face).

    Path runs foot_a -> W1 -> W4 -> esc -> foot_b, ordered so the wave's
    crest rises on the outboard side, away from the barrel.
    """
    lay = train_layout()
    path = [lay["foot_a"], lay["w1"], lay["w4"], lay["esc"], lay["foot_b"]]
    face = wave_bridge_face(path)
    # bosses guarantee full material around every bearing, since the
    # smoothed band deviates slightly from the raw pivot polyline
    for key in ("w1", "w4", "esc", "foot_a", "foot_b"):
        x, y = lay[key]
        face += Pos(x, y) * Circle(5.5)
    part = extrude(face, LV["bridge_t"])
    # pivot bushings for the three train arbors
    for key in ("w1", "w4", "esc"):
        x, y = lay[key]
        part -= Pos(x, y, 0) * Cylinder(
            TRAIN.pivot_d / 2 + TOL.pivot_clearance, LV["bridge_t"] * 3
        )
    # feet: seats over the rig plate's integral posts (Ø3.2 spigots)
    for key in ("foot_a", "foot_b"):
        x, y = lay[key]
        part -= Pos(x, y, 0) * Cylinder(1.6 + TOL.snug_clearance,
                                        LV["bridge_t"] * 3)
    return part


def rig_plate():
    """Ø150 lower plate: replaces the M1 bottom plate. Carries the barrel
    bushing, three pillar bolt positions (reused M1 pillars/spider), the
    three train bushings, and two integral wave-bridge posts."""
    s = STAND
    lay = train_layout()
    r = MOVEMENT_DIAMETER / 2
    part = Cylinder(r, s.plate_t, align=BOTTOM)
    # barrel arbor bushing (center, through)
    part -= Cylinder(ARBOR.pivot_d / 2 + TOL.pivot_clearance, s.plate_t * 3)
    # pillar bolts + nut pockets (3 legs — the M1 tripod, made honest)
    from .stand import _pillar_positions
    for x, y in _pillar_positions():
        part -= Pos(x, y, 0) * Cylinder(s.bolt_clear_d / 2, s.plate_t * 3)
        part -= Pos(x, y, 0) * extrude(
            RegularPolygon(s.nut_pocket_w / 3**0.5, 6), s.nut_pocket_t
        )
    # train arbor bushings: blind, 4 deep, floor left below
    for key in ("w1", "w4", "esc"):
        x, y = lay[key]
        part -= Pos(x, y, s.plate_t - 4.0) * Cylinder(
            TRAIN.pivot_d / 2 + TOL.pivot_clearance, 6, align=BOTTOM
        )
    # integral bridge posts with locating spigots
    for key in ("foot_a", "foot_b"):
        x, y = lay[key]
        part += Pos(x, y, s.plate_t) * Cylinder(4.0, LV["post_h"], align=BOTTOM)
        part += Pos(x, y, s.plate_t + LV["post_h"]) * Cylinder(
            1.6, LV["bridge_t"], align=BOTTOM
        )
    return part


def assembly_positions():
    """z of each M2 element above rig-plate bottom (plate top = plate_t).
    All three arbors share z0 = plate_t - 4 (pivot bottomed in its bushing)."""
    top = STAND.plate_t
    return {
        "arbor_z0": top - 4.0,
        "bridge_z": top + LV["bridge_z"],
    }
