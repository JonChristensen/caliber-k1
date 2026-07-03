"""Brute-force placement solver for the M4 motion-works chain (option B).

Chain: W1 16t pinion (L2) -> R1 32t (L2, pinion 10t on L1)
       -> R2 24t (L1, pinion 10t on L0) -> [idlers 24t on L0] -> T 30t (L0)
       -> M arbor (36t wheel on L0, meshing T's 12t cannon).
Levels (rel plate top): L0 0.5-5.5, L1 5.5-10.5, L2 10.5-15.5.
"""
from math import cos, sin, pi, hypot

W1 = (-18.1, -40.1)
RIM = 83.0
# obstacles: (x, y, radius, levels)
OBS = [
    (0, 0, 37.75, (0, 1, 2)),           # drum + tooth band
    (-18.1, -40.1, 9.0, (0,)),          # W1 pinion tips
    (-18.1, -40.1, 26.0, (1,)),         # W1 wheel (z6-10)
    (-47.2, -29.5, 13.0, (2,)),         # W4 wheel (z11.5-15.5)
    (-47.2, -29.5, 3.0, (0, 1)),        # W4 lower shaft
    (12, -51, 4.5, (0, 1, 2)),          # bridge post A
    (-62.7, -2.6, 4.5, (0, 1, 2)),      # bridge post B
    (-28.0, -73.4, 7.5, (0,)),          # cock foot pad (z0-4)
    (-28.0, -73.4, 5.5, (0, 1, 2)),     # cock column
    (-72, -28, 4.0, (0, 1, 2)),         # esc platform pillar A
    (-60, -44, 4.0, (0, 1, 2)),         # esc platform pillar B
]
for az in (65.7, 185.7, 305.7):         # stand pillars, r43
    OBS.append((43 * cos(az * pi / 180), 43 * sin(az * pi / 180), 5.5, (0, 1, 2)))

def ok(x, y, tip, lvl, placed):
    if hypot(x, y) + tip > RIM - 2:
        return False
    for ox, oy, orad, lv in OBS:
        if lvl in lv and hypot(x - ox, y - oy) < tip + orad + 1.5:
            return False
    for px, py, ptip, plv in placed:
        if plv == lvl and hypot(x - px, y - py) < tip + ptip + 1.5:
            return False
    return True

def ring(cx, cy, dist, a0, a1, step=2):
    a = a0
    while a <= a1:
        yield (cx + dist * cos(a * pi / 180), cy + dist * sin(a * pi / 180), a)
        a += step

best = None
for r1 in ring(*W1, 24, 230, 330):          # R1 32t on L2 (tip 17)
    if not ok(r1[0], r1[1], 17, 2, []):
        continue
    pl1 = [(r1[0], r1[1], 17, 2), (r1[0], r1[1], 6, 1)]
    for r2 in ring(r1[0], r1[1], 17, -90, 90):   # R2 24t on L1 (tip 13)
        if not ok(r2[0], r2[1], 13, 1, pl1):
            continue
        pl2 = pl1 + [(r2[0], r2[1], 13, 1), (r2[0], r2[1], 6, 0)]
        from math import atan2
        def azu(p):
            a = atan2(p[1], p[0]) * 180 / pi % 360
            return a if a > 180 else a + 360      # unwrap CCW past 0
        for i1 in ring(r2[0], r2[1], 17, -80, 140, 3):  # idler 24t on L0
            if not ok(i1[0], i1[1], 13, 0, pl2) or azu(i1) < azu(r2) + 4:
                continue
            pl3 = pl2 + [(i1[0], i1[1], 13, 0)]
            for i2 in ring(i1[0], i1[1], 24, -60, 160, 3):  # idler 2
                if not ok(i2[0], i2[1], 13, 0, pl3) or azu(i2) < azu(i1) + 4:
                    continue
                pl3b = pl3 + [(i2[0], i2[1], 13, 0)]
                for t in ring(i2[0], i2[1], 27, -30, 170, 3):  # T 30t (tip 16)
                    if not ok(t[0], t[1], 16, 0, pl3b) or azu(t) < azu(i2) + 4:
                        continue
                    az = atan2(t[1], t[0]) * 180 / pi % 360
                    if not (15 <= az <= 110):
                        continue
                    pl4 = pl3b + [(t[0], t[1], 16, 0)]
                    for mth in range(0, 360, 6):    # M arbor 36t wheel (tip 19)
                        mx = t[0] + 24 * cos(mth * pi / 180)
                        my = t[1] + 24 * sin(mth * pi / 180)
                        if ok(mx, my, 19, 0, pl4):
                            score = abs(hypot(t[0], t[1]) - 58) + abs(az - 60) * 0.3
                            if best is None or score < best[0]:
                                best = (score, r1[:2], r2[:2], i1[:2], i2[:2],
                                        t[:2], (mx, my), az)
if best:
    _, R1, R2, I1, I2, T, M, az = best
    for name, p in (("R1", R1), ("R2", R2), ("I1", I1), ("I2", I2), ("T", T), ("M", M)):
        print(f"{name}: ({p[0]:7.2f}, {p[1]:7.2f})  r={hypot(*p):5.1f}")
    print(f"T azimuth: {az:.1f} deg  <- subdial center")
else:
    print("NO SOLUTION in searched space")
