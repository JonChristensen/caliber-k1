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

## Update (same day): position 2 SOLVED

A focused `solve_winding_link` (search the riser azimuth for a channel
clear of both drums, place the module crown wheel on the line to the
ratchet, transfer + clutch). First objective (minimize plate reach)
threaded a 70mm train up the south channel — valid but absurd. Re-aimed
at **shortest winding path**: found the NE flank, **44.5mm**, one crown
at ~2 o'clock → riser (40.9, 50.5) up the drum flank → transfer →
module crown wheel (19.9, 41.5) → module ratchet. Clean against both
plates (`k2_winding_gate`, `test_k2_winding_position2_clean`).

Key fix: the keyless cluster (clutch/setting/detent/riser) interlocks —
the 2mm inter-part rule is wrong for a coupled mechanism, so those pairs
are whitelisted (verified by the part-level probe later, like the
escapement).

**Position 1 (base) remains:** winding the base barrel from the same NE
crown needs a multi-wheel base-level train that dodges K1's SE click
(the short paths collide). Pending tier: `cw1_core`, `m_stem`,
`wind_base`, `wind_xfer_base`. Not the novel part — ordinary keyless
routing — but real, and left honest rather than faked.
