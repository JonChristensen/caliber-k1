# 0022 — K2 goes two-sided: the plate stops growing

**Date:** 2026-07-05 · **Decision:** Jon — "two-sided metal module."

Jon chose the chronograph-module architecture: base time movement +
metronome MODULE stacked toward the caseback, not side-by-side on one
plate. This **dissolves the O250 frankenplate problem** — the two
movements no longer compete for one plane, so each gets its own
full-diameter plate. K2's plate returns to **Ø166 (same as K1)**.

## The stack (front → back)

crystal · dial + hands · motion works · **base plate** · base going
train + escapement + balance + base bridge · **module plate** ·
metronome works + hammer + variable-inertia balance · module bridge ·
display-back crystal.

- **BASE** = K1's proven time core (revc) verbatim, minus the moon train.
  No re-solve — it's K1.
- **MODULE** = the metronome ALONE on its own Ø166 plate. Solved
  (`solve_module_alone`, 123s) to reach 63.8 of 83 — 19 mm of margin, a
  roomy single-cluster layout like K1's clock, not a desperate interleave.
- One crown, two positions winds the two barrels (push = base, pull =
  module).

## Numbers

Print: Ø166 × ~36 mm (two movements stacked — a tall desk model, fine).
Metal: Ø40 × ~6 mm scaled, but the z-table is variant-tall → fits the
~10 mm case budget with room. The metronome, its balance and hammer,
show through the sapphire display back.

## Status

`k2_module_gate` CLEAN; the full inventory (log 0021) rides the module
plate. Next: the base↔module winding link (one crown, two positions),
the module-plate pillars down to the base, and Jon's massing gate on the
two-sided stack. Then K2 parts — the variable-inertia balance and hammer
first (the two mechanisms K1 doesn't already prove).
