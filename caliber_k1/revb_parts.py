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
        (-11, 84), (30, 74), (50, 30), (52, 2),
        (40, -24), (48, -34),          # swell 1
        (34, -46), (40, -58),          # swell 2
        (22, -64), (24, -76),          # swell 3 (building)
        (0, -78), (-24, -80),          # approach to the crest
        (-52, -70), (-64, -44),        # past the well, SW
        (-62, -12), (-56, 22), (-48, 50), (-34, 74),
    ]
    face = _ccw_polygon(_chaikin(outline))
    face += P_(bx, by) * Circle(42.0)                     # barrel plateau (rim-flush)
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
    # 2d/A: flush recesses for ratchet + crown wheel (6498 style) — the
    # two pockets overlap where the teeth mesh, forming a figure-eight
    from .revb import keyless_layout_b
    kk = keyless_layout_b()
    for cx, cy in (m["barrel"], kk["crown_wheel"]):
        part -= P_(cx, cy, 2.0) * Cyl(14.5, 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    # 2d additions: stem tunnel block (bore now at z29.5 global = local 8.5)
    # and two click spigot holes near the ratchet
    from math import cos, sin, radians
    from build123d import Rot, Box
    az = radians(105)
    tx, ty = 79 * cos(az), 79 * sin(az)
    part += P_(tx, ty, 3.0) * Rot(0, 0, 105) * Box(
        10, 12, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part -= P_(tx, ty, 8.5) * Rot(0, 90, 0) * Rot(0, 0, 105) * Cyl(2.2, 30)
    from .revb import click_peg_points_global
    for px, py in click_peg_points_global():
        part -= P_(px, py, 1.0) * Cyl(1.65, 4,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part


def _ccw_band(path, half_w):
    from .decor import _ccw_polygon, _polyline_band
    return _ccw_polygon(_polyline_band(path, half_w))


def pallet_cock():
    """Small finger bridge under the balance ring: holds the pallet
    arbor's upper bearing at z16.5-18. Feet = Ø3.15 spigots into the
    mainplate (glue/press), tucked below the ring with 0.5 air."""
    from build123d import Cylinder as Cyl, Pos as P_
    from .revb import escapement_layout_b, ZB
    e = escapement_layout_b()
    face = _ccw_band([e["pallet_feet"][0], e["P"], e["pallet_feet"][1]], 4.0)
    part = extrude(face, ZB["pallet_cock"][1] - ZB["pallet_cock"][0])
    part -= P_(e["P"][0], e["P"][1], 0) * Cyl(1.5 + TOL.pivot_clearance, 8)
    for f in e["pallet_feet"]:
        part += P_(f[0], f[1], -16.5 + 1.0) * Cyl(
            1.55, 15.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part


def balance_cock_b():
    """Spans the well from the calm-water (NE) side: two feet on the
    broad bridge top (z24), riser to the arm at z29-32, bearing boss
    over the staff with the 4mm red cabochon pocket — the jewel, at
    last, exactly where the first sketch promised."""
    from build123d import Cylinder as Cyl, Pos as P_
    from math import cos, sin, radians
    from .revb import revb_layout, ZB
    B = revb_layout()["balance"]
    a1, a2 = radians(35), radians(80)
    feet = [(B[0] + 33 * cos(a1), B[1] + 33 * sin(a1)),
            (B[0] + 33 * cos(a2), B[1] + 33 * sin(a2))]
    face = _ccw_band([feet[0], B, feet[1]], 5.5)
    face += P_(*B) * Circle(7.0)
    part = extrude(face, 3.0)                      # arm plate (local z0=29)
    for f in feet:                                 # risers down to bridge top
        part += P_(f[0], f[1], -5.0) * Cyl(5.0, 5.0,
                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
        part -= P_(f[0], f[1], -6.0) * Cyl(1.7, 12,
                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
    part -= P_(B[0], B[1], -1) * Cyl(1.25 + TOL.pivot_clearance, 2.5,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    part -= P_(B[0], B[1], 1.5) * Cyl(2.1, 5,
                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part


def ratchet_b():
    """24t wheel on the barrel square above the bridge (z24.5-28):
    winds via the crown wheel, holds via the click."""
    from . import gears
    face = gears.wheel_face(24, 24)
    part = extrude(face, 3.5)
    sq = ARBOR.square_side + 2 * TOL.snug_clearance
    from build123d import Rectangle, Pos as P_
    from .decor import swirl_windows
    for w in swirl_windows(4.5, 9.5, spokes=5, spoke_w=1.8):
        part -= P_(0, 0, 3.0) * extrude(w, 0.6)
    part -= extrude(Rectangle(sq, sq), 10)
    return part


def crown_wheel_b():
    """Spur 24t rim (meshes the ratchet) + 20 face slots on top (meshed
    by the stem pinion): the printable axis-turner. Rides a Ø4 stud."""
    from math import cos, sin, pi
    from build123d import Box, Rot, Cylinder as Cyl, Pos as P_
    from . import gears
    part = extrude(gears.wheel_face(24, 24), 3.5)
    for k in range(20):
        a = 360 * k / 20
        part -= Rot(0, 0, a) * P_(10.0, 0, 1.0) * Box(
            4.0, 1.6, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    from .decor import swirl_windows
    for w in swirl_windows(4.0, 7.5, spokes=5, spoke_w=1.6):
        part -= P_(0, 0, 3.0) * extrude(w, 0.6)
    part -= Cyl(2.0 + TOL.pivot_clearance, 12)
    return part


def stem_crown():
    """Crown, stem, and 10t pinion — one print, axis along +X (local);
    the export rotates it to az105. Pinion teeth dip into the crown
    wheel's face slots."""
    from build123d import Rot, Cylinder as Cyl, Pos as P_
    from . import gears
    part = Rot(0, 90, 0) * Cyl(7.0, 6.0)               # crown knob at x~0
    for k in range(18):                                 # grip flutes
        a = 360 * k / 18
        part -= Rot(a, 0, 0) * P_(0, 7.2, 0) * Rot(0, 90, 0) * Cyl(1.2, 8)
    part += P_(3, 0, 0) * Rot(0, 90, 0) * Cyl(2.0, 4, align=(
        Align.CENTER, Align.CENTER, Align.MIN))         # shaft x3..7
    pin = extrude(gears.pinion_face(10), 4.0)           # 10t, module 1
    part += P_(7, 0, 0) * Rot(0, 90, 0) * pin           # pinion x7..11:
    part += P_(11, 0, 0) * Rot(0, 90, 0) * Cyl(1.0, 2.5, align=(
        Align.CENTER, Align.CENTER, Align.MIN))         # over the slot ring
    return part


def click_b():
    """Flexure click in the RATCHET frame (revb.click_geometry_b): M1's
    proven jamming layout scaled to the 24t wheel. The export rotates it
    -30 deg about the ratchet center; pegs match the bridge's holes via
    the shared geometry function. PETG."""
    from build123d import Cylinder as Cyl, Pos as P_
    from .revb import click_geometry_b
    from .decor import _ccw_polygon
    g = click_geometry_b()
    part = extrude(_ccw_polygon(g["outline"]), 2.8)
    for x, y in g["pegs"]:
        part += P_(x, y, -3.2) * Cyl(1.55, 3.2,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part
