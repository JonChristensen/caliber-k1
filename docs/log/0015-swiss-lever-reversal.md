# 0015 — The Swiss lever reversal (Jon's AliExpress evidence)

Jon gently pushed back on "a Swiss lever can't print": his AliExpress
tourbillon visibly has a pallet fork. Verified — he is right:

- Laimer (thing:1249221, our scale ancestor): "The watch has a Swiss
  lever escapement." Anchor 100% printed PLA (0.06mm layers, 80% infill),
  no jewels, runs at Ø100mm — smaller than K1.
- The Mechanica clone family (Jon's unit): printed "Escape Fork" with
  named left/right pallets; runs; known overbanking mode fixed by longer
  fork horns (designer ships a tuning variant + STP).
- Design rules (Headrick/abbeyclock, NAWCC, funprints4u): LOCK 2-3 deg
  for print (+-0.15mm error ~ 1 deg of lock at Ø32 wheel; watch practice
  1-2 deg eaten entirely by print error), DRAW textbook 12-15 deg (no
  more — unlocking losses), flat faces, generous horns, banking pins.

## Decision

Escapement PARITY: swiss_lever in BOTH variants — angles per variant
(print: lock 3.0/draw 15.0; metal: 1.5/13.0). Pin-pallet demoted to
fallback (code retained). The print bench now rehearses the metal
escapement's architecture — the variant switch fulfilling its purpose.
Next build session: parametric lever generator (lock/draw/lift from the
variant), club-tooth escape wheel pair, fork horns sized per the
Mechanica overbanking lesson, phase-aligned probe like the train's.

Full sources in the research transcript; key: makezine tourbillon
tutorial, thingiverse 1249221, myminifactory Mechanica guide,
abbeyclock lever construction.
