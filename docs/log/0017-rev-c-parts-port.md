# 0017 — Rev C parts port: the movement gets real on the approved massing

**Date:** 2026-07-03 · **Status:** movement_r1.step exported, 73 tests green,
adversarial verification pass run before Jon's gate

Jon approved massing r3 ("This is it!"), which authorized part modeling on
`REVC_LAYOUT`. Everything proven in rev B was re-derived — not copied — onto
the rev C coordinates and z-map (`caliber_k1/revc_parts.py`).

## Three architecture facts the port surfaced

Working the z-map to part level exposed consequences the massing implied but
never spelled out:

1. **The barrel is a hanging barrel.** The 80t minute wheel at plane B
   overhangs the barrel center by 6mm (center distance 35 < wheel radius 41),
   so the barrel arbor tops out at z11 — no upper bearing, no ratchet above
   the bridge. Single plate-side journal (boss + recess floor), exactly like
   modern wristwatch practice. Winding therefore enters from the **dial
   side**: the arbor ends in a 4×4 square below the plate. The keyless stage
   builds on that square; until then it key-winds like M1.

2. **The pallet cock became the bay strap.** With the ring at z7.6 there is
   no headroom for rev B's U-cassette. The removable pallet bearing is now a
   thin strap (z6.45–7.0) spanning the recessed bay, feet screwed M2 to the
   plate *under the ring's airspace* — remove two screws, lift the fork.
   Serviceability contract preserved; banking pins moved to the bay floor
   (integral plate posts).

3. **Mesh exactness beats grid rounding.** The solver's 0.1mm coordinate
   rounding left fourth–escape 0.08 tight; escape snapped to (24.4, −40.6)
   for exact 27.0 (and escape–balance stays exactly 40.0). A permanent test
   bounds every mesh's center-distance error to (−0.02, +0.06).

## What's in movement_r1 (17 components)

Mainplate (bay recess + cups + banking pins + bushings + every screw seat),
hanging barrel (drum with integral 56t band, arbor, cover), four train
arbors (minute has the **through-bore + dial-side D-stub** — the indirect
minute interface), 30t club escape wheel, Swiss lever (variant lock/draw),
bay strap, two-tier roller, Ø3-rod balance staff, Ø52 balance, slit-collet
hairspring, balance cock (coplanar with the bridge, cabochon pocket, stud
post), and the plain broad bridge (r79, four rim pillars, cock nestled in
its dilated-silhouette cutout — the NH35 composition; the wave is sculpted
last, per 0011).

## The adversarial review earned its keep

69 agents (six lenses: kinematics, z-stack, watchmaker, test rigor,
variant switch, DFM; every finding re-verified by a skeptic) reviewed the
port BEFORE Jon saw it: 61 confirmed findings collapsing to ~20 unique
defects. The first draft's escapement was dead on arrival THREE ways —
banking pins pinched the fork (zero swing), the fork's guard-level floor
rammed the safety roller at every angle, and the impulse pin bottomed in
the notch. Also: hairspring severed in two by the collet slit, the cock's
stud post floating in air, the builder mis-phasing three meshes in the
exported STEP, and the roller carrying its pin on a bar that swept the
horn zone (real rollers are a table with the pin proud at the rim; real
horns are SHORT — anatomy corrected). All fixed; the suite gained the
gates that were structurally blind to these:

- assembled-pose interference gate over the exported movement (meshes
  phase-CHAINED via za*ta + zb*tb = const, plus 12 disjointness pairs)
- lever-vs-plate and lever-vs-roller probes over REACHABLE states only
  (draw holds the away-bank after pin exit — coupled states excluded)
- click settle/bite profile over one tooth pitch
- both-ends z-band + single-solid check for all 19 parts

New parts the review forced in: dial-side 24t ratchet + M1's flexure
click (the hanging barrel now holds wind AND is axially retained), the
bay-strap became a through-bearing (no unprintable 0.15 ceiling), and
`Variant` gained `backlash`/`press_r` fields so metal reflows the mesh
and the press fits.

## Gates

`test_revc_parts.py` (9 gates) + the standing global `check_all` gate;
75 tests green on print; metal runs 8/9 with the escapement drop-window
retune explicitly skipped-and-tracked (the 1.5/13 deg table angles from
log 0015 leave no drop with 0.12 backlash — the DFM pass must retune
lock/draw/backlash together).

## Honest flags

- Drum interior shrank with the flat stack: ~2.4 usable turns × 4h/rev ≈
  **10h runtime** (not the 18 the massing note estimated). Bench validates;
  strip 2.2×6.0 recovers rev B torque via t³.
- Keyless works, dial-side motion works (1:1 transfer + cannon), moon train:
  next stages. Dial-side pockets must avoid the bay recess plan-area
  (constraint recorded in `revc.py`).
