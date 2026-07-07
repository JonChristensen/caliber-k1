# Caliber K1 rev C — print kit (movement r6)

## Hardware (not printed)

- **M3 + nuts** (hex nuts drop into dial-side pockets, 2.4 deep): **M3×18 ×6**
  (bridge pillars ×4, cock feet ×2 — stack is 17.7 minus the pocket) and
  **M3×20 ×3** (stand feet — plate 6.5 + foot 14). *An earlier note said
  M3×8 ×7 — that was wrong; ×8 doesn't reach any nut in this stack.*
- **M2 self-tap ×6** (bay strap ×2, click ×1, dial platform ×3).
- Super Lube (PTFE grease) on every pivot at assembly.

## Print profiles (Bambu Studio; 0.4 nozzle, textured PEI)

| class | parts | settings |
|---|---|---|
| **A** — big flats | mainplate, bridge_wave, dial_platform, dial_sheet | 0.20 layers, 20% gyroid (bridge_wave 100%), walls 4/4/4, brim 5 |
| **B** — gears, arbors, small | everything not listed elsewhere | 0.12 layers, 4 walls, **100% infill**, outer wall 50 mm/s, first layer 220°/rest 215°, bed 55° |
| **C** — flexures | mainspring, hairspring, click, transfer_pinion, stem_clip | **PETG** (Bambu PETG HF profile), 0.12 layers, 4 walls |
| **D** — register pins | center_post, arbor_post_*, balance_staff | PLA vertical, or swap for Ø3/Ø2 steel rod (press-fit either way) |

**Supports — the anti-scar recipe (learned the hard way on the first arbor batch):**
Tree (**manual**), painted ONLY where a row below says so. Top Z distance **0.2**,
top interface layers **2**, top interface **spacing 0.4–0.5** (a dense 0.2 interface
WELDS to the part), support/object XY distance **0.4**, on build plate only.
Never support a ring hovering ≤1 mm above the disc below it — no room to remove;
the sag self-heals. Cup-shaped parts print closed-face DOWN so the interior
needs no support at all.

**Brim:** type *Outer brim only*, width 5, gap 0.1 — on every vertical part and
the Class A flats. **Elephant-foot compensation ≥0.15** on; deburr and dry-fit
every plate-end pivot in its bushing before assembly (0.2 mm running clearance
is the whole budget).

## Parts

| part | qty | cls | orientation / supports |
|---|---|---|---|
| mainplate | 1 | A | dial face DOWN; tree supports in the dial pockets only. **Measure it before printing mates:** bushing Ø3.0, center bore Ø3.2, barrel recess Ø58.0, thickness 6.5 → set X-Y hole comp to the shortfall |
| drum | 1 | B | **floor DOWN, cup mouth UP** — the interior (where the spring rides) prints clean with zero support; auto-tree ≥50° catches the outside gear-band ledge + 3 cover lugs. *(Band-down buries the interior in support — don't.)* |
| drum_cover | 1 | B | flat, either face |
| barrel_arbor | 1 | B | vertical, square end UP; brim |
| mainspring | 1 | C | **PETG ONLY** — flat spiral as printed, 100% infill; print 2 spares |
| ratchet | 1 | B | flat |
| click | 1 | C | PETG preferred (PLA short-term OK); flat, pegs UP |
| crown_wheel | 1 | B | slots UP (top face down) |
| crown_stud | 1 | B | head DOWN |
| stem_and_crown | 1 | B | crown face DOWN, axis vertical; paint supports under the pinion |
| stem_clip | 1 | C | PETG preferred; flat; print 3 |
| minute_arbor | 2 | B | vertical, **long dial stub DOWN** (its tip is the one non-bearing end — it eats the elephant foot); brim. Paint under the 14t pinion + under the 80t wheel *outside the pinion's footprint*; skip the ring directly over the pinion |
| third_arbor | 2 | B | vertical, long lower pivot DOWN (48t wheel low, 8t pinion up top); brim. Paint the full annulus under the 48t wheel only |
| fourth_arbor | 2 | B | vertical, long pivot DOWN; brim. Paint under the 8t pinion + under the 36t wheel outside the pinion footprint |
| escape_arbor | 2 | B | vertical, bay pivot DOWN; brim. Paint under the 18t pinion — the trees double as bracing for the tall post |
| escape_wheel | 3 | B | flat (bench tuning consumes them) |
| pallet_fork | 3 | B | body flat, **long (2.0) pivot DOWN** — the body hovers 2 mm on the pivot tip. Paint the ENTIRE body underside; never the pivot. Peel supports away from the pivot, holding the body |
| bay_strap | 2 | B | flat |
| roller | 2 | B | flat, crescent side down |
| balance_staff | 1 | D | vertical; or cut from Ø3 steel rod |
| balance_wheel | 1 | B | flat |
| hairspring | 1 | C | **PETG ONLY** — flat; 0.45 walls = single-line: tune flow first; print 3 spares |
| balance_cock | 1 | B | arm flat, columns UP; paint supports under the stud post |
| stand_foot | 3 | B | vertical |
| center_post | 1 | D | vertical; or Ø3 steel rod |
| cannon | 1 | B | pipe vertical, hand-seat UP |
| hour_wheel | 1 | B | pipe vertical |
| motion_arbor | 1 | B | vertical |
| moon_w1 | 1 | B | flat |
| moon_w2 | 1 | B | vertical shaft |
| moon_disc | 1 | B | moons DOWN (two-color swap at 0.3 if using AMS) |
| transfer_pinion | 1 | C | PETG preferred; flat; slit collet is the hand-setting slip; print 2 |
| transfer_idler | 2 | B | flat |
| dial_platform | 1 | A | flat, proud face down |
| dial_sheet | 1 | A | face color! face DOWN; engraved markers paint-fill at the bench |
| minute_hand | 2 | B | hand color; flat |
| hour_hand | 2 | B | hand color; flat |
| bridge_wave | 1 | A | show face — pick a color! SHOW FACE DOWN (pillars up); 100% infill; supports only in the ratchet pocket + stem tunnel; brim |
| arbor_post_motion | 1 | D | vertical; or Ø2 steel pin |
| arbor_post_w1 | 1 | D | vertical; or Ø2 steel pin |
| arbor_post_w2 | 1 | D | vertical; or Ø2 steel pin |
| arbor_post_disc | 1 | D | vertical; or Ø2 steel pin |
| arbor_post_i1 | 1 | D | vertical; or Ø2 steel pin |
| arbor_post_i2 | 1 | D | vertical; or Ø2 steel pin |
