# Milestone 1 — Going Barrel

**Goal:** a wound mainspring that stores real energy and releases it on command.
Wind the arbor with the key (the click holds it), pull the drum-lock pin, and
the drum spins down — pointer whirling — until the spring is slack. This
validates: printed spiral springs, printed pivots and journals, ratchet-and-click
geometry, and our print tolerances. Everything downstream (the going train)
hangs off this barrel.

## Parts to print

| Part | Qty | Material | Nozzle | Layer | Infill | Notes |
|---|---|---|---|---|---|---|
| `mainspring` | 1 (+spares) | **PETG** | 0.4 | 0.20 | 100% | The consumable. Print 2–3; creep kills them over days. No supports; print flat. |
| `drum` | 1 | PLA | 0.4 | 0.20 | 25% | Flat on floor. |
| `cover` | 1 | PLA | 0.4 | 0.20 | 25% | Tabs up (print upside-down). |
| `arbor` | 1 | **PETG** | 0.4 | 0.12 | 100% | Vertical, square up. Torque part. |
| `ratchet_wheel` | 1 | PETG | 0.4 | 0.16 | 60% | Flat. |
| `click` | 1 | **PETG** | 0.4 | 0.16 | 100% | Flexure — PETG mandatory, PLA will creep/snap. Pegs up (print upside-down, or supports under pegs). |
| `winding_key` | 1 | PETG | 0.4 | 0.20 | 40% | Socket down, no supports needed up to the handle. |
| `lock_pin` | 1 | PETG | 0.4 | 0.16 | 100% | Head up. |
| `bottom_plate`, `top_plate` | 1 ea | PLA | 0.4 | 0.20 | 25% | Flat. |
| `pillar` | 4 | PLA | 0.4 | 0.20 | 40% | Vertical. |

H2C dual-nozzle note: PLA and PETG parts can share a plate with one material
per nozzle. Keep the 0.2 mm hotend in reserve — Milestone 3 (escapement) will
want it; nothing here needs it.

## Hardware BOM (the entire metal shopping list)

| Item | Qty | Source |
|---|---|---|
| M3 × 40 socket-head cap screw | 4 | any M3 assortment kit / McMaster 91290A130 |
| M3 × 8 socket-head cap screw | 1 | (click mount) |
| M3 hex nut | 5 | |

That's it — by design. Milestone 2 adds steel pins for train arbors.

## Assembly

1. Ream the plate bushings (Ø8.4) and drum/cover bores (Ø10.4) with a drill
   bit spun by hand until the arbor turns freely. This step is 80% of success.
2. Spring into drum: outer tab through the wall slot, D-ring over the arbor
   hub (flat to flat), coils sitting free of floor and walls.
3. Cover on, tabs into the drum rim notches.
4. Barrel cartridge between the plates; bolt the stand together (M3×40).
5. Ratchet wheel onto the winding square; click over its pegs, M3 + nut snug.
6. Key on. **Wind clockwise.** The click should snick past each tooth.

## The test (film this)

1. Lock-pin in (through top plate into cover): drum can't turn.
2. Wind 3 full key-turns clockwise. Click holds the arbor between strokes.
3. Pull the pin. Drum spins down — count pointer revolutions and time it.
4. Torque measurement: wrap thread around the drum rim, hang a small weight
   (start ~100 g), wind one turn, and find the weight the spring just lifts.
   Torque ≈ weight × 0.036 m. Log wound-turns vs. torque — that curve sizes
   the going train in Milestone 2.

## Tuning knobs (expect to iterate)

- Spring too weak / too strong → `Mainspring.thickness` (1.6) or `.height` (16).
- Arbor binds → `Tolerances.pivot_clearance` (0.20) up by 0.05.
- Click skips under load → thicken `click_arm_t` / deepen tooth engagement.
- Spring coils fuse while printing → raise coil count spacing: fewer `coils`.

Every change is one line in `parameters.py`; re-run the export, reprint only
the affected part.
