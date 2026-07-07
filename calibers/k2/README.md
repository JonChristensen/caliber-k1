# Caliber K2 — time + the haptic metronome

A TWO-BARREL caliber: K1's proven time core as the base, plus the
metronome as its complication — 60–180 BPM continuous (variable-inertia
balance with sliding weights), hammer tick + desk thump, chronograph
pen-cam pusher, its own barrel with a ≥30-min-at-180 beat budget.
The frozen brief is [log 0020](../../docs/log/0020-metronome-brief.md).

**Architecture of record: TWO-SIDED** (Jon's call, July 5 2026 — the
chronograph-module pattern). Base time movement on one plate, metronome
module stacked toward the caseback on its own full-diameter plate, both
Ø166. One crown, two positions: push winds the base, pull winds the
module through a riser + cross-plate transfer
([log 0023](../../docs/log/0023-k2-winding-link.md), SOLVED).

**The metal target governs**: K2 must eventually drop into a ~44×15 mm
wristwatch case (Ø40×10 movement). The print and the metal are one
topology at two scales.

## Where things are

- [`brief.py`](brief.py) — the frozen brief, metal target, energy
  budget, tooth counts
- [`layout.py`](layout.py) — the two-sided layout, module solve, Jon's
  full-cast inventory, K2's mesh-pair registry
- [`winding.py`](winding.py) — one crown / two positions: sweeps, solver,
  and the cross-plate gate

Massing artifact: `exports/k2/two_sided_r2.step`
(regenerate: `python tools/k2_two_sided_massing.py`).

**Status:** massing at Jon's gate; parts stage next. The superseded
one-plate interleave (massing r1–r5) is in
[`attic/k2_round_plate.py`](../../attic/k2_round_plate.py).
