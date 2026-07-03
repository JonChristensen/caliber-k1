# 0009 — Caliber K1 rev B: the flattening (plan of record)

Jon's Fusion review of the rev A assembly found the truth: a 2.7:1 tower
built by accretion around the M1 test fixture. Rev B rebuilds the SKELETON,
keeps the ORGANS. Approved July 3, 2026.

## Architecture (classic two-plate watch construction)

- **Mainplate** Ø170 + individual **bridges** on top: barrel bridge, train
  bridge (THE WAVE — finally visible as the movement's crown), balance
  cock (jewel over the wave tube, per the 0003 contract, now on display).
- **All wheels interleave into 2-3 gear planes** between mainplate and
  bridges. Target overall height ~24mm => 4.2mm at Ø30 metal scale (OM10
  proportions). Every milestone gets a "would this ship in metal?" review.
- **Offset barrel** (not center). **Winding from the edge**: crown-style
  stem or edge key — never through the movement's face.
- **Center wheel at center** if spring physics allows a classic train;
  otherwise document the deviation as print-era with the metal train
  designed alongside (both ratio sets tested).
- **Escapement**: Swiss lever club-tooth as the DESIGN escapement (metal
  target); pin-pallet kept as the printable fallback variant. Both from
  one parametric generator, selected by a parameter.
- **Display**: hands on the front at proper heights (no storeys), moon
  aperture in a dial sector. Module bay preserved (interface v0 carries).

## What transfers unchanged (the organs)

gears.py (cycloidal generator) - decor.py (wave, swirls, tube contract) -
tools/solve_m4.py pattern (extend into a general placement solver) -
oscillator physics + trim math - moon train (14->63|8->105) - module
interface contract - all test discipline - Milestone 1 barrel INTERNALS
(spring, arbor, ratchet, click — the drum becomes offset).

## What dies

The spider plate (test fixture, never architecture). The deck plate, dial
cock, and storey stack. Center-through winding square + knob. The M1
stand plates remain only as the historical barrel test rig.

## Execution order

1. rev-b/ layout: gear-plane assignment + solver run for the full flat
   train (barrel, center, W3, W4, escape, balance, motion works UNDER
   the dial side — the watch way).
2. Mainplate + bridges (wave bridge = train bridge, visible).
3. Escapement generator (lever variant) + balance over the wave.
4. Motion works + hands + moon module in-plane.
5. Renders reviewed in Fusion BEFORE each milestone freezes.
