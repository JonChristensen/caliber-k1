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


def wave_bridge_b():
    """Rev B train bridge — THE wave, on top of the movement (z16-19).
    Spans third/fourth/escape upper pivots; the crest's tube lands on the
    balance center so the staff rises through the barrel of the wave.
    Feet: (56,14) barrel-side, (-30.77,-35.37) past the crest."""
    from math import cos, sin, radians, hypot
    from build123d import Pos as P_, Cylinder as Cyl
    from .decor import wave_bridge_face
    m = revb_layout()
    BAL = m["balance"]
    d = (cos(radians(200)), sin(radians(200)))       # crest travel direction
    n = (-d[1], d[0])
    pc = (BAL[0] - 9 * (d[0] + n[0]), BAL[1] - 9 * (d[1] + n[1]))
    k1 = (pc[0] - 14 * d[0], pc[1] - 14 * d[1])
    foot_b = (pc[0] + 30 * d[0], pc[1] + 30 * d[1])   # runway encloses the tube
    foot_a = (56.0, 14.0)
    path = [foot_a, m["third"], m["fourth"], m["escape"], k1, foot_b]
    # crest fraction = arc length to pc / total arc length
    pts = path[:4] + [pc, foot_b]
    seg = lambda a, b: hypot(b[0] - a[0], b[1] - a[1])
    arcs = [seg(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    f_c = sum(arcs[:4]) / sum(arcs)
    # wave_bridge_face evaluates the crest at (crest_at + 0.03): compensate
    face = wave_bridge_face(path, half_w=6.5, crest_at=f_c - 0.03)
    for f in (foot_a, foot_b):                    # end caps: feet get pads
        face += Pos(*f) * Circle(6.0)
    part = extrude(face, 3.0)
    for k in ("third", "fourth", "escape"):
        part -= P_(m[k][0], m[k][1], 0) * Cyl(1.5 + TOL.pivot_clearance, 10)
    for f in (foot_a, foot_b):
        part -= P_(f[0], f[1], 0) * Cyl(1.65, 10)
    return part


def broad_wave_bridge():
    """The NH35-style broad train+barrel bridge, v2 (log 0010): the wave
    IS the plate's outboard boundary. Three swells roll along the SE edge
    as bulges of the outline itself; the crest lobe straddles the balance
    well's SW rim, so cutting the well carves the curl into an open
    crescent — the balance emerges from the wave into calm water."""
    from build123d import Cylinder as Cyl, Pos as P_
    from math import cos, sin, radians
    from .decor import _ccw_polygon, _chaikin
    m = revb_layout()
    BAL = m["balance"]
    bx, by = m["barrel"]

    outline = [
        (-11, 95), (32, 82), (50, 30), (52, 2),
        (40, -24), (48, -34),          # swell 1
        (34, -46), (40, -58),          # swell 2
        (22, -64), (24, -76),          # swell 3 (building)
        (0, -78), (-24, -80),          # approach to the crest
        (-52, -70), (-64, -44),        # past the well, SW
        (-62, -12), (-56, 22), (-50, 52), (-36, 84),
    ]
    face = _ccw_polygon(_chaikin(outline))
    face += P_(bx, by) * Circle(43.0)                     # barrel plateau
    face += Circle(13.0)                                  # center pad
    for k in ("third", "fourth", "escape"):
        face += P_(*m[k]) * Circle(9.0)
    face += P_(*BAL) * Circle(32.0)                       # well surround
    # crest lobe straddling the well rim (SW): the well cut opens it
    ca = radians(215)
    face += P_(BAL[0] + 33 * cos(ca), BAL[1] + 33 * sin(ca)) * Circle(13.0)
    face -= P_(*BAL) * Circle(27.0)                       # the balance well
    part = extrude(face, 3.0)
    # train bosses to z16 (plate local z0 = 21) + open bearings
    for k in ("center", "third", "fourth", "escape"):
        x, y = m[k]
        part += P_(x, y, -5.0) * Cyl(4.0, 5.0,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        part -= P_(x, y, -6.0) * Cyl(1.5 + TOL.pivot_clearance, 12,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    part -= P_(bx, by, 0) * Cyl(ARBOR.pivot_d / 2 + TOL.pivot_clearance, 12)
    for f in ((44.0, 8.0), (14.0, 40.0), (-54.0, -20.0), (0.0, -70.0)):
        part -= P_(f[0], f[1], 0) * Cyl(1.7, 12)
    return part


def _ccw_band(path, half_w):
    from .decor import _ccw_polygon, _polyline_band
    return _ccw_polygon(_polyline_band(path, half_w))
