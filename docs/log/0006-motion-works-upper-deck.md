# 0006 — Motion works: the upper-deck solution

The placement solver (tools/solve_m4.py) proved option B's ground-floor
walk IMPOSSIBLE: at z0-16 the annulus r51.5-68 is corked at every azimuth
(foot_a az283, stand pillar az305.7, foot_b az182, cock/escapement
az200-260). No idler chain of any length fits. Negative result, exhaustive.

## The solution: climb, then walk (hybrid of options A and B)

- R1 (32t, L2 z10.5-15.5) meshes W1's second pinion at the VERIFIED spot
  (-9.9, -62.65): r63.4 — outside the spider disc (r50), beside the
  bridge band (18.4mm > 14 needed), clear of the cock column (21mm).
- R1's 10-leaf pinion rides a TALL shaft up to z27-32 — climbing past
  the bridge level in open air.
- Above z28 the ENTIRE plate is open except: cock column (az249 r78.5),
  winding click (r~34, z28.3-33.3), ratchet (r20), balance ring (r25
  about az229, z35+), escapement platform (az200-250, z31-34), key sweep
  (z38+ center). The az 300 -> 110 fairway is completely clear.
- R2 (24t wheel z28-33, 10-leaf pinion above) -> T (30t) lands in the
  open sector az~60 at r~55; 12:1 motion works + friction cannon + hands
  stack above; subdial ring prints as part of a small "dial cock" bridged
  off the spider rim + one plate pillar.
- Ratios unchanged: (32/16)(24/10)(30/10) = 14.4 exact; MOTION dataclass
  needs amending from the committed 2-stage to this 3-stage (same test).

The time literally rises out of the movement and floats on the top deck,
wave on the left, dial on the right — regulator layout in 3 storeys.
Next session: model r1/r2/t arbors, dial cock, hands, friction cannon;
solver extends trivially for the upper deck if placement needs tuning.
