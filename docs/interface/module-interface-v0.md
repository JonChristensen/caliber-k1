# Caliber K1 complication-module interface — v0 (draft)

The whole point of K1: complications bolt on without redesigning the base.
This contract is versioned; modules declare which version they target.

## Drive takeoffs (rotating outputs a module may mesh with)

| Takeoff | Period | Where | Status |
|---|---|---|---|
| Seconds | exactly 60 s | W4 arbor | live since M2 |
| Minute | exactly 3600 s | T arbor (M4) | ratios locked, geometry pending |
| Hour | exactly 43,200 s | hour wheel on T (M4) | ratios locked |
| Barrel | 1125 s | drum ring gear, 72t module 1 | live since M2 |

All takeoff gearing is module 1.0 cycloidal per `gears.py`; a module meshes
by placing its input pinion at standard center distance m*(z1+z2)/2.

## Mechanical mounting

- Fastener standard: M3, socket head, with printed hex-nut pockets.
- Module footprint: the free plate sector (azimuth ~0-130 deg, r 44-80)
  plus the airspace above the spider (z > 33 rel plate).
- Height budget: base movement tops out at z 49 (cock arm) over the wave
  only; elsewhere z 33. Modules may build to z 60.
- Every module ships as parametric build123d code + its own clearance
  tests against `train_layout()` / `m3_layout()` — CI rejects collisions.

## Power budget (to be measured on the bench)

Milestone 1's torque test defines available drive torque; a module may
load the minute takeoff by at most 10% of measured drum torque (rule of
thumb until real data lands). The haptic metronome (M6) uses its own
barrel and only takes TIMING from this interface, not power.
