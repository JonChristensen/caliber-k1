# 0005 — Motion works packaging: the constraint map

Placing R/T/M arbors is the tightest packaging problem in K1. Verified
no-go results (each caught by clearance math before printing anything):

1. Ø48 R-wheel at deck level (z0.5-5.5, meshing W1's pinion): needs
   |R| >= 63.5 (drum) but <= 58 (rim). Contradiction — impossible.
2. Ø72 T-wheel anywhere: below z22.3 blocked by drum (needs |T|>=75.5),
   z22.8-27.8 blocked by spider disc, z28-33 blocked by ratchet sweep
   (needs |T|>=58.5 but rim caps at 46). No legal storey exists.
3. Three-stage 2 x 2.4 x 3 chain (32/16 -> 24/10 -> 30/10 = 14.4): R1 at
   (-9.9,-62.7) z10.5-15.5 works (clears cock foot via z, foot_a by 2.3mm),
   but R2 at z16-21 fouls either the drum annulus (<51.5) or the wave
   bridge band near W1. Restacking R2 lower collides with W1's own wheel.

## The open z-storeys (rel. plate top)
- z0.5-16.5: outboard annulus r51.5..(83-tip) only — narrow but real
- z >= 33.5, r <= 37.5: above ratchet, inside spider footprint — OPEN
  and unused. Candidate: run the time display UPWARD at the center —
  a "mystery-dial" storey above the ratchet, driven by a tall lateral
  idler from R1's level through the spider's window gaps (the spider is
  3 spokes; its windows are open shafts from z22.8 up).
- The 65.7-azimuth third of the plate is empty at ALL levels below 22
  outside r44 — but unreachable in one 24mm hop from W1; needs an idler.

Next session: solve with either (a) the center mystery-dial storey via a
spider-window idler, or (b) two idlers marching az 245 -> 65 around the
rim annulus at z10.5-15.5. Ratios stay as committed (14.4 x 12 exact).
