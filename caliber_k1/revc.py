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
        if hypot(s.x, s.y) + s.r > RIM:
            bad.append(f"{s.name}: past rim by "
                       f"{hypot(s.x, s.y) + s.r - RIM:.1f}")
    for i, a in enumerate(sweeps):
        for b in sweeps[i + 1:]:
            if not (a.rotating or b.rotating):
                continue
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
RING = (7.2, 11.0)           # ring literally on the plate
SPRING_Z = (11.7, 14.2)
BRIDGE = (14.7, 17.7)        # ONE bridge, well over the bay
COCK = (14.7, 17.7)          # coplanar cock — nothing higher


def _station_sweeps(kind, x, y, counts):
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = counts
    drum_r = (Zd + 6) / 2
    dh = 4.8 + 6.0
    S = {
        # drum body tucked INSIDE its gear roots, and RECESSED into the
        # mainplate (real-watch move) so its body clears plane B above
        "barrel": [Sweep("drum", x, y, Zd/2 - 1.5, 2.2, 11.0),
                   Sweep("drum_gear", x, y, Zd/2 + 1, *PLANES["A"])],
        "minute": [Sweep("min_p", x, y, pm/2 + 1, *PLANES["A"]),
                   Sweep("min_w", x, y, Zm/2 + 1, *PLANES["B"])],
        "third": [Sweep("third_p", x, y, p3/2 + 1, *PLANES["B"]),
                  Sweep("third_w", x, y, Z3/2 + 1, *PLANES["A"])],
        "fourth": [Sweep("fourth_p", x, y, p4/2 + 1, *PLANES["A"]),
                   Sweep("fourth_w", x, y, Z4/2 + 1, *PLANES["B"])],
        "escape": [Sweep("esc_p", x, y, pe/2 + 1, *PLANES["B"]),
                   Sweep("esc_w", x, y, 17, *ROLLER_Z)],
        "balance": [Sweep("roller", x, y, 6, *ROLLER_Z),
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
        # Z4/pe == 2 (30s escape). Fourth/escape enlarged to 36/18 so the
        # plane-A escape wheel clears the fourth arbor (mesh d 27 > 23).
        (56, 14, 80, 8, 48, 8, 36, 18),
        (72, 12, 80, 8, 48, 8, 36, 18),
        (56, 14, 90, 9, 48, 8, 36, 18),
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
        for b_r in range(b_max, b_max - 13, -4):
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
    # Zd, pm, Zm, p3, Z3, p4, Z4, pe — fourth/escape enlarged (36/18)
    # so the plate-level escape wheel clears the fourth arbor
    "counts": (56, 14, 80, 8, 48, 8, 36, 18),
    "barrel": (0.0, 39.0),                   # drum recessed z2.2-11.0
    "minute": (-22.5, 12.2),                 # 80t on plane B (indirect
    "third": (-22.5, -31.8),                 #  center display: 1:1 dial-
    "fourth": (-1.0, -49.8),                 #  side transfer to cannon)
    "escape": (24.3, -40.6),
    "balance": (44.3, -5.9),                 # ON THE PLATE (Jon's note)
    "lever_span": 40.0,
    "drum_ratio": 4.0,                       # 4 h/rev -> ~18 h runtime
    # v3: escapement bay recessed 2.5 into the plate, clearance 2.0
    # everywhere (Jon: use the rim room), stack tops at COCK z1 = 17.7
}


def revc_sweeps():
    """The frozen layout as swept volumes — THE global gate."""
    L = REVC_LAYOUT
    counts = L["counts"]
    s = []
    for k in ("barrel", "minute", "third", "fourth", "escape", "balance"):
        kind = "minute" if k == "minute" else k
        s += _station_sweeps(kind, *L[k], counts)
    ex, ey = L["escape"]
    Bx, By = L["balance"]
    ux, uy = (Bx - ex) / 40.0, (By - ey) / 40.0
    s.append(Sweep("lever_hub", ex + 20.6*ux, ey + 20.6*uy, 13, *ROLLER_Z))
    s.append(Sweep("lever_fork", ex + 34.0*ux, ey + 34.0*uy, 5, *ROLLER_Z))
    return s
