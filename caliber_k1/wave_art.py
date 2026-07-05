"""The wave, drawn properly — cubic Bezier art for the THREE-BRIDGE
composition (Jon's direction: his mock-up read the bridge layer as
separate plates whose gaps paint the wave; his NH35's own three bridges
prove the construction).

Geometry contract (enforced by tests, routed by design here):
- SEP1 (the swell line, west rim -> east rim) and SEP2 (the winding
  corner boundary, north rim -> SEP1) are TRUE separations: they are
  never keepout-clipped, so they must be routed clear of every boss,
  pocket and pillar. They split the bridge into SKY (NW), WINDING (NE)
  and SEA (south) plates.
- The CURL (Hokusai's crest) is a decorative spur off SEP1 biting into
  the sky plate; it and the sea's wave slots ARE keepout-clipped, so
  they can flow anywhere.

Control points live here in plain lists — edit them like you'd drag
handles in Illustrator. (If you'd rather draw: build123d can also
import SVG paths; say the word and we wire art/wave.svg in.)
"""


def _cubic(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n):
        t = i / n
        mt = 1 - t
        pts.append((mt**3 * p0[0] + 3 * mt**2 * t * p1[0]
                    + 3 * mt * t**2 * p2[0] + t**3 * p3[0],
                    mt**3 * p0[1] + 3 * mt**2 * t * p1[1]
                    + 3 * mt * t**2 * p2[1] + t**3 * p3[1]))
    return pts


def bezier_chain(start, segments, n=40):
    """start point + [(c1, c2, end), ...] -> smooth sampled polyline."""
    pts = []
    p0 = start
    for c1, c2, p3 in segments:
        pts += _cubic(p0, c1, c2, p3, n)
        p0 = p3
    pts.append(p0)
    return pts


# --- SEP1: the great swell, west rim to east rim ------------------------------
# passes SOUTH of the minute boss (-30.3, 23.5), dodges the ratchet
# pocket (0,41 r16.5), and sails over the module bay (z-clear).
SEP1 = bezier_chain(
    (-81.0, 6.0),
    [((-73, 8), (-64, 9.5), (-55, 11)),
     ((-46, 12.5), (-40, 14), (-34, 16)),
     ((-26, 18), (-18, 19), (-10, 19.5)),
     ((-2, 20), (8, 21), (20, 20.5)),
     ((32, 20), (41, 18.5), (50, 17)),
     ((60, 15), (70, 13), (81, 10.5))])

# --- SEP2: the winding corner, north rim down to SEP1 -------------------------
# west of the crown wheel (0,65 r16.2) and the ratchet pocket, landing
# ON SEP1 so the two gaps merge.
SEP2 = bezier_chain(
    (-12.0, 80.0),
    [((-15, 72), (-18, 65), (-18, 58)),
     ((-18, 51), (-20, 46), (-19, 42)),
     ((-17, 33), (-12, 25), (-2.5, 19.3))])   # lands PAST SEP1's centerline

# --- the CURL: Hokusai's crest, a spur off SEP1 into the sky plate ------------
# (keepout-clipped: it may approach the minute boss; structure wins)
CURL = bezier_chain(
    (-40.0, 14.2),
    [((-39, 20), (-37, 26), (-34, 30)),
     ((-31, 35), (-26, 37.5), (-20, 36.5)),
     ((-14, 35.5), (-10, 32), (-11, 28)),
     ((-12, 25), (-15, 23.8), (-19, 23.5))])

# --- the sea's wave slots (keepout-clipped, graceful now) ----------------------
SLOTS = [
    (bezier_chain((-66, -6),
                  [((-54, -10), (-44, -13), (-32, -13.5)),
                   ((-18, -14), (-4, -11), (10, -14)),
                   ((26, -17.5), (42, -18), (56, -15))]), 3.0),
    (bezier_chain((-58, -30),
                  [((-46, -35), (-36, -39), (-22, -41.5)),
                   ((-6, -44.5), (10, -44), (26, -45)),
                   ((38, -46), (48, -49), (55, -52))]), 3.6),
    (bezier_chain((-44, -52),
                  [((-33, -56.5), (-24, -59), (-12, -60.5)),
                   ((2, -62.5), (16, -62.5), (38, -60.5))]), 2.6),
    (bezier_chain((-64, 2),
                  [((-56, -1), (-49, -3), (-42, -3.5)),
                   ((-35, -4), (-29, -3), (-24, -1.5))]), 2.2),
]

SEP_GAP = 1.8       # clear air between bridge plates
CURL_W = (4.4, 2.2)  # the crest tapers toward its tip
