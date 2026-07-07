"""Rev C dial-side parts on the frozen DIAL_LAYOUT. Everything pockets
into the plate's dial face (log 0013); only pipes, hands and the moon
window's platform stand proud. Bands and the axis theorem (hour pipe
SHORT, cannon gears above it) are law — see revc_dial's docstring.

Register parts (metal-worthy even in print): the Ø3 center post and the
five Ø2 arbor posts — plain pins, pressed into the plate.
"""
from math import cos, sin, pi, radians, hypot

from build123d import Align, Axis, Circle, Cylinder, Pos, Rectangle, extrude

from . import gears
from .variants import active_variant
from .revc import REVC_LAYOUT
from .revc_dial import DIAL_BANDS, DIAL_LAYOUT, DIAL_TRAIN, TIP, WALL, \
    POCKET_AIR, dial_parts_list, post_specs

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def _b(band):
    return DIAL_BANDS[band]


def _bt(band):
    lo, hi = DIAL_BANDS[band]
    return lo, hi - lo


def _gear(key, mate_key=None, wheel=True):
    z, m = DIAL_TRAIN[key]
    bl = active_variant().backlash * m      # backlash SCALES with module:
    if wheel:                               # 0.3 flat would eat half a
        mz = DIAL_TRAIN[mate_key][0]        # m0.6 tooth
        return gears.wheel_face(z, mz, module=m, backlash=bl, addendum=0.85)
    return gears.pinion_face(z, module=m, backlash=bl)


def center_post_d():
    """Ø3 register pin at the dial center: pressed into the plate, the
    cannon and hour pipe ride it. Nothing else holds the hands."""
    return Pos(0, 0, -4.1) * Cylinder(1.5, 4.1 + 5.8, align=BOTTOM)


def arbor_post_d(length):
    """Ø2 register pin: pressed deep into its feature-aware bore, tip
    at z-0.7 supporting AND locating the platform (dial-feet analog)."""
    return Cylinder(1.0, length, align=BOTTOM)


def cannon_d():
    """The cannon: pipe riding the center post, minute-hand seat below
    the face, 12t pinion at B3 and the 16t transfer wheel at B4 — both
    ABOVE the short hour pipe (the axis theorem)."""
    v = active_variant()
    lo3, t3 = _bt("B3")
    lo4, t4 = _bt("B4")
    part = Pos(0, 0, -3.9) * Cylinder(2.7, 3.9 + lo4 + t4, align=BOTTOM)
    part += Pos(0, 0, lo3) * extrude(_gear("cannon", wheel=False), t3)
    part += Pos(0, 0, lo4) * extrude(_gear("transfer", wheel=False), t4)
    part -= Pos(0, 0, -5) * Cylinder(1.5 + v.pivot_clearance, 20, align=BOTTOM)
    # minute hand friction flat
    part -= Pos(2.7, 0, -3.9) * extrude(Rectangle(0.8, 1.8), 1.0)
    return part


def hour_wheel_d():
    """Hour wheel (B1) + integral 24t moon pinion (B2) on a SHORT pipe
    over the cannon; hour-hand seat proud of the face."""
    v = active_variant()
    lo1, t1 = _bt("B1")
    lo2, t2 = _bt("B2")
    part = Pos(0, 0, -2.9) * Cylinder(3.7, 2.9 + lo2 + t2, align=BOTTOM)
    part += Pos(0, 0, lo1) * extrude(_gear("hour", "motion_p"), t1)
    part += Pos(0, 0, lo2) * extrude(_gear("moon_p", wheel=False), t2)
    part -= Pos(0, 0, -5) * Cylinder(2.7 + v.pivot_clearance, 20, align=BOTTOM)
    return part


def motion_arbor_d():
    """Motion works arbor: 10t pinion (B1, meshes the hour wheel) +
    36t wheel (B3, meshed by the cannon), shaft crossing B2."""
    v = active_variant()
    lo1, t1 = _bt("B1")
    lo3, t3 = _bt("B3")
    part = Pos(0, 0, lo1) * Cylinder(1.6, lo3 + t3 - lo1, align=BOTTOM)
    part += Pos(0, 0, lo1) * extrude(_gear("motion_p", wheel=False), t1)
    part += Pos(0, 0, lo3) * extrude(_gear("motion_w", "cannon"), t3)
    part -= Pos(0, 0, -5) * Cylinder(1.0 + v.pivot_clearance, 20, align=BOTTOM)
    return part


def w1_d():
    """Moon stage 1: 36t wheel (B2, meshes the hour pipe's 24t) + 12t
    pinion above (B3)."""
    v = active_variant()
    lo2, t2 = _bt("B2")
    lo3, t3 = _bt("B3")
    part = Pos(0, 0, lo2) * Cylinder(1.6, lo3 + t3 - lo2, align=BOTTOM)
    part += Pos(0, 0, lo2) * extrude(_gear("w1_w", "moon_p"), t2)
    part += Pos(0, 0, lo3) * extrude(_gear("w1_p", wheel=False), t3)
    part -= Pos(0, 0, -5) * Cylinder(1.0 + v.pivot_clearance, 20, align=BOTTOM)
    return part


def w2_d():
    """Moon stage 2: 54t wheel (B3) + 8t pinion at B1, shaft crossing B2."""
    v = active_variant()
    lo1, t1 = _bt("B1")
    lo3, t3 = _bt("B3")
    part = Pos(0, 0, lo1) * Cylinder(1.6, lo3 + t3 - lo1, align=BOTTOM)
    part += Pos(0, 0, lo1) * extrude(_gear("w2_p", wheel=False), t1)
    part += Pos(0, 0, lo3) * extrude(_gear("w2_w", "w1_p"), t3)
    part -= Pos(0, 0, -5) * Cylinder(1.0 + v.pivot_clearance, 20, align=BOTTOM)
    return part


def moon_disc_d():
    """70t moon carrier (B1): two moons recessed 0.25 into its face —
    visible through the platform window, nothing proud (the platform
    slides 0.3 under the disc plane)."""
    v = active_variant()
    lo1, t1 = _bt("B1")
    part = Pos(0, 0, lo1) * extrude(_gear("disc", "w2_p"), t1)
    for k in (0, 1):
        a = pi * k
        part -= Pos(13.5 * cos(a), 13.5 * sin(a), lo1 - 0.01) * \
            Cylinder(4.0, 0.26, align=BOTTOM)
    part -= Pos(0, 0, -5) * Cylinder(1.0 + v.pivot_clearance, 20, align=BOTTOM)
    return part


def xfer_pinion_d():
    """Transfer chain head: 16t friction-gripping the minute arbor's
    round stub via a SLIT COLLET (the hairspring pattern) — THE hand-
    setting slip: running torque carries, setting torque slips here."""
    v = active_variant()
    lo4, t4 = _bt("B4")
    face = _gear("transfer", wheel=False)
    bore = Circle(1.25 - v.press_r)                # grips the r1.25 stub
    slit = Pos(3.2, 0) * Rectangle(4.2, 0.45)
    part = Pos(0, 0, lo4) * extrude(face - bore - slit, t4)
    # hub extension doubles the collet's flexure length (DFM: a 0.8
    # slit collet alone is the least forgiving print in the stage)
    part += Pos(0, 0, lo4 - 0.8) * extrude(Circle(3.2) - bore - slit, 0.8)
    return part


def idler_d():
    """Transfer idler: 24t WHEEL-form (epicycloid addenda — pinion-form
    idlers only kissed noses; wheel-drives-pinion is the proper cycloidal
    pairing) at B4 on a Ø2 post."""
    v = active_variant()
    lo4, t4 = _bt("B4")
    part = Pos(0, 0, lo4) * extrude(_gear("idler", "transfer"), t4)
    part -= Pos(0, 0, -5) * Cylinder(1.0 + v.pivot_clearance, 20, align=BOTTOM)
    return part


PLATFORM_SCREWS = [(29.0, -56.0), (-44.0, -16.0), (18.0, 15.0)]
MOON_WINDOW = (29.16, -44.7, 4.5)    # disc orbit, toward 6 o'clock


def dial_sheet_d():
    """The dial: a Ø150 sheet riding the platform, located by the six
    post tips (real dial feet), moon window ringed, center pierced for
    the hour pipe. Face art (markers) embossed 0.3 — wave motifs come
    with the aesthetics pass."""
    from math import cos as c_, sin as s_
    part = Pos(0, 0, -1.9) * Cylinder(75.0, 1.0, align=BOTTOM)
    part -= Pos(0, 0, -5) * Cylinder(3.7 + 0.35, 20, align=BOTTOM)
    wx, wy, wr = MOON_WINDOW
    part -= Pos(wx, wy, -5) * Cylinder(wr, 20, align=BOTTOM)
    part += Pos(wx, wy, -1.9 - 0.3) * (
        Cylinder(wr + 1.6, 0.3, align=BOTTOM)
        - Cylinder(wr, 2, align=BOTTOM))            # window bezel ring
    for name, px, py, tip, top in post_specs():     # dial FEET recesses
        part -= Pos(px, py, -0.91) * Cylinder(1.15, 0.25, align=BOTTOM)
    for k in range(12):                # hour markers, ENGRAVED 0.35
        a = radians(90 - k * 30)       # (embossed ones would strike the
        mx_, my_ = 66 * c_(a), 66 * s_(a)   # hour hand; paint-fill later)
        L = 7.0 if k % 3 == 0 else 4.0
        part -= Pos(mx_, my_, -1.91) * extrude(
            Rectangle(1.8, L), 0.36
        ).rotate(Axis((mx_, my_, 0), (0, 0, 1)), 90 - k * 30)
    return part


def minute_hand_d():
    """Friction-seats the cannon's flat at z-3.9; blade to r70 with a
    gentle swell taper and a counterpoise — prints flat."""
    hub = Circle(3.5)
    bore = Circle(2.75) - Pos(2.35, 0) * Rectangle(1.2, 1.9)
    blade = _hand_blade(70.0, 2.6, 1.1)
    tail = Pos(-7.5, 0) * Circle(2.6) + Pos(-4, 0) * Rectangle(8, 2.2)
    face = (hub + blade + tail) - bore
    return Pos(0, 0, -3.9) * extrude(face, 0.9)


def hour_hand_d():
    """Friction-seats the hour pipe at z-2.9; blade to r46."""
    hub = Circle(4.6)
    bore = Circle(3.72)
    blade = _hand_blade(46.0, 3.4, 1.6)
    tail = Pos(-8.5, 0) * Circle(3.0) + Pos(-4.5, 0) * Rectangle(9, 2.8)
    face = (hub + blade + tail) - bore
    return Pos(0, 0, -2.9) * extrude(face, 0.9)


def _hand_blade(length, w_root, w_tip):
    """Tapered blade with a subtle swell — the wave, understated."""
    pts = []
    n = 24
    for i in range(n + 1):
        f = i / n
        w = (w_root + (w_tip - w_root) * f) * (1 + 0.18 * sin(pi * f)) / 2
        pts.append((3.0 + (length - 3.0) * f, w))
    for i in range(n + 1):
        f = 1 - i / n
        w = (w_root + (w_tip - w_root) * f) * (1 + 0.18 * sin(pi * f)) / 2
        pts.append((3.0 + (length - 3.0) * f, -w))
    from .revc_parts import _ccw_polygon
    return _ccw_polygon(pts)


def dial_platform_d():
    """The retaining platform (log 0013): closes every pocket, guards
    the works, carries the dial. Proud band -0.8..0; pipe hole at the
    center; the moon window opens NW over the disc's orbit."""
    L = DIAL_LAYOUT
    face = Circle(23.0)                                    # center cluster
    face += Pos(*L["motion"]) * Circle(TIP["motion_w"] + 4.0)
    face += Pos(*L["w1"]) * Circle(TIP["w1_w"] + 2.0)
    face += Pos(*L["w2"]) * Circle(TIP["w2_w"] + 2.0)
    face += Pos(*L["disc"]) * Circle(TIP["disc"] + 2.0)
    face += Pos(*L["i1"]) * Circle(TIP["idler"] + 2.0)
    face += Pos(*L["i2"]) * Circle(TIP["idler"] + 2.0)
    mx, my = REVC_LAYOUT["minute"]
    face += Pos(mx, my) * Circle(TIP["transfer"] + 2.0)
    for sx, sy in PLATFORM_SCREWS:
        face += Pos(sx, sy) * Circle(4.0)
    part = Pos(0, 0, -0.8) * extrude(face, 0.8)
    part -= Pos(0, 0, -5) * Cylinder(3.7 + 0.3, 20, align=BOTTOM)  # hour pipe
    wx, wy, wr = MOON_WINDOW
    part -= Pos(wx, wy, -5) * Cylinder(wr, 20, align=BOTTOM)
    for sx, sy in PLATFORM_SCREWS:
        part -= Pos(sx, sy, -5) * Cylinder(1.05, 20, align=BOTTOM)  # M2
    for name, px, py, tip, top in post_specs():   # post tips locate + prop
        part -= Pos(px, py, -5) * Cylinder(1.1, 20, align=BOTTOM)
    return part


def dial_pockets_and_bores():
    """(cutters, adders) the mainplate applies for the dial side:
    stepped pockets per part band, post bores, platform screws."""
    cuts = []
    for (name, x, y, tip_r, band) in dial_parts_list():
        lo, hi = DIAL_BANDS[band]
        cuts.append((x, y, tip_r + WALL, hi + POCKET_AIR))
    return cuts, post_specs()
