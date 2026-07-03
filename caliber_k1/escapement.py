"""Caliber K1 — Milestone 3: pin-pallet escapement + balance.

The escapement storey lives above the wave bridge; the balance sweeps over
the crest and its jewel — a real 4mm red cabochon acting as a functional
cap jewel — sits on the balance cock, dead over the tube of the wave.

Rotation: the escape wheel turns CCW (from above); tooth faces lead.
All XY geometry comes from parameters.m3_layout(); z from M3_LEVELS.
Local convention: parts model at their natural print orientation, z0 at
the lowest face; export positions them via assembly z from M3_LEVELS.
"""

from math import atan2, cos, pi, sin

from build123d import (
    Align, Circle, Cylinder, Polygon, Pos, Rectangle, Rot, extrude,
)

from .decor import _ccw_polygon, _polyline_band, swirl_windows
from .parameters import BAL, ESC, M3_LEVELS, TOL, m3_layout

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)
LV = M3_LEVELS


def escape_wheel():
    """30 pointed ratchet teeth; steep faces lead (CCW). D-bore Ø3."""
    z = ESC.wheel_teeth
    step = 2 * pi / z
    lean = ESC.tooth_lean_deg * pi / 180
    pts = []
    for k in range(z):
        a = k * step
        pts.append((ESC.wheel_tip_r * cos(a), ESC.wheel_tip_r * sin(a)))
        pts.append((ESC.wheel_root_r * cos(a + lean),
                    ESC.wheel_root_r * sin(a + lean)))
    face = _ccw_polygon(pts)
    # lightening: 4 swirl windows keep it on-theme and cut inertia
    for w in swirl_windows(4.0, ESC.wheel_root_r - 2.0, spokes=4, spoke_w=3.0):
        face -= w
    part = extrude(face, ESC.wheel_t)
    bore = Circle(1.5 + TOL.drive_clearance) - \
        Pos(1.1 + TOL.drive_clearance + 15, 0) * Rectangle(30, 30)
    part -= extrude(bore, ESC.wheel_t * 3)
    return part


def pallet_lever():
    """Anchor + fork, one print. Integral Ø2 pallet pins hang below the
    body into the wheel plane; integral Ø3 arbor pivots run up and down.
    Local frame: pallet arbor at origin, z0 = body bottom."""
    m = m3_layout()
    P = m["P"]
    body_t = LV["lever_t"]
    pin_drop = LV["lever_z"] - (LV["esc_wheel_z"] + 0.3)   # 3.2

    def loc(pt):  # global XY -> pallet-local
        return (pt[0] - P[0], pt[1] - P[1])

    pins = [loc(p) for p in m["pins"]]
    u = m["u_pb"]
    fork_tip = (u[0] * (m["fork_len"] - ESC.roller_r + 2.5),
                u[1] * (m["fork_len"] - ESC.roller_r + 2.5))
    slot_c = (u[0] * (m["fork_len"] - ESC.roller_r),
              u[1] * (m["fork_len"] - ESC.roller_r))

    face = _ccw_polygon(_polyline_band([pins[0], (0, 0), pins[1]], 2.2))
    face += _ccw_polygon(_polyline_band([(0, 0), fork_tip], 2.6))
    face += Circle(3.5)                                     # arbor hub
    for p in pins:
        face += Pos(*p) * Circle(2.2)                       # pin bosses
    # fork slot for the impulse pin
    ang = atan2(u[1], u[0]) * 180 / pi
    face -= Pos(*slot_c) * Rot(0, 0, ang) * Rectangle(6.0, ESC.fork_slot_w)

    part = extrude(face, body_t)
    for p in pins:                                          # pallet pins
        part += Pos(p[0], p[1], -pin_drop) * Cylinder(
            ESC.pin_d / 2, pin_drop, align=BOTTOM)
    # arbor pivots: down into the bridge pad, up into the platform
    lower = LV["lever_z"] - 18.0                            # pad seat at z18
    part += Pos(0, 0, -lower) * Cylinder(1.5, lower, align=BOTTOM)
    part += Pos(0, 0, body_t) * Cylinder(
        1.5, (LV["platform_z"] + LV["platform_t"] - 1.0) - (LV["lever_z"] + body_t),
        align=BOTTOM)
    return part


def roller():
    """Roller table on the balance staff: disc + impulse pin, one print."""
    face = Circle(4.0)
    face += Pos(ESC.roller_r, 0) * Circle(ESC.impulse_pin_d / 2)
    face += Pos(ESC.roller_r / 2 + 1, 0) * Rectangle(ESC.roller_r - 2, 2.0)
    part = extrude(face, LV["lever_t"])
    bore = Circle(BAL.staff_d / 2 + TOL.drive_clearance) - \
        Pos(BAL.staff_d / 2 - 1.2 + TOL.drive_clearance + 15, 0) * Rectangle(30, 30)
    part -= extrude(bore, LV["lever_t"] * 3)
    return part


def balance_staff():
    """Lower pivot (chaton) .. D-shaft .. upper pivot (under the cabochon)."""
    lower_pivot = 2.5                                       # z 18 -> 20.5
    shaft_len = (LV["cock_arm_z"] + 2.5) - 20.5             # to the cap jewel
    part = Cylinder(BAL.pivot_d / 2, lower_pivot, align=BOTTOM)
    shaft = Pos(0, 0, lower_pivot) * Cylinder(BAL.staff_d / 2, shaft_len - 4.5,
                                              align=BOTTOM)
    flat = BAL.staff_d / 2 - 1.2
    shaft -= Pos(flat + 15, 0, lower_pivot) * extrude(Rectangle(30, 30),
                                                      shaft_len - 4.5)
    part += shaft
    part += Pos(0, 0, lower_pivot + shaft_len - 4.5) * Cylinder(
        BAL.pivot_d / 2, 4.5, align=BOTTOM)
    return part


def balance_wheel():
    """Ø50 ring, whirlpool spokes, 6 rim holes for M3 timing nuts."""
    face = Circle(BAL.ring_od / 2)
    for w in swirl_windows(5.5, BAL.ring_id / 2 - 0.5, spokes=3, spoke_w=5.0):
        face -= w
    part = extrude(face, BAL.ring_h)
    for k in range(BAL.timing_holes):
        a = 2 * pi * k / BAL.timing_holes
        r = (BAL.ring_od + BAL.ring_id) / 4
        part -= Pos(r * cos(a), r * sin(a), 0) * Cylinder(1.45, BAL.ring_h * 3)
    bore = Circle(BAL.staff_d / 2 + TOL.drive_clearance) - \
        Pos(BAL.staff_d / 2 - 1.2 + TOL.drive_clearance + 15, 0) * Rectangle(30, 30)
    part -= extrude(bore, BAL.ring_h * 3)
    return part


def hairspring():
    """Archimedean spiral, collet at center, stud tab at the outer end."""
    t, h = BAL.hs_t, BAL.hs_h
    r0, r1, coils = BAL.hs_r_in, BAL.hs_r_out, BAL.hs_coils
    theta_end = coils * 2 * pi
    b = (r1 - r0) / theta_end
    n = coils * 40
    outer, inner = [], []
    for i in range(n + 1):
        th = theta_end * i / n
        r = r0 + b * th
        outer.append(((r + t / 2) * cos(th), (r + t / 2) * sin(th)))
        inner.append(((r - t / 2) * cos(th), (r - t / 2) * sin(th)))
    face = Polygon(*(outer + inner[::-1]), align=None)
    # collet: D-bore ring welded to the inner coil
    bore = Circle(BAL.staff_d / 2 + TOL.drive_clearance) - \
        Pos(BAL.staff_d / 2 - 1.2 + TOL.drive_clearance + 15, 0) * Rectangle(30, 30)
    face += Circle(r0 - t / 2 + 0.6) - bore
    # stud tab at the outer end (spiral ends at angle 0): Ø3.2 hole onto
    # the cock's printed stud pin
    face += Pos(r1 + 3.2, 0) * Circle(2.6)
    face += Pos(r1 + 1.2, 0) * Rectangle(4.0, 3.4)
    face -= Pos(r1 + 3.2, 0) * Circle(1.6 + TOL.snug_clearance)
    return extrude(face, h)


def tube_chaton():
    """Balance lower bearing, set into the wave tube from below the bridge.
    Flange against the bridge underside; two Ø2 spigot pins locate it."""
    part = Cylinder(8.0, 1.5, align=BOTTOM)                          # flange
    part += Pos(0, 0, 1.5) * Cylinder(6.0 - TOL.snug_clearance, 2.5,
                                      align=BOTTOM)                  # boss in tube
    part -= Pos(0, 0, 2.0) * Cylinder(BAL.pivot_d / 2 + TOL.pivot_clearance,
                                      5, align=BOTTOM)               # bearing
    for s in (+1, -1):
        part += Pos(0, s * 6.8, 1.5) * Cylinder(0.95, 1.4, align=BOTTOM)
    return part


def platform():
    """Escapement platform: bar over the escape + pallet upper pivots,
    standing on two bridge legs and one plate-rooted pillar. Banking
    posts hang from its underside, flanking the fork."""
    m = m3_layout()
    u, P = m["u_pb"], m["P"]
    branch_tip = (P[0] + 15 * u[0], P[1] + 15 * u[1])
    path = [m["pillar_a"], m["E"], m["P"], m["pillar_b"]]
    face = _ccw_polygon(_polyline_band(path, 5.0))
    face += _ccw_polygon(_polyline_band([m["P"], branch_tip], 4.0))
    part = extrude(face, LV["platform_t"])
    for key, r in (("E", 1.7 + TOL.pivot_clearance), ("P", 1.5 + TOL.pivot_clearance)):
        part -= Pos(*m[key]) * Cylinder(r, LV["platform_t"] * 3)
    # sockets over the two plate-rooted pillars' Ø3.2 spigots
    for key in ("pillar_a", "pillar_b"):
        part -= Pos(*m[key]) * Cylinder(1.6 + TOL.snug_clearance,
                                        LV["platform_t"] * 3)
    # banking posts flanking the fork neck at 12mm from the pallet arbor
    perp = (-u[1], u[0])
    for s in (+1, -1):
        x = P[0] + 12 * u[0] + s * 4.65 * perp[0]
        y = P[1] + 12 * u[1] + s * 4.65 * perp[1]
        part += Pos(x, y, -(LV["platform_z"] - 26.2)) * Cylinder(
            1.5, LV["platform_z"] - 26.2, align=BOTTOM)
    return part


def balance_cock():
    """Foot on the plate rim, column, arm over the wave to the staff.
    The upper bearing is capped by a 4mm red cabochon — the jewel,
    dead center over the tube of the wave."""
    m = m3_layout()
    F, B = m["cock_foot"], m["B"]
    arm_z = LV["cock_arm_z"]
    # foot pad + column (modeled standing at z0 = plate top)
    part = Pos(*F) * Cylinder(7.0, 4.0, align=BOTTOM)
    part += Pos(*F) * Cylinder(5.0, arm_z, align=BOTTOM)
    # arm: tapered band from column to the staff boss
    face = _ccw_polygon(_polyline_band([F, B], 5.0))
    face += Pos(*B) * Circle(6.0)
    arm = Pos(0, 0, arm_z) * extrude(face, LV["cock_arm_t"])
    part += arm
    # bearing: Ø2.9 through the arm; cabochon pocket from the top
    part -= Pos(B[0], B[1], arm_z - 1) * Cylinder(
        BAL.pivot_d / 2 + TOL.pivot_clearance, LV["cock_arm_t"] + 1, align=BOTTOM)
    part -= Pos(B[0], B[1], arm_z + LV["cock_arm_t"] - 1.5) * Cylinder(
        2.1, 3, align=BOTTOM)
    # hairspring stud: Ø3 pin down from the arm underside at the spring's
    # outer radius, along the arm direction
    u = ((B[0] - F[0]), (B[1] - F[1]))
    L = (u[0] ** 2 + u[1] ** 2) ** 0.5
    sx = B[0] - u[0] / L * (BAL.hs_r_out + 3.2)
    sy = B[1] - u[1] / L * (BAL.hs_r_out + 3.2)
    part += Pos(sx, sy, arm_z - 4.0) * Cylinder(1.5, 4.0, align=BOTTOM)
    # foot screw holes (2x M3), tangential to the rim
    tang = (-F[1] / (F[0] ** 2 + F[1] ** 2) ** 0.5,
            F[0] / (F[0] ** 2 + F[1] ** 2) ** 0.5)
    for s in (+1, -1):
        part -= Pos(F[0] + s * 4.5 * tang[0], F[1] + s * 4.5 * tang[1], 0) * \
            Cylinder(1.7, 12)
    return part
