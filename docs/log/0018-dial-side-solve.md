# 0018 — The dial side: four depth bands, three hard theorems, one solver

**Date:** 2026-07-04 · **Status:** movement_r2.step (36 components), 79 tests
green, dial verification fleet run before Jon's gate

The dial side got the same treatment as the massing: a whole-face model and
solver (`caliber_k1/revc_dial.py`) BEFORE any geometry, because rev C's
compactness makes the plate's underside a minefield — the drum recess floor
sits 2.2 above the dial face with its plan edge 12mm from center, the bay
allows 2.8, bushings 2.9, strap pilots 1.9. Every pocket obeys
`depth ≤ local ceiling − 0.6`, enforced by `check_dial()` forever.

## Three theorems the solve surfaced

1. **The 1:1 transfer can't be a pair.** A direct pair needs two r13+
   wheels; the cannon-side one would overhang the drum plan where only 1.6
   of depth exists. It became a 16-24-24-16 **idler chain** — every member
   deep-band legal, and the odd mesh count keeps the hands clockwise (the
   full chirality chain from the club-tooth lean to the cannon is documented
   in the module docstring).
2. **The axis theorem.** The hour pipe surrounds the cannon, so the cannon's
   gears must sit ABOVE the hour pipe's top. That forces a SHORT hour pipe
   with the moon pinion riding LOW (B2) — which also dissolved the
   motion-wheel/moon-wheel fight for the southwest plate.
3. **A two-stage moon train is impossible here.** Any wheel meshing a pinion
   at the origin lands its rim at d/(1+ratio) from center; the cannon needs
   7.8 clear, and 59.0625 split two ways forces ratio ≥ 4.2 → rim at ~4.
   (Rev B carried this collision silently — the gate caught it.) The moon is
   now THREE gentle stages: (36/24)(54/12)(70/8) = 59.0625 exactly, still
   29.53125 days, 1 day per ~122 years.

## What's in the face (frozen `DIAL_LAYOUT`, reach 64.3 of 83)

Motion works south (12:1 exact, module trick at d=24); moon train sweeping
west, disc at 10–11 o'clock with the platform window over its r13.5 orbit;
transfer chain in the western corridor. Parts: Ø3 center post + five Ø2
arbor posts (register pins), cannon, hour wheel + integral moon pinion,
motion arbor, w1, w2, moon disc (moons recessed 0.25), wheel-form idlers
(pinion-form idlers only kissed noses — proper cycloidal pairing is
wheel-drives-pinion), and the retaining platform.

## Design corrections the gates forced

- **Backlash scales with module** (0.3·m): the flat 0.3 tuned for m1 train
  teeth would eat half a m0.6 tooth.
- **Hand setting**: the chain rigidly geared the cannon to the train — no
  way to set the time. The transfer pinion now friction-grips the minute
  arbor's round stub via a slit collet (the hairspring pattern): running
  torque carries, setting torque slips. The keyless stage builds the
  setting input on top of this slip.

## Open items

- Keyless works (winding conversion from the dial-side square + setting).
- The wave pass (2f) over the now-complete movement.
- Metal-variant escapement retune (tracked skip, see 0017).
