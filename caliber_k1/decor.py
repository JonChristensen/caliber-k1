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
                     crest_at: float = 0.45, curl_r: float = 9.0):
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

    # the curl: logarithmic spiral ribbon rolling forward over the crest
    ci = int((crest_at + 0.03) * (n_pts - 1))
    nx, ny = normal(ci)
    cx = path[ci][0] + nx * (half_w + swells[-1][0] - curl_r * 0.30)
    cy = path[ci][1] + ny * (half_w + swells[-1][0] - curl_r * 0.30)
    tx, ty = ny, -nx                       # travel direction (left-normal frame)
    base_ang = atan2(ny, nx)               # spiral starts pointing outboard
    spiral_out, spiral_in = [], []
    n = 36
    for i in range(n + 1):
        th = 2.5 * pi * i / n
        r_o = curl_r * exp(-0.20 * th)
        # ribbon never thinner than 1.2mm (3 perimeters at 0.4 nozzle)
        r_i = max(min(r_o - 1.2, r_o - 2.6 * exp(-0.25 * th)), 0.4)
        a = base_ang - th                  # curl rolls forward/down-swell
        spiral_out.append((cx + r_o * cos(a), cy + r_o * sin(a)))
        spiral_in.append((cx + r_i * cos(a), cy + r_i * sin(a)))
    body += _ccw_polygon(spiral_out + spiral_in[::-1])
    return body
