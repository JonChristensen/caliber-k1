# 0019 — The ratchet comes home: Jon's NH35 catch re-solves the movement

**Date:** 2026-07-04 · **Status:** massing_r4 + movement_r3 exported, 80
tests green, verification-fleet findings applied

Jon flagged the dial-side ratchet poking into the dial's airspace and held
up the NH35: the ratchet belongs on the MOVEMENT side. He was right, and
the diagnosis went deep: the dial-side winding was a patch on a patch —
the 80t minute wheel overhung the barrel center, which decapitated the
barrel arbor at z11, which forced the hanging barrel, which forced
dial-side winding.

## The root fix: new tooth counts

`(60, 10, 56, 7, 45, 6, 36, 18)` — worked out under four simultaneous
constraints (all now encoded in the solver's menu comment):

- minute wheel ≤ r29 so the **barrel arbor column** (a new permanent
  sweep the global gate protects) rises past plane B to the bridge;
- minute PINION small enough that it clears the coplanar third wheel —
  which forced the drum to 60t/10-leaf = **6h per turn**, and the bigger
  drum holds more spring: runtime IMPROVES to **~17h** (from ~10);
- the barrel stands off at y ≥ 40 (a dial-side reservation: the moon
  pinion's pocket needs 10.7 of drum-free plan at the origin);
- (56/7)(45/6) = 60.000 — timekeeping exact, as always.

## What the architecture becomes

- **Two-bearing barrel**: plate cup below, bridge-web bearing above. The
  hanging-barrel wobble flag from 0017 dies.
- **Ratchet + click recessed FLUSH in the bridge top** (the NH35
  composition), click pegs through the bridge web, winding by key into a
  **female square socket** — nothing stands above z17.7.
- **The dial face is completely untouched** — no bore, no boss, no pegs.
  The dial sheet reservation is now a constant (`DIAL_SHEET`).
- Transfer chain slimmed to 10-24-24-10 (the pinion pocket must fit
  between the minute arbor and the drum recess — 0.8mm of margin).

Both solvers re-ran (bridge 70s, dial <1s after teaching the i2 ring to
walk at 1/3 step — its legal windows are ~7° wide). Same-day fleet
findings folded in: feature-aware post bores (the disc post would have
breached the bay floor — posts are now IN the gate), posts extended to
z-0.7 as platform supports/locators (dial-feet analog), cannon/hour pipe
walls thickened, the transfer collet got a doubled flexure hub, press
bores derive from `Variant.press_r`, and a platform-coverage retention
test. Interim hand-setting: push the minute hand; the transfer collet
slips (the keyless stage adds the proper setting path).

## For Jon's gate

`exports/revc/massing_r4.step` (composition moved: train now sweeps the
WEST side, balance at ~5 o'clock, moon window lands near 6) and
`exports/revc/movement_r3.step` (36 components). The stack still tops at
17.7; the dial side is clean glass.
