"""Ocean motifs for Caliber K1 — the tide complication's design language
starts in the frame itself.

Two elements:
- swirl_windows(): whirlpool-curved spoke cutouts for wheels — water
  circling a drain, in the plane of rotation.
- wave_bridge_face(): the train bridge as a breaking wave. The bridge body
  follows the swell line through its pivot points; above it, three rising
  swells build to a crest that curls over in a logarithmic spiral —
  the barrel of the wave, drawn in plan view.

Everything returns 2D faces (sampled polygons) for extrusion by callers.
"""

from math import atan2, cos, exp, pi, sin

from build123d import Circle, Polygon


def _ccw_polygon(pts):
    """Polygon with counterclockwise winding enforced — a CW loop makes a
    face whose normal points -z, and extrude() follows the face normal."""
    area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                - pts[(i + 1) % len(pts)][0] * pts[i][1]
                for i in range(len(pts)))
    if area2 < 0:
        pts = pts[::-1]
    return Polygon(*pts, align=None)


# ---------------------------------------------------------------------------
# Whirlpool spokes for wheels
# ---------------------------------------------------------------------------

def swirl_windows(r_in: float, r_out: float, spokes: int = 4,
                  spoke_w: float = 4.0, sweep_deg: float = 70.0):
    """Annular face minus curved spokes: returns the CUTOUT faces (a list)
    the caller subtracts from a wheel disc. Spokes curve like water
    spiraling — each window is bounded by two swept arcs.
    """
    sweep = sweep_deg * pi / 180
    windows = []
    n = 18
    gap = 2 * pi / spokes
    # angular width consumed by a spoke at radius r (constant width band)
    for k in range(spokes):
        a0 = k * gap
        pts = []
        # leading edge: spiral from (r_in, a0) to (r_out, a0 + sweep)
        for i in range(n + 1):
            f = i / n
            r = r_in + (r_out - r_in) * f
            a = a0 + sweep * f + spoke_w / r  # offset by spoke half-width-ish
            pts.append((r * cos(a), r * sin(a)))
        # outer arc to the next spoke's start
        a_end = a0 + gap - spoke_w / r_out
        for i in range(1, n + 1):
            a = (a0 + sweep + spoke_w / r_out) + \
                (a_end + sweep - (a0 + sweep + spoke_w / r_out)) * i / n
            pts.append((r_out * cos(a), r_out * sin(a)))
        # trailing edge: spiral back in (next spoke's leading side)
        for i in range(n + 1):
            f = 1 - i / n
            r = r_in + (r_out - r_in) * f
            a = a0 + gap + sweep * f - spoke_w / r
            pts.append((r * cos(a), r * sin(a)))
        # inner arc back to start
        a_start = a0 + spoke_w / r_in
        a_from = a0 + gap - spoke_w / r_in
        for i in range(1, n + 1):
            a = a_from + (a_start - a_from) * i / n
            pts.append((r_in * cos(a), r_in * sin(a)))
        windows.append(_ccw_polygon(pts))
    return windows


# ---------------------------------------------------------------------------
# The wave bridge
# ---------------------------------------------------------------------------

def _polyline_band(path, half_w: float):
    """Thick band along a polyline path: offset both sides, join into a
    closed polygon. Path points must be ordered; no self-intersection."""
    def normals(p):
        ns = []
        for i in range(len(p)):
            if i == 0:
                dx, dy = p[1][0] - p[0][0], p[1][1] - p[0][1]
            elif i == len(p) - 1:
                dx, dy = p[-1][0] - p[-2][0], p[-1][1] - p[-2][1]
            else:
                dx, dy = p[i + 1][0] - p[i - 1][0], p[i + 1][1] - p[i - 1][1]
            L = (dx * dx + dy * dy) ** 0.5
            ns.append((-dy / L, dx / L))
        return ns

    ns = normals(path)
    up = [(x + n[0] * half_w, y + n[1] * half_w) for (x, y), n in zip(path, ns)]
    dn = [(x - n[0] * half_w, y - n[1] * half_w) for (x, y), n in zip(path, ns)]
    return up + dn[::-1]


def _resample(path, n):
    """Densify a polyline to n points by linear interpolation."""
    import bisect
    d = [0.0]
    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        d.append(d[-1] + (dx * dx + dy * dy) ** 0.5)
    total = d[-1]
    out = []
    for i in range(n):
        t = total * i / (n - 1)
        j = min(bisect.bisect_left(d, t), len(path) - 1)
        if j == 0:
            out.append(path[0])
            continue
        f = (t - d[j - 1]) / (d[j] - d[j - 1] + 1e-12)
        out.append((path[j - 1][0] + f * (path[j][0] - path[j - 1][0]),
                    path[j - 1][1] + f * (path[j][1] - path[j - 1][1])))
    return out


def _chaikin(points, iterations: int = 3):
    """Corner-cutting smoothing: keeps endpoints, rounds interior corners
    so that offsetting the polyline cannot self-intersect."""
    pts = list(points)
    for _ in range(iterations):
        out = [pts[0]]
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            out.append((0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1))
            out.append((0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1))
        out.append(pts[-1])
        pts = out
    return pts


def wave_bridge_face(path_points, half_w: float = 6.5,
                     crest_at: float = 0.40, curl_r: float = 9.0):
    """Bridge body along path_points with an ocean-swell top edge and a
    curling crest.

    Built as ONE simple closed polygon: the inboard edge is a plain offset
    of the path; the outboard edge is offset by half_w plus a smooth lift —
    three gaussian swells rising toward the crest. The curl (a logarithmic
    spiral ribbon) is a second simple polygon unioned over the crest.
    Pass points ordered so the LEFT of travel faces away from the barrel.
    """
    n_pts = 90
    path = _resample(_chaikin(path_points), n_pts)

    def normal(i):
        j0, j1 = max(0, i - 1), min(len(path) - 1, i + 1)
        dx, dy = path[j1][0] - path[j0][0], path[j1][1] - path[j0][1]
        L = (dx * dx + dy * dy) ** 0.5
        return (-dy / L, dx / L)

    swells = [(4.0, crest_at - 0.30, 0.075),      # (height, center, width)
              (7.0, crest_at - 0.14, 0.075),
              (11.0, crest_at + 0.03, 0.085)]

    def lift(f):
        return sum(h * exp(-((f - c) / w) ** 2) for h, c, w in swells)

    inboard, outboard = [], []
    for i in range(n_pts):
        f = i / (n_pts - 1)
        nx, ny = normal(i)
        x, y = path[i]
        inboard.append((x - nx * half_w, y - ny * half_w))
        off = half_w + lift(f)
        outboard.append((x + nx * off, y + ny * off))
    body = _ccw_polygon(inboard + outboard[::-1])

    # The crest: a thick C-form rolling forward over the tallest swell.
    # What makes a wave read isn't the lip — it's the TUBE, the round
    # negative space under it. The C is a thick elliptical arc in the
    # local (travel, outboard) frame: rooted in the swell mass behind
    # the peak, arching over it, and diving forward until its lip kisses
    # the band edge — enclosing a round hollow. Minimum section ~3.5mm:
    # nothing to snap off.
    ci = int((crest_at + 0.03) * (n_pts - 1))
    nx, ny = normal(ci)
    tx, ty = ny, -nx                        # forward along the path
    # solid crest lobe: an ellipse leaning forward over the tallest swell
    ox = path[ci][0] + nx * 10.0 + tx * 2.0
    oy = path[ci][1] + ny * 10.0 + ty * 2.0
    a_l, b_l = 12.0, 8.5
    lobe = []
    n = 48
    for i in range(n + 1):
        phi = 2 * pi * i / n
        c_p, s_p = cos(phi), sin(phi)
        lobe.append((ox + a_l * c_p * tx + b_l * s_p * nx,
                     oy + a_l * c_p * ty + b_l * s_p * ny))
    body += _ccw_polygon(lobe)
    # the tube: an open round bite forward of the lobe center — it eats
    # the lobe's forward flank AND breaks out through the descending
    # swell edge, so the upper lip arcs over an OPEN hollow (the mouth
    # faces forward, like a wave about to close out). Positioned clear
    # of the W4 bearing boss (asserted by eye + clearance re-render).
    tube_r = 6.0
    tcx = path[ci][0] + tx * 9.0 + nx * 9.0
    tcy = path[ci][1] + ty * 9.0 + ny * 9.0
    tube = []
    for i in range(n + 1):
        phi = 2 * pi * i / n
        tube.append((tcx + tube_r * cos(phi), tcy + tube_r * sin(phi)))
    body -= _ccw_polygon(tube)
    return body
