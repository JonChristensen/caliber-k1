"""Caliber K1 rev C — real parts on the approved massing (Jon's gate,
July 3 2026). Every generator here is the rev B design re-derived onto
REVC_LAYOUT coordinates and the ZC z-map; nothing is free-floating.

Architecture facts this module encodes (derived, not asserted):
- HANGING BARREL: the 80t minute wheel overhangs the barrel center by
  6mm at plane B, so the barrel arbor tops out at z11 — single plate
  bearing, like modern movements. Winding enters from the DIAL side
  (arbor square below the plate; keyless stage builds on it).
- BAY STRAP: with the ring at z7.6 there is no room for a classic
  pallet cock — the removable cassette becomes a thin strap spanning
  the recessed escapement bay, feet screwed to the plate UNDER the
  ring's airspace (M2 x2 = lift the fork out, Jon's serviceability).
- INDIRECT MINUTE: only the minute arbor pierces the plate (through
  bore + dial-side stub) — the 1:1 transfer pair to the central cannon
  is the dial-side stage's job. All other lower pivots are blind.

Parts are modeled at LOCAL XY origin but GLOBAL z (the builder only
translates in XY and rotates for mesh phase).
"""
from math import atan2, cos, sin, pi, radians, hypot

from build123d import (Align, Box, Circle, Cylinder, Polygon, Pos, Rectangle,
                       RegularPolygon, Rot, extrude)

from . import gears
from .decor import _ccw_polygon, _polyline_band, swirl_windows
from .revb import active_variant
from .revc import (BAY_FLOOR, PLATE_T, REVC_BACKLASH, REVC_LAYOUT, RIM, ZC,
                   bay_band, bay_stations, bridge_pillar_xy, cock_layout_c,
                   lever_layout_c)

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def _bl():
    return active_variant().backlash


def _counts():
    return REVC_LAYOUT["counts"]


def _clr():
    return active_variant().pivot_clearance


def _press_r():
    """Bore radius that press-grips the Ø3 staff (variant interference)."""
    return 1.5 - active_variant().press_r


def _stack(z0, sections):
    """Bottom-up (face_or_radius, height) sections starting at z0."""
    part, z = None, z0
    for spec, h in sections:
        if isinstance(spec, (int, float)):
            layer = Pos(0, 0, z) * Cylinder(float(spec), h, align=BOTTOM)
        else:
            layer = Pos(0, 0, z) * extrude(spec, h)
        part = layer if part is None else part + layer
        z += h
    return part


def _band(path, half_w):
    return _ccw_polygon(_polyline_band(path, half_w))


# --- the mainplate ------------------------------------------------------------

def mainplate_c():
    """Ø170 x 6.5. Barrel recess, escapement bay (2.5 deep) with its
    lower pivot cups and integral banking pins, blind train bushings,
    the minute through-bore (indirect-minute interface), and every
    screw seat: strap M2, cock + bridge pillars M3 (dial-side hex
    pockets), stand feet M3 at the rim."""
    v = active_variant()
    L = lever_layout_c()
    Zd = _counts()[0]
    part = Cylinder(85, PLATE_T, align=BOTTOM)

    # barrel recess + BLIND arbor cup in its floor: the arbor rises to
    # a real bridge bearing (Jon's NH35 catch) and the dial face under
    # the barrel stays untouched
    bx, by = REVC_LAYOUT["barrel"]
    part -= Pos(bx, by, 2.2) * Cylinder(Zd / 2 - 1.0, 10, align=BOTTOM)
    part -= Pos(bx, by, 0.7) * Cylinder(2.85 + v.pivot_clearance, 2,
                                        align=BOTTOM)

    # escapement bay: union of resident circles + the E-P band (no cusp
    # wedge for the lever arm to hit), floor at BAY_FLOOR
    for (cx, cy), wall_r in bay_stations():
        part -= Pos(cx, cy, BAY_FLOOR) * Cylinder(wall_r, PLATE_T, align=BOTTOM)
    bpath, bhw = bay_band()
    part -= Pos(0, 0, BAY_FLOOR) * extrude(_band(bpath, bhw), PLATE_T)
    # lower pivot cups in the bay floor (escape, pallet, balance staff)
    for (cx, cy), r_cup in ((L["E"], 1.3), (L["P"], 1.3), (L["B"], 1.6)):
        part -= Pos(cx, cy, BAY_FLOOR - 1.8) * Cylinder(
            r_cup + v.pivot_clearance, 2.0, align=BOTTOM)
    # banking pins rise from the bay floor, flanking the fork neck
    for px, py in L["bank_pins"]:
        part += Pos(px, py, BAY_FLOOR) * Cylinder(1.0, 2.3, align=BOTTOM)

    # train bushings: blind from the top (dial face stays clean)...
    for k in ("third", "fourth"):
        x, y = REVC_LAYOUT[k]
        part -= Pos(x, y, PLATE_T - 3.0) * Cylinder(
            1.3 + v.pivot_clearance, 4, align=BOTTOM)
    # ...except the minute arbor: THROUGH (the indirect-minute interface)
    mx, my = REVC_LAYOUT["minute"]
    part -= Pos(mx, my, -1) * Cylinder(1.4 + v.pivot_clearance, 10,
                                       align=BOTTOM)

    # pallet strap screws (M2 self-tap pilot, blind)
    for fx, fy in L["strap_feet"]:
        part -= Pos(fx, fy, PLATE_T - 4.0) * Cylinder(0.9, 5, align=BOTTOM)
    # cock feet + bridge pillars: M3 through, dial-side hex nut pockets
    anchors = list(cock_layout_c()["feet"]) + bridge_pillar_xy()
    for ax, ay in anchors:
        part -= Pos(ax, ay, -1) * Cylinder(1.7, 10, align=BOTTOM)
        part -= Pos(ax, ay, -0.01) * extrude(RegularPolygon(5.7 / 3**0.5, 6), 2.4)
    # stand feet (M3) at the rim
    for az in (30, 150, 270):
        part -= Pos(78 * cos(radians(az)), 78 * sin(radians(az)), -1) * \
            Cylinder(1.7, 12, align=BOTTOM)
    # dial side: stepped pockets for the solved face (revc_dial), Ø2
    # register-post bores, the Ø3 center-post bore, platform M2 screws
    from .revc_dial_parts import PLATFORM_SCREWS, dial_pockets_and_bores
    cuts, posts = dial_pockets_and_bores()
    for cx, cy, pr, depth in cuts:
        part -= Pos(cx, cy, -0.01) * Cylinder(pr, depth + 0.01, align=BOTTOM)
    for name, px, py, tip, top in posts:
        part -= Pos(px, py, -0.01) * Cylinder(1.0 - v.press_r, top + 0.01,
                                              align=BOTTOM)
    part -= Pos(0, 0, -0.01) * Cylinder(1.5 - v.press_r, 5.91, align=BOTTOM)
    for sx, sy in PLATFORM_SCREWS:
        part -= Pos(sx, sy, -0.01) * Cylinder(0.8, 2.0, align=BOTTOM)
    return part


# --- barrel: hanging drum, dial-side winding ---------------------------------

DRUM_WALL_R = None  # derived below


def drum_c():
    """Going barrel, recessed z2.2-11.0: floor + wall carrying the 56t
    band at plane A. Slim walls inside the gear roots; interior hosts
    the strip (bench-formed; see SPRING_C). Cover rests on three lugs."""
    Zd = _counts()[0]
    r_wall_o = Zd / 2 - 1.5                      # 26.5, inside root r26.65
    floor = Pos(0, 0, ZC["drum"][0]) * Cylinder(r_wall_o, 1.2, align=BOTTOM)
    wall = Pos(0, 0, ZC["drum"][0] + 1.2) * (
        Cylinder(r_wall_o, ZC["drum"][1] - ZC["drum"][0] - 1.2, align=BOTTOM)
        - Cylinder(r_wall_o - 1.5, 20, align=BOTTOM))
    band = gears.wheel_face(Zd, _counts()[1], backlash=_bl(), addendum=0.85) \
        - Circle(r_wall_o - 0.2)
    part = floor + wall + Pos(0, 0, ZC["planeA"][0]) * extrude(band, 3.0)
    part -= Cylinder(2.85 + _clr(), 30)          # arbor bore
    # cover lugs at z9.6 + outer-end hook rib on the inner wall
    for k in range(3):
        a = radians(120 * k + 60)
        part += Pos((r_wall_o - 2.2) * cos(a), (r_wall_o - 2.2) * sin(a),
                    9.6 - 1.2) * Cylinder(1.4, 1.2, align=BOTTOM)
    part += Pos(r_wall_o - 2.6, 0, 3.4) * Box(2.2, 2.2, 4.5, align=BOTTOM)
    return part


def barrel_arbor_c():
    """Two-bearing barrel arbor (Jon's NH35 catch): plate cup below,
    bridge-web bearing above, ratchet square flush in the bridge pocket,
    FEMALE key socket in the top face — nothing pokes past z17.6."""
    part = _stack(0.8, [(2.7, 2.75),             # plate cup to drum floor
                        (5.5, 5.9),              # spring hub 3.55-9.45
                        (2.7, 1.4),              # cover journal to 10.85
                        (2.85, 5.15)])           # column to the bridge web
    sq = extrude(Rectangle(4.0, 4.0), 1.6)
    part += Pos(0, 0, 16.0) * sq                 # ratchet seat, in-pocket
    part -= Pos(0, 0, 15.6) * extrude(Rectangle(2.6, 2.6), 5)  # key socket
    part += Pos(5.5, 0, 3.4) * Box(2.4, 2.4, 6.2, align=BOTTOM)  # inner hook
    return part


def drum_cover_c():
    """Drop-in lid on the three lugs, flush at z10.8."""
    part = Pos(0, 0, 9.6) * Cylinder(24.8, 1.2, align=BOTTOM)
    part -= Cylinder(2.85 + _clr(), 30)
    return part


SPRING_C = dict(strip_t=2.2, strip_h=6.0, drum_id=54.0, hub_d=12.0,
                note="PETG, printed as a relaxed spiral; ~2.8 usable "
                     "turns x 6h = ~17h. TORQUE FLAG: bench-validate.")


def mainspring_c():
    """THE mainspring: a PETG spiral strip printed in its relaxed
    state — inner C-loop grips the arbor hub past its hook rib, outer
    tab hooks the drum wall rib. PETG ONLY (PLA creeps and snaps)."""
    from math import tau
    t, h = SPRING_C["strip_t"], SPRING_C["strip_h"]
    r0, r1, coils = 6.6, 25.2, 4.25
    theta_end = coils * tau
    b = (r1 - r0) / theta_end
    outer, inner = [], []
    n = int(coils * 60)
    for i in range(n + 1):
        th = theta_end * i / n
        r = r0 + b * th
        outer.append(((r + t / 2) * cos(th), (r + t / 2) * sin(th)))
        inner.append(((r - t / 2) * cos(th), (r - t / 2) * sin(th)))
    face = Polygon(*(outer + inner[::-1]), align=None)
    # inner end: C-loop around the arbor hub (r5.5), gap rides the rib
    face += Circle(6.6 + t / 2) - Circle(6.6 - t / 2)         - Pos(0, -6.6) * Rectangle(4.5, 4.0)
    # outer end: hook tab, catches the drum wall rib
    ex, ey = (r1 + t / 2) * cos(theta_end % tau), (r1 + t / 2) * sin(theta_end % tau)
    face += Pos(ex * 0.92, ey * 0.92) * Circle(2.4)
    part = Pos(0, 0, 3.5) * extrude(face, h)
    return part


def stand_foot_c():
    """Desk-stand foot (x3): M3 through, seats against the plate's rim
    holes from the dial side. Lifts the hands/platform clear of the desk."""
    part = Cylinder(6.0, 14.0, align=BOTTOM)
    part -= Cylinder(1.7, 40)
    part -= Pos(0, 0, -0.01) * extrude(RegularPolygon(5.7 / 3**0.5, 6), 2.6)
    return part


# --- train arbors (wheel + pinion + pivots, one print each) -------------------

def minute_arbor_c():
    """14t pinion (A) + 80t wheel (B). The ONE through arbor: dial-side
    stub with a D-flat for the future 1:1 transfer pinion."""
    part = _stack(1.6, [(1.25, 5.3),                       # stub + pivot
                        (1.75, 0.35),
                        (gears.pinion_face(_counts()[1], backlash=_bl()), 3.0),
                        (1.75, 1.0),
                        (gears.wheel_face(_counts()[2], _counts()[3],
                                          backlash=_bl(), addendum=0.85), 3.0),
                        (1.25, 1.95)])                     # top pivot to 16.2
    # dial stub stays ROUND: the transfer pinion grips it by friction
    # (slit collet) — that joint is how hands get SET without fighting
    # the whole train (the classic cannon-pinion slip, relocated)
    return part


def third_arbor_c():
    """48t wheel (A) + 8t pinion (B)."""
    return _stack(3.6, [(1.25, 3.3),
                        (1.75, 0.35),
                        (gears.wheel_face(_counts()[4], _counts()[5],
                                          backlash=_bl(), addendum=0.85), 3.0),
                        (1.75, 1.0),
                        (gears.pinion_face(_counts()[3], backlash=_bl()), 3.0),
                        (1.25, 1.95)])


def fourth_arbor_c():
    """8t pinion (A) + 36t wheel (B). Turns in exactly 60s — the future
    seconds/metronome tap."""
    return _stack(3.6, [(1.25, 3.3),
                        (1.75, 0.35),
                        (gears.pinion_face(_counts()[5], backlash=_bl()), 3.0),
                        (1.75, 1.0),
                        (gears.wheel_face(_counts()[6], _counts()[7],
                                          backlash=_bl(), addendum=0.85), 3.0),
                        (1.25, 1.95)])


def escape_arbor_c():
    """Bay-floor pivot, D-seat for the club wheel down in the bay,
    long climb to the 18t pinion at plane B, top pivot into the bridge."""
    part = _stack(2.3, [(1.25, 1.95),                      # bay cup pivot
                        (1.5, 2.45),                       # D-seat 4.25-6.7
                        (1.75, ZC["planeB"][0] - 6.7),     # the climb
                        (gears.pinion_face(_counts()[7], backlash=_bl()), 3.0),
                        (1.25, 1.95)])
    part -= Pos(1.13 + 15, 0, 4.25) * Box(30, 30, 2.45, align=BOTTOM)  # D-flat
    return part


# --- escapement (register parts: ciechanow.ski anatomy) ------------------------

def club_escape_wheel_c():
    """30t club-tooth wheel, r16, t2.4 — the proven rev B form, thinner
    for the bay. D-bore Ø3."""
    r_tip, r_root = 16.0, 13.2
    pts = []
    for k in range(30):
        a = 2 * pi * k / 30
        w = 2 * pi / 30
        pts.append((r_tip * cos(a), r_tip * sin(a)))
        pts.append((r_tip * 0.985 * cos(a + w * 0.22),
                    r_tip * 0.985 * sin(a + w * 0.22)))
        pts.append((r_root * cos(a + w * 0.45), r_root * sin(a + w * 0.45)))
    face = _ccw_polygon(pts)
    for wdw in swirl_windows(4.0, 11.0, spokes=4, spoke_w=3.0):
        face -= wdw
    part = extrude(face, 2.4)
    bore = Circle(1.53) - Pos(1.16, 0) * Rectangle(30, 30, align=(Align.MIN, Align.CENTER))
    part -= extrude(bore, 10)                    # drive fit on the D-seat
    return part


def swiss_lever_c():
    """The pallet fork on rev C geometry: t2.1 body (bay band), stones
    with variant lock/draw angles, long horns, guard finger, short
    integral pivots (down into the bay-floor cup, up into the strap).
    Modeled in the PALLET frame (P origin, +x toward the balance)."""
    L = lever_layout_c()
    ang = L["ang"]
    t_body = ZC["lever"][1] - ZC["lever"][0]              # 2.1

    def loc(pt):
        dx, dy = pt[0] - L["P"][0], pt[1] - L["P"][1]
        c, s = cos(-ang), sin(-ang)
        return (dx * c - dy * s, dx * s + dy * c)

    E_l = loc(L["E"])
    face = None
    for C in L["contacts"]:
        Cl = loc(C)
        rad = (Cl[0] - E_l[0], Cl[1] - E_l[1])
        rl = hypot(*rad)
        n = (rad[0] / rl, rad[1] / rl)
        dth = radians(90 - L["draw_deg"])
        t = (n[0] * cos(dth) - n[1] * sin(dth),
             n[0] * sin(dth) + n[1] * cos(dth))
        ith = radians(-38)
        m_ = (n[0] * cos(ith) - n[1] * sin(ith),
              n[0] * sin(ith) + n[1] * cos(ith))
        p_in = (Cl[0] - 1.0 * t[0], Cl[1] - 1.0 * t[1])
        p_tip = (Cl[0] + 1.2 * t[0], Cl[1] + 1.2 * t[1])
        p_imp = (p_tip[0] + 2.0 * m_[0], p_tip[1] + 2.0 * m_[1])
        p_back = (p_in[0] + 2.6 * n[0], p_in[1] + 2.6 * n[1])
        stone = _ccw_polygon([p_in, p_tip, p_imp, p_back])
        half = ((E_l[0] + Cl[0]) / 2, (E_l[1] + Cl[1]) / 2)
        hr = hypot(half[0] - E_l[0], half[1] - E_l[1])
        mid = (E_l[0] + (half[0] - E_l[0]) / hr * 19.0,
               E_l[1] + (half[1] - E_l[1]) / hr * 19.0)
        arm = _band([(0, 0), mid, p_back], 1.6)
        face = stone + arm if face is None else face + stone + arm
    face += Circle(3.2)
    fl = L["fork_len"] - 5.5                              # to the pin orbit
    face += _band([(0, 0), (fl + 0.7, 0)], 2.4)
    part = extrude(face, t_body)
    # fork slot: deep enough that the r1.25 pin (orbit r5.5) never
    # bottoms — notch floor at fl-1.6, pin's deepest sweep is fl-1.25
    part -= Pos(fl + 1.9, 0, 0.95) * extrude(Rectangle(7.0, 3.1), 3)
    # the guard-level floor must NOT run to the horn tips (it would ram
    # the r3.2 safety roller): cut it back, then the guard finger is the
    # only material at guard level toward the balance
    part -= Pos(fl - 1.0 + 15, 0, -0.01) * Box(30, 30, 0.97, align=BOTTOM)
    guard_tip = L["fork_len"] - 3.2 - 0.3     # 0.3 off the safety roller
    part += Pos((fl - 1.0 + guard_tip) / 2, 0, 0) * extrude(
        Rectangle(guard_tip - (fl - 1.0), 1.2), 0.95)
    # integral pivots: 2.0 down (tip rides the bay-cup floor), 0.9 up
    # (through the strap's hole, 0.1 witness above it)
    part += Pos(0, 0, -2.0) * Cylinder(1.25, 2.0, align=BOTTOM)
    part += Pos(0, 0, t_body) * Cylinder(1.25, 0.9, align=BOTTOM)
    return part


def bay_strap_c():
    """The rev C pallet cassette: a thin strap across the bay, blind cup
    over the fork's upper pivot, 2x M2 to the plate — remove it, lift
    the fork, service the balance. Rides UNDER the ring (0.6 air)."""
    L = lever_layout_c()
    P, feet = L["P"], L["strap_feet"]
    face = _band([loc for loc in (feet[0], P, feet[1])], 3.5)
    for f in feet:
        face += Pos(*f) * Circle(4.0)
    part = Pos(0, 0, ZC["strap"][0]) * extrude(face, ZC["strap"][1] - ZC["strap"][0])
    part -= Pos(P[0], P[1], 0) * Cylinder(1.3 + _clr(), 20, align=BOTTOM)
    for fx, fy in feet:
        part -= Pos(fx, fy, 0) * Cylinder(1.1, 20, align=BOTTOM)  # M2 pass
    return part


def roller_c():
    """Two-tier roller for the bay band: safety tier (crescent) below,
    impulse tier (pin at r5.5) above. Friction-fits the Ø3 staff."""
    saf = Circle(3.2) - Pos(3.4, 0) * Circle(1.4)
    part = Pos(0, 0, ZC["roller_saf"][0]) * extrude(
        saf, ZC["roller_saf"][1] - ZC["roller_saf"][0])
    imp = Circle(4.4) + Pos(5.5, 0) * Circle(1.25) + Pos(4.85, 0) * Rectangle(1.3, 1.5)
    part += Pos(0, 0, ZC["roller_imp"][0]) * extrude(
        imp, ZC["roller_imp"][1] - ZC["roller_imp"][0])
    part -= Pos(0, 0, 0) * Cylinder(_press_r(), 20, align=BOTTOM)
    return part


# --- oscillator ----------------------------------------------------------------

def balance_staff_c():
    """The staff IS the register's Ø3 rod: plain cylinder, bay cup to
    cock cup (print: printed; metal: cut steel rod). Grip parts (roller,
    wheel, collet) friction-press onto it."""
    return Pos(0, 0, 2.3) * Cylinder(1.5, 16.1 - 2.3, align=BOTTOM)


def balance_wheel_c():
    """Ø52 ring at z7.6-11.0, whirlpool spokes, 6 timing holes."""
    face = Circle(26.0)
    for w in swirl_windows(5.5, 20.0, spokes=3, spoke_w=5.0):
        face -= w
    part = Pos(0, 0, ZC["ring"][0]) * extrude(face, ZC["ring"][1] - ZC["ring"][0])
    for k in range(6):
        a = 2 * pi * k / 6
        part -= Pos(23.0 * cos(a), 23.0 * sin(a), 0) * Cylinder(1.45, 30, align=BOTTOM)
    part -= Cylinder(1.45, 30, align=BOTTOM)
    return part


def hairspring_c():
    """Slit-collet spiral, squeezed to h2.4 for the flat stack; grips
    the Ø3 rod, stud tab pinned to the cock's hanging post."""
    t, h, r0, r1, coils = 0.45, ZC["spring"][1] - ZC["spring"][0], 8.0, 24.0, 11
    theta_end = coils * 2 * pi
    b = (r1 - r0) / theta_end
    outer, inner = [], []
    n = coils * 40
    for i in range(n + 1):
        th = theta_end * i / n
        r = r0 + b * th
        outer.append(((r + t / 2) * cos(th), (r + t / 2) * sin(th)))
        inner.append(((r - t / 2) * cos(th), (r - t / 2) * sin(th)))
    face = Polygon(*(outer + inner[::-1]), align=None)
    face += Circle(r0 - t / 2 + 0.6) - Circle(_press_r() - 0.03)  # collet
    face += Pos(r1 + 3.2, 0) * Circle(3.4)                # stud tab ring
    face += Pos(r1 + 1.2, 0) * Rectangle(4.0, 3.4)
    face -= Pos(r1 + 3.2, 0) * Circle(2.3)                # ring slides OVER
                                                          # the cock's post
    # the SLIT (beat adjust): cuts the collet ring only, at an azimuth
    # where the first coil stands 0.56 off the collet lip (at -x the coil
    # is 0.13 away and the old slit severed the spring in two)
    sa = 5.0                                              # rad, ~286 deg
    slit = _ccw_polygon([( (1.0) * cos(sa) - w * -sin(sa),
                           (1.0) * sin(sa) - w * cos(sa)) for w in (-0.25, 0.25)]
                        + [( (8.6) * cos(sa) - w * -sin(sa),
                             (8.6) * sin(sa) - w * cos(sa)) for w in (0.25, -0.25)])
    face -= slit
    part = Pos(0, 0, ZC["spring"][0]) * extrude(face, h)
    return part


def balance_cock_c():
    """Coplanar with the bridge (14.7-17.7): two feet columns down to
    the PLATE (M3 through), arm over the staff, blind cup + the red
    cabochon pocket on top, stud post hanging to the hairspring."""
    ck = cock_layout_c()
    B, feet, stud = ck["B"], ck["feet"], ck["stud"]
    face = _band([feet[0], B, feet[1]], 5.5)
    face += Pos(*B) * Circle(7.0)
    face += _band([B, stud], 2.8)                # stud finger off the boss
    for f in feet:
        face += Pos(*f) * Circle(5.0)
    part = Pos(0, 0, ZC["bridge"][0]) * extrude(face, 3.0)
    for fx, fy in feet:                                   # columns to plate
        part += Pos(fx, fy, PLATE_T) * Cylinder(
            5.0, ZC["bridge"][0] - PLATE_T, align=BOTTOM)
        part -= Pos(fx, fy, 0) * Cylinder(1.7, 30, align=BOTTOM)
    part -= Pos(B[0], B[1], ZC["bridge"][0] - 0.01) * Cylinder(
        1.6 + _clr(), 1.51, align=BOTTOM)                 # staff cup to 16.2
    part -= Pos(B[0], B[1], ZC["bridge"][0] + 2.0) * Cylinder(
        2.1, 5, align=BOTTOM)                             # cabochon (web 0.5)
    part += Pos(stud[0], stud[1], 11.9) * Cylinder(
        2.15, ZC["bridge"][0] - 11.9 + 0.3, align=BOTTOM) # stud post, fused
    return part


# --- dial-side ratchet + click (M1's proven jamming click, ported) -------------

def click_geometry_c():
    """Click in the RATCHET frame (origin = ratchet center): block +
    tangential arm + wedge tip 0.9 into the 24t/O26 teeth. Lives WITH
    the ratchet, flush in the bridge-top pocket (the NH35 way)."""
    outline = [(16.9, -1.3), (22.1, -1.3), (22.1, 5.2), (16.9, 5.2),
               (16.9, 4.2), (4.0, 13.5), (2.9, 11.8), (5.1, 13.0),
               (16.9, 3.2)]
    pegs = [(18.0, 1.5), (21.5, 1.5)]
    return {"outline": outline, "pegs": pegs, "angle_deg": -30.0}


def click_pegs_global():
    g = click_geometry_c()
    bx, by = REVC_LAYOUT["barrel"]
    a = radians(g["angle_deg"])
    return [(bx + x * cos(a) - y * sin(a), by + x * sin(a) + y * cos(a))
            for x, y in g["pegs"]]


def ratchet_c():
    """24t ratchet on the arbor square, FLUSH in the bridge-top pocket
    (z16.05-17.65): winds by key from above, holds via the click."""
    face = gears.wheel_face(24, 24)
    face -= Rectangle(4.0 + 0.3, 4.0 + 0.3)               # square bore
    return Pos(0, 0, 16.05) * extrude(face, 1.6)


def click_c():
    """Flexure click beside the ratchet in the bridge pocket: an M2
    screw through the block does the holding, two O2.4 pegs do the
    locating (Jon's catch: the peg-only version read as floating)."""
    g = click_geometry_c()
    part = Pos(0, 0, 16.05) * extrude(_ccw_polygon(g["outline"]), 1.6)
    for x, y in g["pegs"]:
        part += Pos(x, y, 14.95) * Cylinder(1.2, 1.1, align=BOTTOM)
    part -= Pos(19.5, 2.0, 0) * Cylinder(1.05, 30, align=BOTTOM)  # M2
    return part


# --- the winding stage: crown wheel, stud, stem, clip (Jon's gate r6) ----------

def crown_wheel_c():
    """One flat crown wheel at the ratchet plane: 24t m1 spur rim (meshes
    the ratchet) with 23 bevel SLOTS in its underside annulus — meshed
    FROM BELOW by the stem's pinion (the rev B face-slot pair, flipped).
    Rides the shoulder stud; head counterbore keeps everything flush."""
    from math import degrees
    from .revc import WINDING
    face = gears.wheel_face(24, 24, backlash=_bl())
    part = Pos(0, 0, 16.05) * extrude(face, 1.6)
    r0, r1 = WINDING["slot_ring"]
    n = WINDING["slots"]
    for k in range(n):
        a = 360 * k / n
        part -= Pos(0, 0, 16.04) * (
            Rot(0, 0, a) * Pos((r0 + r1) / 2, 0, 0) *
            Box(r1 - r0, 1.7, 1.11, align=BOTTOM))
    part -= Cylinder(2.55 + _clr(), 40)                   # stud bore
    part -= Pos(0, 0, 17.05) * Cylinder(3.7, 2, align=BOTTOM)  # head seat
    return part


def crown_stud_c():
    """Shoulder stud: press tail into the bridge web, Ø5.1 bearing
    shoulder, mushroom head flush in the wheel's counterbore."""
    v = active_variant()
    part = Pos(0, 0, 14.69) * Cylinder(2.35 - v.press_r + 0.35, 1.31,
                                       align=BOTTOM)     # press tail
    part += Pos(0, 0, 16.0) * Cylinder(2.55, 1.05, align=BOTTOM)
    part += Pos(0, 0, 17.05) * Cylinder(3.55, 0.6, align=BOTTOM)
    return part


def stem_c():
    """The stem, one print: fluted crown OUTSIDE the rim, body through
    the bridge tunnel (clip groove inside), 7t m1 pinion at the tip
    meshing the crown wheel's underside slots. Axis y, z12.8."""
    from build123d import Rot as R_
    from .revc import WINDING
    z = WINDING["stem_z"]
    part = Pos(0, 87.5, z) * R_(-90, 0, 0) * Cylinder(6.8, 7.0, align=BOTTOM)
    for k in range(16):                                   # crown flutes
        a = 360 * k / 16
        part -= Pos(7.1 * cos(radians(a)), 87.5,
                    z + 7.1 * sin(radians(a))) * R_(-90, 0, 0) *             Cylinder(1.1, 8, align=BOTTOM)
    part += Pos(0, 74.7, z) * R_(-90, 0, 0) * Cylinder(2.5, 13.3,
                                                       align=BOTTOM)
    part += Pos(0, 74.7, z) * R_(-90, 0, 0) * extrude(
        gears.pinion_face(7, backlash=_bl()), 3.6)
    # clip groove inside the tunnel: retention against pull
    part -= (Pos(0, 82.6, z) * R_(-90, 0, 0) *
             (Cylinder(4.0, 1.3, align=BOTTOM) - Cylinder(1.7, 1.3,
                                                          align=BOTTOM)))
    return part


def stem_clip_c():
    """Printed C-clip: snaps into the stem's groove behind the tunnel."""
    from .revc import WINDING
    z = WINDING["stem_z"]
    face = Circle(3.3) - Circle(1.75)
    face -= Pos(0, -2.5) * Rectangle(2.6, 5)              # the C opening
    from build123d import Rot as R_
    return Pos(0, 82.65, z) * R_(-90, 0, 0) * extrude(face, 1.2)


# --- the bridge (plain broad cover; the WAVE is sculpted last, 2f) -------------

def _cock_cutout_face(gap=1.5):
    ck = cock_layout_c()
    B, feet = ck["B"], ck["feet"]
    face = _band([feet[0], B, feet[1]], 5.5 + gap)
    face += Pos(*B) * Circle(8.5 + gap)
    face += _band([B, ck["stud"]], 2.8 + gap)
    for f in feet:
        face += Pos(*f) * Circle(5.0 + gap)
    return face


def bridge_c():
    """ONE broad bridge over everything (14.7-17.7): four rim pillars
    down to the plate, upper pivot holes for the whole train (through,
    with cone lead-ins — a sighted four-pivot landing), and the balance
    bay OPEN to the rim with the cock nestled inside (no orphan rim
    sliver) — the NH35 composition. Plain; the wave pass sculpts it."""
    from build123d import Cone
    L = REVC_LAYOUT
    ck = cock_layout_c()
    B = L["balance"]
    a1 = ck["az"] + radians(26 + 8)
    a2 = ck["az"] - radians(26 + 8)
    wedge = _ccw_polygon([
        (B[0] + 30.5 * cos(a2), B[1] + 30.5 * sin(a2)),
        (B[0] + 95 * cos(a2), B[1] + 95 * sin(a2)),
        (B[0] + 95 * cos(a1), B[1] + 95 * sin(a1)),
        (B[0] + 30.5 * cos(a1), B[1] + 30.5 * sin(a1))])
    from .revc import WINDING as _W
    face = Circle(79.0) - Pos(*B) * Circle(30.0) - _cock_cutout_face() - wedge
    # the stem-tunnel TAB: the bridge reaches the rim over the tunnel
    # boss (Jon's catch: the boss only kissed the r79 edge and floated)
    face += Pos(0, 81.9) * Rectangle(13, 6.2)   # behind the pinion
    part = Pos(0, 0, ZC["bridge"][0]) * extrude(face, 3.0)
    for px, py in bridge_pillar_xy():
        part += Pos(px, py, PLATE_T) * Cylinder(
            4.0, ZC["bridge"][0] - PLATE_T, align=BOTTOM)
        part -= Pos(px, py, 0) * Cylinder(1.7, 30, align=BOTTOM)
    for k in ("minute", "third", "fourth", "escape"):
        x, y = L[k]
        part -= Pos(x, y, ZC["bridge"][0] - 0.01) * Cylinder(1.35, 4,
                                                             align=BOTTOM)
        part -= Pos(x, y, ZC["bridge"][0] - 0.01) * Cone(
            2.3, 1.35, 1.2, align=BOTTOM)                 # lead-in cone
    # the winding station (Jon's NH35 catch): arbor bearing through the
    # web, ratchet + click recessed FLUSH in the bridge top
    bx, by = L["barrel"]
    g = click_geometry_c()
    from math import cos as c_, sin as s_
    a = radians(g["angle_deg"])
    pocket = Pos(bx, by) * Circle(13.8)
    lobe = [(bx + x * c_(a) - y * s_(a), by + x * s_(a) + y * c_(a))
            for x, y in g["outline"]]
    pocket += _ccw_polygon(lobe)
    from build123d import offset as _off
    part -= Pos(0, 0, 16.0) * extrude(_off(pocket, 0.6), 2.0)
    part -= Pos(bx, by, ZC["bridge"][0] - 0.01) * Cylinder(
        2.85 + _clr(), 4, align=BOTTOM)                   # arbor bearing
    # crown wheel: flush pocket + stud press bore in the web
    from .revc import WINDING
    cwx, cwy = WINDING["crown_wheel"]
    part -= Pos(cwx, cwy, 16.0) * Cylinder(14.2, 2.0, align=BOTTOM)
    part -= Pos(cwx, cwy, 14.69) * Cylinder(2.35, 1.4, align=BOTTOM)
    # the winding-pinion WINDOW: the pinion reaches through the web to
    # the crown wheel's underside slots (every real movement has this)
    part -= Pos(0, WINDING["pinion_y"], 14.69) * Box(9.5, 8.4, 1.4,
                                                     align=BOTTOM)
    # stem tunnel boss under the bridge (the case-tube analog), with the
    # C-clip slot opening downward inside the run
    from build123d import Rot as R_
    zs = WINDING["stem_z"]
    part += Pos(0, 81.65, zs - 2.5) * Box(11, 5.7, 14.7 - (zs - 2.5),
                                         align=BOTTOM)  # behind the pinion
    part -= Pos(0, 78.7, zs) * R_(-90, 0, 0) * Cylinder(2.7, 20,
                                                        align=BOTTOM)
    part -= Pos(0, 83.25, zs - 2.6) * Box(7.0, 1.6, 6.5, align=BOTTOM)
    for x, y in g["pegs"]:
        part -= Pos(bx + x * c_(a) - y * s_(a), by + x * s_(a) + y * c_(a),
                    14.69) * Cylinder(1.25, 1.4, align=BOTTOM)  # through-web
    part -= Pos(bx + 19.5 * c_(a) - 2.0 * s_(a),
                by + 19.5 * s_(a) + 2.0 * c_(a),
                14.69) * Cylinder(0.9, 1.4, align=BOTTOM)  # click M2 pilot
    return part
