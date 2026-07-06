# 0023 — K2 winding link: one crown, two positions across two plates

**Date:** 2026-07-05 · **Status:** open design problem, scoped

Two-sided K2 (log 0022) leaves one real sub-design: how one crown winds
**both** barrels when they sit on different plates. Position 1 (push)
winds the base barrel via K1's existing winding — reused, done. Position
2 (pull) must wind the **module** barrel, and that's the hard part.

## The constraint the gate surfaced

The module barrel is big (76t, r38) and central, so its ratchet sits at
the module-plate **center**, at bridge z (~34–36). Reaching it from a
base-level north crown is NOT a straight shot:

1. stem enters the north rim at base level (z~13)
2. a **vertical riser** climbs ~22mm to module-bridge level — and must
   clear both drums (r38), so it rides the **flank** of the module drum
   (there's only 9mm north of the drum, but 48mm+ to the sides/south)
3. a **horizontal transfer wheel** at module-bridge level runs inward
4. → the module crown wheel → the module ratchet

Plus the shared clutch + setting lever + detent that select position 1
vs 2. First naive hand-placement collided (riser through the drum, clutch
crammed north) — a clear sign this needs its own solve, not patching.

## Plan

A small dedicated solver for the winding link: riser azimuth free around
the drum flank, transfer-wheel placement gated against the module train,
clutch works spaced along the stem. Reserved coarsely now
(`winding_link_zone`) so the massing shows the space; geometry at the
solve. Everything else on the module plate is gated clean.
