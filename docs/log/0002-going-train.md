# 0002 — Going train design (July 2026)

Designed ahead of Milestone 1 physical validation (deliberate: design
capital now, troubleshoot from measurements later).

## Train math

Constraint chain: 1 Hz balance → 30t escape wheel at 30 s/rev → seconds
arbor at 60 s → drum at 18.75 min/rev so that 3.2 spring turns = 60 min.
Solved with three stages: 72/16 × 50/12 × 24/12. The 60.0000 s seconds
arbor falls out exactly — integer tooth counts, no approximation.

Non-obvious inversion vs. real watches: our barrel turns FASTER than a
watch barrel (18.75 min/rev vs ~7 h/rev) because the printed spring only
yields ~3.2 turns. Minute/hour display will therefore come from a
reduction off the train in M4 (motion works), not from a 1 rev/h center
wheel. Clocks have done this for centuries; it costs two small gears.

## Decisions

- **Cycloidal teeth** (epicycloid addenda / radial-flank pinions, BS978-ish
  simplification proven by the printed-clock canon). Involute undercuts at
  12-leaf counts; cycloidal is also the horological statement.
- **Module 1.0**, backlash 0.15 tangential — chunky, printable, tunable.
- **Layout**: whole train folded into the pillar gap at azimuth 245.7°,
  clearances asserted pairwise in tests (which caught two real collisions
  during design: W4 past the rim, and the bridge band sweeping a pillar).
- **Drum = great wheel**: 72t ring gear cut into the drum's lower band.
- **Printed Ø3 pivots** for rig v1; music-wire upgrade is a parameter.
- **Tripod confession**: M1's pillar generator made 4 positions, 2 identical
  (5.7+180 == 125.7+60). Shipped plates have 3 unique holes. Fixed as an
  intentional 3-pillar design + a distinctness test.

## The wave (decor.py)

Bridge body = Chaikin-smoothed spine through its five bearing points,
offset asymmetrically: plain inboard edge, outboard edge lifted by three
gaussian swells rising to a crest, topped by a logarithmic-spiral curl.
W1 wheel got whirlpool spokes (four 70°-swept arcs).

Geometry lessons paid for this session:
1. OCCT will happily extrude a self-intersecting polygon into a solid with
   an untriangulatable skin — watch for "null triangulation" STL warnings.
   Concave-side polyline offsets fold at corners; smooth the spine first.
2. Polygon winding is load-bearing: a clockwise loop's face normal points
   -z and extrude() follows it. decor normalizes all loops to CCW.
