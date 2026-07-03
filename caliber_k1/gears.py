"""Cycloidal gear profile generator — the horologically-correct tooth form.

Clock/watch trains use cycloidal (not involute) teeth: wheel teeth get an
epicycloidal addendum traced by a circle rolling on the pitch circle, and
low-count pinions get straight radial flanks with rounded noses. This form
tolerates the low tooth counts (8-16 leaf pinions) that watch trains demand,
where involute teeth would undercut.

Simplification used here (same as the printed-clock canon — Hugh Sparks /
Hessmer / MrBunsy): flanks below the pitch circle are radial lines; the
generating circle radius is half the mate's pitch radius. Proven to run
at FDM scale.

All profiles are returned as build123d faces built from sampled polygons —
numerically robust, no exotic B-rep operations.
"""

from math import atan2, cos, pi, sin

from build123d import Circle, Polygon

from .parameters import TRAIN


def _rotate(pts, ang):
    c, s = cos(ang), sin(ang)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def _epicycloid_flank(pitch_r: float, gen_r: float, tip_r: float, n: int = 12):
    """Epicycloid from the pitch circle outward, capped at tip_r.

    Returns points starting ON the pitch circle at angle 0, curving
    outward/forward (+angle). Each point is (radius, angle) converted
    to XY by the caller after mirroring/rotating.
    """
    pts = []
    t = 0.0
    step = 0.02
    while t < 2.0:
        x = (pitch_r + gen_r) * cos(t) - gen_r * cos((pitch_r + gen_r) / gen_r * t)
        y = (pitch_r + gen_r) * sin(t) - gen_r * sin((pitch_r + gen_r) / gen_r * t)
        r = (x * x + y * y) ** 0.5
        pts.append((x, y))
        if r >= tip_r:
            break
        t += step
    # resample down to n points for polygon economy
    if len(pts) > n:
        idx = [round(i * (len(pts) - 1) / (n - 1)) for i in range(n)]
        pts = [pts[i] for i in idx]
    return pts


def wheel_face(teeth: int, mate_teeth: int, module: float = None,
               backlash: float = None):
    """Face of a cycloidal WHEEL (drives a pinion). Centered at origin."""
    m = module if module is not None else TRAIN.module
    bl = backlash if backlash is not None else TRAIN.backlash
    R = m * teeth / 2
    tip_r = R + TRAIN.wheel_addendum * m
    root_r = R - TRAIN.wheel_dedendum * m
    gen_r = m * mate_teeth / 4          # half the mate pinion's pitch radius

    half_tooth = pi / (2 * teeth) - bl / (2 * R)   # half angular width at pitch
    flank = _epicycloid_flank(R, gen_r, tip_r)

    outline = []
    for k in range(teeth):
        a = 2 * pi * k / teeth
        # right flank: root -> pitch -> epicycloid out to tip
        right = [(root_r * cos(-half_tooth), root_r * sin(-half_tooth))]
        right += _rotate(flank, -half_tooth)
        # left flank: mirror of the epicycloid, walked tip -> pitch -> root
        left = _rotate([(x, -y) for x, y in reversed(flank)], half_tooth)
        left += [(root_r * cos(half_tooth), root_r * sin(half_tooth))]
        outline += _rotate(right + left, a)
    return Polygon(*outline, align=None)


def pinion_face(teeth: int, module: float = None, backlash: float = None):
    """Face of a cycloidal PINION: radial flanks, rounded noses."""
    m = module if module is not None else TRAIN.module
    bl = backlash if backlash is not None else TRAIN.backlash
    R = m * teeth / 2
    root_r = R - TRAIN.wheel_dedendum * m
    half_leaf = pi / (2 * teeth) - bl / (2 * R)
    nose_r = R * sin(half_leaf)         # semicircular nose atop radial flanks

    outline = []
    for k in range(teeth):
        a = 2 * pi * k / teeth
        leaf = [(root_r * cos(-half_leaf), root_r * sin(-half_leaf)),
                (R * cos(-half_leaf), R * sin(-half_leaf))]
        # nose arc: semicircle centered at (R, 0) bulging outward
        for i in range(9):
            th = -pi / 2 + pi * i / 8
            leaf.append((R + nose_r * cos(th) * 0.9, nose_r * sin(th)))
        leaf += [(R * cos(half_leaf), R * sin(half_leaf)),
                 (root_r * cos(half_leaf), root_r * sin(half_leaf))]
        outline += _rotate(leaf, a)
    return Polygon(*outline, align=None)


def center_distance(z1: int, z2: int, module: float = None) -> float:
    m = module if module is not None else TRAIN.module
    return m * (z1 + z2) / 2
