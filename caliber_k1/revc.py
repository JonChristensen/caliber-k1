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
    ("fourth_w", "esc_p"), ("esc_w", "lever"), ("lever", "ring"),
    ("lever", "spring"),
]}


def check_all(sweeps, clearance=1.0):
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

PLANES = {"A": (7.0, 10.5), "B": (11.0, 14.5), "E": (15.0, 18.0)}
RING = (18.7, 22.7)          # in the bridge's thickness (bridge 19.2-22.2)
BRIDGE = (19.2, 22.2)
SPRING_Z = (23.2, 25.7)
COCK = (26.2, 28.7)          # total stack target <= 28.7 + cabochon


def _station_sweeps(kind, x, y, counts):
    Zd, pm, Zm, p3, Z3, p4, Z4 = counts
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
        "escape": [Sweep("esc_p", x, y, 7, *PLANES["B"]),
                   Sweep("esc_w", x, y, 17, *PLANES["E"])],
        "balance": [Sweep("ring", x, y, 26, *RING),
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
        # (Zd, pm, Zm, p3, Z3, p4, Z4): (Zm/p3)*(Z3/p4) == 60 exactly.
        # Big minute wheel lives on plane B (clear above the recessed
        # drum); plane A keeps only small/medium residents.
        (56, 14, 80, 8, 48, 8, 24),      # drum 4h/rev
        (72, 12, 80, 8, 48, 8, 24),      # drum 6h/rev
        (56, 14, 90, 9, 48, 8, 24),      # drum 4h/rev, alt
    ]
    best = None
    for counts in menu:
        Zd, pm, Zm, p3, Z3, p4, Z4 = counts
        if abs((Zm / p3) * (Z3 / p4) - 60) > 1e-9:
            continue
        d_bm = (Zd + pm) / 2
        d_mt, d_tf, d_fe = (Zm + p3) / 2, (Z3 + p4) / 2, (Z4 + 12) / 2
        # barrel on +y axis (rotational symmetry); drum must fit the rim
        b_r = None
        for rr in range(30, 60, 2):
            if rr + (Zd + 6) / 2 <= RIM - 1:
                b_r = rr
        bx, by = 0.0, float(b_r)
        base = _station_sweeps("barrel", bx, by, counts)

        def ring_pts(cx, cy, d):
            for az in range(0, 360, step):
                yield (cx + d * cos(radians(az)),
                       cy + d * sin(radians(az)))

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
                        for Bx, By in ring_pts(ex, ey, 34.5):
                            s5 = s4 + _station_sweeps("balance", Bx, By, counts)
                            s5.append(Sweep("lever", (ex+Bx)/2, (ey+By)/2,
                                            19, *PLANES["E"]))
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
    "counts": (56, 14, 80, 8, 48, 8, 24),   # Zd, pm, Zm, p3, Z3, p4, Z4
    "barrel": (0.0, 50.0),                   # drum recessed z2.2-11.0
    "minute": (-23.4, 24.0),                 # 80t on plane B (indirect
    "third": (-52.9, -8.7),                  #  center display: 1:1 dial-
    "fourth": (-49.9, -36.6),                #  side transfer to cannon)
    "escape": (-31.9, -36.6),
    "balance": (2.6, -36.6),
    "drum_ratio": 4.0,                       # 4 h/rev -> ~18 h runtime
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
    s.append(Sweep("lever", (ex + Bx) / 2, (ey + By) / 2, 19, *PLANES["E"]))
    return s
