"""Caliber K1 rev C — the flat movement (log 0016 expert brief).

DISCIPLINE FIRST: nothing here is geometry. This module is the
whole-movement model — swept volumes, energy, and the layout solver.
Parts get modeled only after a layout passes check_all() and Jon's
massing gate.
"""
from dataclasses import dataclass
from math import cos, sin, pi, hypot

RIM = 83.0
PLATE_T = 6.5


@dataclass(frozen=True)
class Sweep:
    """A part's swept envelope: cylinder (rotating) or disc (static)."""
    name: str
    x: float
    y: float
    r: float
    z0: float
    z1: float
    rotating: bool = True


MESH_PAIRS = {frozenset(p) for p in [
    ("drum_gear", "min_p"), ("drum", "min_p"), ("min_w", "third_p"), ("third_w", "fourth_p"),
    ("ratchet", "crown_w"), ("ratchet", "b_arbor"), ("crown_w", "stem"),
    ("ratchet", "click_zone"), ("b_arbor", "click_zone"),
    ("drum_gear", "stem"),   # real clearance asserted analytically
    ("fourth_w", "esc_p"), ("esc_w", "lever_hub"), ("esc_w", "lever_fork"),
    ("lever_fork", "roller"), ("lever_fork", "ring"), ("lever_hub", "ring"),
    ("lever_fork", "spring"), ("lever_hub", "spring"),
    # intra-escapement: hub/fork are ONE part, and hub-to-roller spacing
    # is a constant of the mechanism (all on the escape->balance line) —
    # enforced by the escapement probe at part level, not the layout
    ("lever_hub", "lever_fork"), ("lever_hub", "roller"),
]}


def check_all(sweeps, clearance=2.0):
    """THE global test: every pair involving a rotating part must clear
    radially (if z-bands overlap) and stay inside the rim — EXCEPT
    meshing pairs, whose intentional engagement is verified by the
    phase-aligned probes at part level instead."""
    bad = []
    for s in sweeps:
        if s.name == "stem":
            continue                    # the stem EXITS the rim (crown)
        if hypot(s.x, s.y) + s.r > RIM:
            bad.append(f"{s.name}: past rim by "
                       f"{hypot(s.x, s.y) + s.r - RIM:.1f}")
    for i, a in enumerate(sweeps):
        for b in sweeps[i + 1:]:
            if not (a.rotating or b.rotating):
                continue
            if a.name == b.name:
                continue                # segments of one part
            if frozenset((a.name, b.name)) in MESH_PAIRS:
                continue
            if a.z1 <= b.z0 + 1e-9 or b.z1 <= a.z0 + 1e-9:
                continue
            d = hypot(a.x - b.x, a.y - b.y)
            if d < 0.01:
                continue
            need = a.r + b.r + clearance
            if d < need:
                bad.append(f"{a.name} x {b.name}: {need - d:.2f} short "
                           f"(z {max(a.z0,b.z0):.1f}-{min(a.z1,b.z1):.1f})")
    return bad


# --- energy model (replaces armchair spring math) ----------------------------

def spring_model(drum_id, hub_d, strip_t, strip_h, module_E=2.0e9):
    """PETG spiral in a drum: usable turns (half-fill rule), mean torque
    (N*mm, linearized), strip length (mm)."""
    r_wall, r_hub = drum_id / 2, hub_d / 2
    area = pi * (r_wall**2 - r_hub**2)
    L = area / 2 / strip_t
    turns_wound = ((r_hub**2 + L * strip_t / pi) ** 0.5 - r_hub) / strip_t
    turns_relax = (r_wall - (r_wall**2 - L * strip_t / pi) ** 0.5) / strip_t
    turns = turns_wound - turns_relax
    I_sec = strip_h * strip_t**3 / 12          # mm^4
    k = module_E * I_sec / (L * 1e3)           # N*mm per radian-ish
    tau_mean = k * (turns * 2 * pi) / 2 / 1e3  # rough mean torque N*mm... keep relative
    return {"turns": turns, "length": L, "tau_rel": strip_h * strip_t**3 / L}


def runtime_hours(turns, drum_ratio_to_center):
    """drum period = 1h * ratio (center wheel is exactly 60 min)."""
    return turns * drum_ratio_to_center


# --- the layout solver --------------------------------------------------------
# Chain: drum(Zd) -> [intermediate Zi/pi] -> center(Zc/pc at ORIGIN) ->
# third -> fourth -> escape -> lever span -> balance. Planes A/B alternate
# by mesh parity; escapement+lever plane E above B; ring in the well.

PLANES = {"A": (7.0, 10.5), "B": (11.0, 14.5)}
# Jon's massing note, watch-true: the balance lives ON THE PLATE in its
# own bay — lowest resident, everything steps over it. Escape wheel
# drops to plane A on an extended arbor to meet the lever down there.
# Escapement bay RECESSED 2.5 into the plate (Jon's note; real watches
# do this). Constraint carried to the dial-side solve: no dial pocket
# may share plan-area with this recess (web >= 1.2).
ROLLER_Z = (4.2, 6.7)        # roller + lever + escape wheel, IN the recess
RING = (7.6, 11.0)           # ring just over the plate (0.6 air over the
                             # pallet strap — the flat-movement squeeze)
SPRING_Z = (11.7, 14.2)
BRIDGE = (14.7, 17.7)        # ONE bridge, well over the bay
COCK = (14.7, 17.7)          # coplanar cock — nothing higher
BAY_FLOOR = 4.0              # escapement recess floor (2.5 into the plate)


def _station_sweeps(kind, x, y, counts):
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = counts
    drum_r = (Zd + 6) / 2
    dh = 4.8 + 6.0
    S = {
        # drum body tucked INSIDE its gear roots, and RECESSED into the
        # mainplate (real-watch move) so its body clears plane B above
        "barrel": [Sweep("drum", x, y, Zd/2 - 1.5, 2.2, 11.0),
                   Sweep("drum_gear", x, y, Zd/2 + 1, *PLANES["A"]),
                   Sweep("b_arbor", x, y, 2.85, 11.0, BRIDGE[1])],
        "minute": [Sweep("min_p", x, y, pm/2 + 1, *PLANES["A"]),
                   Sweep("min_w", x, y, Zm/2 + 1, *PLANES["B"])],
        "third": [Sweep("third_p", x, y, p3/2 + 1, *PLANES["B"]),
                  Sweep("third_w", x, y, Z3/2 + 1, *PLANES["A"])],
        "fourth": [Sweep("fourth_p", x, y, p4/2 + 1, *PLANES["A"]),
                   Sweep("fourth_w", x, y, Z4/2 + 1, *PLANES["B"])],
        "escape": [Sweep("esc_p", x, y, pe/2 + 1, *PLANES["B"]),
                   Sweep("esc_w", x, y, 17, *ROLLER_Z)],
        "balance": [Sweep("roller", x, y, 7, *ROLLER_Z),
                    Sweep("ring", x, y, 26, *RING),
                    Sweep("spring", x, y, 26, *SPRING_Z)],
    }
    return S[kind]


def solve_layout(step=12):
    """Staged placement, pruned. The minute wheel is FREE (hands reach
    the central cannon via a 1:1 dial-side transfer pair — indirect
    minute, classic practice). Chain: drum(A)->minP(A); minW(B)->
    thirdP(B); thirdW(A)->fourthP(A); fourthW(B)->escP(B); escW(E).
    Exactness: minute wheel = 60 min via drum ratio; fourth = 60 s;
    escape = 30 s (30t at 1 Hz). Barrel azimuth fixed (symmetry)."""
    from math import radians
    menu = [
        # (Zd, pm, Zm, p3, Z3, p4, Z4, pe): (Zm/p3)*(Z3/p4) == 60 exact;
        # Z4/pe == 2 (30s escape). Minute wheel CAPPED at 56t so its tip
        # (r29) clears the barrel center (mesh d 35) by the arbor column
        # + air — Jon's NH35 catch: the ratchet belongs on the MOVEMENT
        # side, so the barrel arbor must rise to the bridge.
        # 60/10 drum = 6h/rev (MORE spring room: ~17h runtime); minute
        # pinion r6 clears the coplanar third wheel; minute wheel r29
        # clears the barrel arbor column. (56/7)(45/6) = 60.000 exact.
        (60, 10, 56, 7, 45, 6, 36, 18),
    ]
    best = None
    for counts in menu:
        Zd, pm, Zm, p3, Z3, p4, Z4, pe = counts
        if abs((Zm / p3) * (Z3 / p4) - 60) > 1e-9 or Z4 != 2 * pe:
            continue
        d_bm = (Zd + pm) / 2
        d_mt, d_tf, d_fe = (Zm + p3) / 2, (Z3 + p4) / 2, (Z4 + pe) / 2
        def ring_pts(cx, cy, d):
            for az in range(0, 360, step):
                yield (cx + d * cos(radians(az)),
                       cy + d * sin(radians(az)))

        b_max = int(RIM - 1 - (Zd + 6) / 2)
        # dial-side reservation: the drum recess plan edge must stay
        # >= 10.7 from the ORIGIN (the moon pinion's pocket lives there)
        b_min = int(Zd / 2 - 1 + 10.7) + 1
        for b_r in range(b_max, b_min - 1, -4):
          bx, by = 0.0, float(b_r)
          base = _station_sweeps("barrel", bx, by, counts)
          for mx, my in ring_pts(bx, by, d_bm):
              s1 = base + _station_sweeps("minute", mx, my, counts)
              if check_all(s1):
                  continue
              for tx, ty in ring_pts(mx, my, d_mt):
                  s2 = s1 + _station_sweeps("third", tx, ty, counts)
                  if check_all(s2):
                      continue
                  for fx, fy in ring_pts(tx, ty, d_tf):
                      s3 = s2 + _station_sweeps("fourth", fx, fy, counts)
                      if check_all(s3):
                          continue
                      for ex, ey in ring_pts(fx, fy, d_fe):
                          s4 = s3 + _station_sweeps("escape", ex, ey, counts)
                          if check_all(s4):
                              continue
                          for Bx, By in ring_pts(ex, ey, 40.0):
                              s5 = s4 + _station_sweeps("balance", Bx, By, counts)
                              ux, uy = (Bx - ex) / 40.0, (By - ey) / 40.0
                              s5.append(Sweep("lever_hub", ex + 20.6*ux,
                                              ey + 20.6*uy, 13, *ROLLER_Z))
                              s5.append(Sweep("lever_fork", ex + 34.0*ux,
                                              ey + 34.0*uy, 5, *ROLLER_Z))
                              if check_all(s5):
                                  continue
                              reach = max(hypot(s.x, s.y) + s.r for s in s5)
                              cand = (reach, dict(
                                  counts=counts, barrel=(bx, by),
                                  minute=(round(mx,1), round(my,1)),
                                  third=(round(tx,1), round(ty,1)),
                                  fourth=(round(fx,1), round(fy,1)),
                                  escape=(round(ex,1), round(ey,1)),
                                  balance=(round(Bx,1), round(By,1))))
                              if best is None or cand[0] < best[0]:
                                  best = cand
    return best


# --- THE REV C LAYOUT (solver output, frozen; Jon's massing gate next) -------
REVC_LAYOUT = {
    # Zd, pm, Zm, p3, Z3, p4, Z4, pe: 60/10 drum (6h/rev), 56t minute
    # (clears the barrel ARBOR COLUMN - Jon's NH35 catch: the ratchet
    # lives on the MOVEMENT side, recessed flush in the bridge top),
    # 45/6 third, 36/18 fourth/escape. (56/7)(45/6) = 60.000 exact.
    "counts": (60, 10, 56, 7, 45, 6, 36, 18),
    "barrel": (0.0, 41.0),                   # drum recessed z2.2-11.0;
    "minute": (-30.3, 23.5),                 #  y>=40: dial reservation
    "third": (-46.1, -3.8),
    "fourth": (-41.6, -28.9),
    "escape": (-14.6, -28.9),
    "balance": (25.4, -28.9),
    "lever_span": 40.0,
    "drum_ratio": 6.0,                       # 6 h/rev x ~2.8 turns = ~17 h
    # v4: movement-side ratchet architecture; bay recessed; clearance
    # 2.0 everywhere; stack still tops at COCK z1 = 17.7
}


# --- the winding station (Jon's NH35 catch, completed): ratchet + click
# flush in the bridge-top pocket, crown wheel outboard toward 12, stem
# entering over the rim like a pocket-watch pendant. The stem's pinion
# must clear the crown wheel's top: the pendant boss stands proud of the
# bridge at the rim — THE open question for Jon's massing gate.
WINDING = {
    # 6498-true: the crown wheel is ONE flat wheel at the ratchet plane
    # with 23 bevel SLOTS cut into its UNDERSIDE annulus; the winding
    # pinion meshes it FROM BELOW (rev B's proven face-slot pair,
    # flipped — the height cost becomes a height savings). Stem axis
    # z12.8, dead in the corridor; nothing above the bridge (Jon's
    # section-view catch).
    "ratchet_r": 13.6, "pocket_z": (16.05, 17.65),
    "crown_wheel": (0.0, 65.0),              # 24t x 24t m1: exactly 24
    "slot_ring": (8.5, 13.0),                # spans the pinion tip chord
    "slots": 23,                             # = m1 pitch at ring r11.5
    "stem_z": 12.8,                          # pinion tip dips 1.1 into
    "pinion_y": 76.5,                        #  the slots from below
    "stem_y": (74.7, 94.5),
    "module_bay": (56.0, 18.0, 18.0),        # reserved: metronome barrel
}


def winding_sweeps():
    """The winding station + reservations as gate-covered volumes."""
    bx, by = REVC_LAYOUT["barrel"]
    cw = WINDING["crown_wheel"]
    z0, z1 = WINDING["pocket_z"]
    s = [Sweep("ratchet", bx, by, WINDING["ratchet_r"], z0, z1),
         Sweep("crown_w", cw[0], cw[1], WINDING["ratchet_r"], z0, z1),
         Sweep("click_zone", bx + 14.3, by - 1.3, 9.5, z0, z1,
               rotating=False),
         # the winding pinion's swept cylinder + the stem run. Vertical
         # cans over-approximate a horizontal cylinder, so drum_gear x
         # stem is whitelisted and the REAL cylinder-to-tip clearance
         # (>=2.0) is asserted analytically in the test suite.
         Sweep("stem", 0.0, WINDING["pinion_y"], 4.6,
               WINDING["stem_z"] - 4.4, WINDING["stem_z"] + 4.4),
         Sweep("stem", 0.0, 81.0, 2.7, WINDING["stem_z"] - 2.5,
               WINDING["stem_z"] + 2.5),
         Sweep("stem", 0.0, 87.0, 2.7, WINDING["stem_z"] - 2.5,
               WINDING["stem_z"] + 2.5)]
    mx, my, mr = WINDING["module_bay"]
    s.append(Sweep("module_bay", mx, my, mr, 7.0, 14.5, rotating=False))
    return s


# --- THE COMPONENT INVENTORY: everything that lives in the movement.
# The massing BUILDS from this list and a test fails if it forgets one —
# Jon's rule: no massing without reciting the full cast first.
INVENTORY = [
    # (label, source): sweeps come from the gate model; zones are static
    ("mainplate", "plate"), ("bridge", "zone"), ("balance cock", "zone"),
    ("pallet strap", "zone"), ("drum", "sweep"), ("drum_gear", "sweep"),
    ("b_arbor", "sweep"), ("min_p", "sweep"), ("min_w", "sweep"),
    ("third_p", "sweep"), ("third_w", "sweep"), ("fourth_p", "sweep"),
    ("fourth_w", "sweep"), ("esc_p", "sweep"), ("esc_w", "sweep"),
    ("lever_hub", "sweep"), ("lever_fork", "sweep"), ("roller", "sweep"),
    ("ring", "sweep"), ("spring", "sweep"),
    ("ratchet", "sweep"), ("crown_w", "sweep"), ("click_zone", "sweep"),
    ("stem", "sweep"), ("module_bay", "sweep"),
    ("dial works", "dial"), ("dial platform", "dial"),
]


def revc_sweeps():
    """The frozen layout as swept volumes — THE global gate."""
    L = REVC_LAYOUT
    counts = L["counts"]
    s = []
    for k in ("barrel", "minute", "third", "fourth", "escape", "balance"):
        kind = "minute" if k == "minute" else k
        s += _station_sweeps(kind, *L[k], counts)
    s += winding_sweeps()
    ex, ey = L["escape"]
    Bx, By = L["balance"]
    ux, uy = (Bx - ex) / 40.0, (By - ey) / 40.0
    s.append(Sweep("lever_hub", ex + 20.6*ux, ey + 20.6*uy, 15.5, *ROLLER_Z))
    s.append(Sweep("lever_fork", ex + 34.0*ux, ey + 34.0*uy, 5, *ROLLER_Z))
    return s


# --- part-level z-map (parts port; all ABSOLUTE, dial face = z0) -------------
# Derived from the frozen bands above; parts assert against these.
REVC_BACKLASH = 0.30
ZC = {
    "bay_cup_floor": BAY_FLOOR - 1.8,        # lower pivot cups in the bay
    "esc_wheel": (4.2, 6.6),                 # club wheel t2.4
    "lever": (4.2, 6.3),                     # fork body t2.1, pivots +-
    "roller_saf": (4.2, 5.15),               # safety tier == guard band
    "roller_imp": (5.15, 6.7),               # impulse tier == slot band
    "strap": (6.55, 7.1),                    # removable pallet strap
    "planeA": (7.25, 10.25),                 # gear metal inside PLANES["A"]
    "planeB": (11.25, 14.25),                # gear metal inside PLANES["B"]
    "ring": (7.6, 11.0),
    "spring": (11.7, 14.1),
    "bridge": BRIDGE,
    "bush_floor": PLATE_T - 3.0,             # train lower bushings (blind)
    "drum": (2.2, 11.0),
}


def mesh_ideals(layout=None):
    """(name, station_a, station_b, ideal_center_distance) for the four
    train meshes at module 1.0 — the exactness gate."""
    L = layout or REVC_LAYOUT
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = L["counts"]
    return [("drum-minute", "barrel", "minute", (Zd + pm) / 2),
            ("minute-third", "minute", "third", (Zm + p3) / 2),
            ("third-fourth", "third", "fourth", (Z3 + p4) / 2),
            ("fourth-escape", "fourth", "escape", (Z4 + pe) / 2)]


def lever_layout_c(variant=None):
    """Swiss lever on rev C coordinates (same proven proportions as rev B:
    r_esc 16, 6.5-space embrace = +-39 deg, stones dip 1.2). E, P, B
    colinear; strap feet flank P; banking pins rise from the bay floor."""
    from math import atan2, cos, sin, radians
    if variant is None:
        from .revb import active_variant
        variant = active_variant()
    E = REVC_LAYOUT["escape"]
    B = REVC_LAYOUT["balance"]
    span_mm = REVC_LAYOUT["lever_span"]
    ang = atan2(B[1] - E[1], B[0] - E[0])
    r_esc = 16.0
    span = radians(39)
    a = r_esc / cos(span)                        # 20.59
    u = (cos(ang), sin(ang))
    P = (E[0] + a * u[0], E[1] + a * u[1])
    dip = r_esc * sin(radians(variant.lock_deg)) + 0.4   # lock -> stone dip
    r_eng = r_esc - dip
    contacts = [(E[0] + r_eng * cos(ang + s * span),
                 E[1] + r_eng * sin(ang + s * span)) for s in (+1, -1)]
    perp = (-u[1], u[0])
    feet = [(P[0] + s * 19.5 * perp[0], P[1] + s * 19.5 * perp[1])
            for s in (+1, -1)]                   # strap feet, on solid plate
    # banking pins: neck half 2.4 + pin r1.0 + swing room at the 8mm station
    from math import tan
    bank_off = 2.4 + 1.0 + 8 * tan(radians(6.5))
    pins = [(P[0] + 8 * u[0] + s * bank_off * perp[0],
             P[1] + 8 * u[1] + s * bank_off * perp[1]) for s in (+1, -1)]
    return {"E": E, "P": P, "B": B, "ang": ang, "a": a, "r_esc": r_esc,
            "dip": dip, "bank_deg": 6.5,
            "contacts": contacts, "span_deg": 39.0,
            "lock_deg": variant.lock_deg, "draw_deg": variant.draw_deg,
            "fork_len": span_mm - a, "strap_feet": feet, "bank_pins": pins}


def bay_stations():
    """Centers + wall radii of the escapement bay recess (plan outline =
    resident sweeps + 1.5 wall). Shared by the mainplate and the tests."""
    Lv = lever_layout_c()
    E, P, B = Lv["E"], Lv["P"], Lv["B"]
    u = (cos(Lv["ang"]), sin(Lv["ang"]))
    fork = (E[0] + 34.0 * u[0], E[1] + 34.0 * u[1])
    return [(E, 17 + 1.5), (P, 15.5 + 1.5), (fork, 5 + 1.5), (B, 7 + 1.5)]


def bay_band():
    """The E-P connecting band of the recess (same wall as the P circle):
    without it a concave cusp of solid plate survives between the two wall
    circles — the lever's exit-arm cap swings through that wedge."""
    Lv = lever_layout_c()
    return ([Lv["E"], Lv["P"]], 15.5 + 1.5)


def cock_layout_c():
    """Balance cock: coplanar with the bridge, feet columns to the PLATE
    (rim side of the balance), stud post at the hairspring's outer end."""
    from math import atan2, cos, sin, radians
    B = REVC_LAYOUT["balance"]
    az = atan2(B[1], B[0])                       # toward the rim
    feet = [(B[0] + 33.5 * cos(az + radians(s)),
             B[1] + 33.5 * sin(az + radians(s))) for s in (26, -26)]
    stud_az = az                                 # centered between the arms,
    stud = (B[0] + 27.2 * cos(stud_az),          # on its own finger off the
            B[1] + 27.2 * sin(stud_az))          # boss (clear of the columns)
    return {"B": B, "feet": feet, "stud": stud, "az": az, "stud_az": stud_az}


BRIDGE_PILLARS = [(55, 74.0), (145, 74.0), (200, 74.0), (285, 74.0),
                  (165.2, 70.3), (37.8, 73.4)]  # sky + winding anchors


def bridge_pillar_xy():
    from math import cos, sin, radians
    return [(r * cos(radians(az)), r * sin(radians(az)))
            for az, r in BRIDGE_PILLARS]
