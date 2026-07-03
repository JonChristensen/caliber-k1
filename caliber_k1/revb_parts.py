"""Caliber K1 rev B — real parts on the frozen flat layout (log 0009).

Heights (rel mainplate top, z=0): P0 gears 0.5-5.5 | P1 gears 6.5-11.5 |
escape wheel 12.5-15.5 | bridges ~17-21 | balance 18.5-23.5 over the
wave bridge. Mainplate is 4mm; everything indexes off its top face.
"""
from build123d import Align, Circle, Cylinder, Pos, extrude
from .parameters import ARBOR, TOL
from .revb import revb_layout, TRAINS

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def mainplate():
    """Ø170 x 4. Blind bushings for every lower pivot (no through-holes:
    the dial side stays clean — the watch way)."""
    m = revb_layout()
    part = Cylinder(85, 4, align=BOTTOM)
    # barrel arbor: Ø8 pivot (reuses the proven M1 arbor), blind 3 deep
    bx, by = m["barrel"]
    part -= Pos(bx, by, 1.0) * Cylinder(
        ARBOR.pivot_d / 2 + TOL.pivot_clearance, 5, align=BOTTOM)
    # train lower pivots Ø3, blind 3 deep
    for k in ("center", "third", "fourth", "escape"):
        x, y = m[k]
        part -= Pos(x, y, 1.0) * Cylinder(1.5 + TOL.pivot_clearance, 5,
                                          align=BOTTOM)
    # balance staff lower pivot Ø2.5
    x, y = m["balance"]
    part -= Pos(x, y, 1.0) * Cylinder(1.25 + TOL.pivot_clearance, 5,
                                      align=BOTTOM)
    # three mounting feet holes at the rim (M3, for the display stand)
    from math import cos, sin, radians
    for az in (30, 150, 270):
        part -= Pos(78 * cos(radians(az)), 78 * sin(radians(az)), 0) * \
            Cylinder(1.7, 12)
    return part
