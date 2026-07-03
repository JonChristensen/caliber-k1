# Milestone 3 — Escapement + Balance ("it ticks")

A pin-pallet (Roskopf) lever escapement — chosen over the club-tooth Swiss
lever because cylindrical pins + pointed teeth tolerate FDM error — driving
a Ø50 balance at 1 Hz on a printed PLA hairspring. Predicted period 1.037 s;
trim with M3 nuts in the 6 balance-rim holes (add nuts = slower, ~3%/nut).

The balance jewel — a real 4 mm red glass cabochon, working as a cap jewel —
sits on the balance cock dead over the tube of the breaking wave.

## Parts to print

| Part | Material | Nozzle | Notes |
|---|---|---|---|
| `escape_wheel` | PLA | 0.2 | teeth are the precision feature |
| `pallet_lever` | PETG (regular) | 0.2 | prints on its back, pins up; the flexing... it doesn't flex, but pins take impact |
| `roller`, `balance_staff` | PETG | 0.2/0.4 | staff prints vertical |
| `balance_wheel` | PLA | 0.4 | 100% infill — inertia is the point |
| `hairspring` (+2 spares) | **PLA only** | 0.4 | 0.45mm walls; rate depends on E of PLA; no combing/wipe |
| `tube_chaton` | PLA | 0.4 | glue 4mm cabochon later — it caps the COCK, not this |
| `platform`, `balance_cock` | PLA | 0.4 | cock prints lying on its side |
| `rig_plate` v3, `wave_bridge` v3, `esc_arbor` v2 | PLA/PETG | 0.4 | reprints (Ø170 plate, pallet pad, wheel seat) |

## Hardware added this milestone

- 2× M3×12 + nuts (balance cock foot)
- 1× 4mm red glass cabochon (craft store / Etsy, ~$3) — glued into the
  cock's top pocket; its underside is the balance's upper end-stone
- Optional: 2× Ø2×6mm steel dowel pins to replace printed pallet pins

## Expected bench-tuning (this is v0.1 of a hard mechanism)

1. Escapement lock/drop: tune `Escapement.engage` (1.6) in ±0.2 steps and
   reprint the lever — 15 min print.
2. Beat: rotate the hairspring collet on its D-flat to center the impulse
   pin between the banking posts at rest.
3. Rate: nuts in rim holes; big steps via `Balance.hs_t` (t³ leverage).
4. Overbanking (no guard pin in v0.1): if the fork jumps the roller on
   knocks, print the guard-pin lever variant (planned v0.2).
