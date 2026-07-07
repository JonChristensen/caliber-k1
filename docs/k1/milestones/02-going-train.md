# Milestone 2 — Going Train

**Goal:** the wound barrel drives a three-stage gear train instead of
free-spinning. Pull the lock pin and the whole train blurs; the W4 arbor —
the future seconds hand — turns at exactly 1 rev/60 s ratio to the drum.
This validates cycloidal gear meshing, printed pivots, depthing, and the
layout that Milestone 3's escapement will regulate.

![wave bridge](../images/m2-wave-bridge.png)

## The timing chain (all ratios exact)

| Stage | Drives | Ratio | Period |
|---|---|---|---|
| Drum, 72t ring gear | W1 pinion, 16 leaves | 4.5 | drum: 18.75 min/rev |
| W1 wheel, 50t | W4 pinion, 12 leaves | 4.1667 | W1: 250 s |
| W4 wheel, 24t | escape pinion, 12 leaves | 2.0 | **W4: 60.0000 s** |
| — | — | — | escape: 30 s (→ 30t wheel @ 1 Hz in M3) |

3.2 usable spring turns × 18.75 min/rev = **60 min design runtime**.
Teeth are **cycloidal** (epicycloid wheel addenda, radial-flank pinions) —
the horologically correct form for low-count pinions, generated in
[gears.py](../../caliber_k1/gears.py).

## The ocean, in the frame

- The **train bridge is a breaking wave**: three swells build along its
  outboard edge to a crest that curls over in a logarithmic spiral. It
  carries all three upper pivots and seats on two integral posts.
- The **W1 wheel's spokes are a whirlpool** — four arcs sweeping 70° from
  hub to rim. Both live in [decor.py](../../caliber_k1/decor.py) and will
  carry through the rest of the caliber.

## Parts to print

| Part | Material | Nozzle | Layer | Infill | Notes |
|---|---|---|---|---|---|
| `rig_plate` | PLA | 0.4 | 0.20 | 25% | Ø150. Replaces M1 bottom_plate. Posts print up. |
| `drum` (reprint) | PLA | 0.4 | 0.20 | 25% | Now carries the 72t ring gear. Everything else in the barrel is unchanged. |
| `wave_bridge` | PLA | 0.4 | 0.16 | 40% | Flat; the star of the show — print it clean. |
| `w1_arbor` | **regular PETG** | 0.4 | 0.12 | 100% | Vertical, pivot down, with a brim. Wheel is a large overhang — see below. |
| `w4_arbor` | **regular PETG** | 0.4 | 0.12 | 100% | Vertical + brim. |
| `esc_arbor` | **regular PETG** | 0.4 | 0.12 | 100% | Vertical + brim. |

**Arbor overhang note:** wheels sit partway up their arbors, so each wheel's
underside is a large flat overhang. Print arbors with **supports enabled
(snug, from build plate only)** and peel them from the wheel underside — or
slice with a 0.2 nozzle at 0.10 for crisper teeth if patience allows.
Expect to ream the plate/bridge bushings (3.4 mm → 3.5 mm drill twisted by
hand) and polish the printed pivots with fine sandpaper.

**Hardware: none new.** Same 3× M3×40 stand bolts. (Milestone 1's plates
had only three unique pillar positions — a v1 bug now embraced as a tripod;
the fourth printed pillar is a spare.)

## The test (film this)

1. Assemble: rig plate → train arbors into their bushings → barrel cartridge
   between plates as in M1 → wave bridge onto its posts over the train.
2. Check free running BEFORE the spring: every arbor should spin from a
   breath of air. If not, find the tight pivot and ream/polish.
3. Wind 1 turn with the lock pin in. Pull the pin.
4. **Count:** mark the W4 arbor; the drum should make exactly 3 revolutions
   while W4 makes 56.25 (i.e., in ratio 18.75:1). Any slip/skip = mesh problem.
5. Time the spin-down from a full 3-turn wind. Unregulated, it will run down
   in seconds — that's expected. The number feeds M3's escapement design:
   60 min runtime ÷ spin-down seconds ≈ the braking factor the escapement
   must provide.

## Tuning knobs

- Teeth bind / feel gritty → raise `Train.backlash` (0.15 → 0.20) and reprint
  the smaller part of the offending pair.
- Teeth skip under load → deepen mesh: lower backlash, or check arbor bushings
  for slop (`pivot_clearance`).
- Arbors rattle → drop `Train.pivot_d` clearance in `Tolerances`.
- Wave not dramatic enough on camera → `decor.wave_bridge_face` exposes
  `half_w`, `crest_at`, `curl_r`, and the swell table. Iterate freely; the
  bridge is a 20-minute print.
