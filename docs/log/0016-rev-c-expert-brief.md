# 0016 — Rev C: the expert brief (end of the patch loop)

Jon's diagnosis, accepted: rev B was rebuilt by accretion under user
correction — locally-right patches, globally-wrong architecture. Rev C
is designed top-down, whole-movement-first, by the numbers below.
No part gets modeled until the layout study passes the global test.

## Hard targets (print variant / metal variant)
- Total stack **<= 28mm / <= 14mm** including cock, excluding crown.
- **Two gear planes + one escapement plane.** No arbor longer than 18mm.
- Drum **<= 35% of plate diameter** (<= O60 on O170). Recover energy by
  wider-flatter spring or accept 4-6h print runtime (bench duty).
- Barrel position becomes a FREE variable in the layout solve: if the
  drum cannot coexist with a central center wheel, use an intermediate
  transmission wheel (classic solution) or offset time display.
- Stem at PLATE level; true keyless works (winding pinion, clutch,
  setting lever, yoke) in the dial-side pocket; crown fully outside the
  plate boundary. Crown wheel + ratchet stay celebrated on the bridge.
- Oscillator: Jon's arrangement is KEPT (it converged on real watch
  practice): ring under bridge in the well, spring nested in the well
  thickness, near-coplanar cock, removable pallet bridge, steel staff,
  bushings/thrust shims per the parts register; jewels in metal variant.
- ONE broad bridge (the wave) + balance cock + pallet bridge. Nothing else.

## Process discipline (the actual fix)
1. **Global swept-volume test FIRST**: every rotating part declares its
   swept cylinder (r_tip, z-band); one test asserts all pairwise
   rotating-vs-rotating and rotating-vs-static clearances across the
   WHOLE movement. It exists before any rev C part is modeled and gates
   every commit. No more pairwise patches.
2. Layout study: solver over ALL stations simultaneously (barrel free,
   train, oscillator, keyless, motion works) against the swept-volume
   model + energy model. Deliverable: one massing STEP for Jon's gate.
3. Only after the massing gate: port parts (all generators survive).
4. Jon's role returns to taste and bench truth; whole-movement
   consistency is the designer's job — mine — enforced by the global
   test, not by his screenshots.

Rev B stays in-tree: every generator, probe, register, and lesson
carries forward. The layout does not.
