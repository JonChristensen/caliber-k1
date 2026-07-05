# Caliber K1 — FDM printing guide (Bambu Studio, H2C)

Settings for printing rev C parts from `exports/print/`. These are watch
parts: module 0.6–1.0 gears with sub-millimeter teeth and press-fit bores,
so dimensional accuracy matters more than speed. Read the calibration note
before the first real run.

## H2C quick-set (Bambu Studio)

**Nozzle: 0.4 mm — install/confirm this and keep it for the whole build.**
The smallest teeth in the movement are the module-0.6 moon-train gears
(~0.9 mm thick at the pitch line), which a 0.4 nozzle renders as ~2 clean
perimeters — proven at this scale. A 0.2 nozzle would sharpen those flanks
but roughly doubles print time and makes every part more fragile; not worth
it for a functional first build. A **standard steel** nozzle is fine —
hardened is only for abrasive (carbon/glass-filled) filament, which we
don't use. *(Later, if you want jewelry-grade dial gears, re-printing only
the moon train with a 0.2 nozzle is the upgrade — recalibrate first.)*

**Machine / plate**

| field | value |
|---|---|
| Nozzle | **0.4 mm**, standard steel |
| Build plate | **Textured PEI** — safe for both PLA and PETG (smooth PEI grips PETG hard enough to chip) |
| Flow dynamics / pressure advance | Auto-calibrate **ON** (leave Bambu's) |
| Auto bed leveling | **ON** every print — matters for the Ø170 flat parts |

**PLA** — start from the **Bambu PLA Basic** profile, then:

| field | value |
|---|---|
| Nozzle temp | 220 °C first layer / 215 °C rest |
| Bed temp | 55 °C |
| Layer height | 0.20 mm plates · 0.12 mm gears |
| Walls / top / bottom | 4 / 4 / 4 |
| Infill | 20% gyroid (plates) · 100% (gears & small parts) |
| Outer-wall speed | 50 mm/s (slow flanks = clean teeth) |
| Brim | 5 mm on the Ø170 parts |
| Supports | Organic (tree), pockets/overhangs only |

**PETG** — select the **Bambu PETG HF** profile (matches your spool) and
**leave its temps and fan as tuned by Bambu**; only change:

| field | value |
|---|---|
| Layer height | 0.12 mm |
| Walls | 4 (hairspring/mainspring are intentionally thin — see Class C) |
| Plate | Textured PEI + a glue-stick release layer |

**Before the real parts:** run Bambu Studio's built-in **flow-rate and
pressure-advance calibration** once per filament (~10 min). It's what saves
you the hairspring and gear reprints.

> Confirm the exact profile *names* and any H2C-specific fields (dual-nozzle
> / AMS options) in your own Bambu Studio — the H2C is new enough that I'd
> rather you verify the machine profile than take my word for a menu label.
> The **values** above are the targets regardless of what the profile is called.

## The one thing that will bite you: clearances are already baked in

The geometry already includes running clearance (0.20 mm on every print
pivot) and gear backlash (0.30 × module). **Do not add more.** In
particular:

- **X-Y hole/contour compensation:** leave Bambu's default *as-is* for the
  first print, then measure and calibrate. Do **not** stack your own hole
  expansion on top of the designed clearance — the bores will come out
  loose and the gears will have lash.
- Your printer's real dimensional offset is unknown until you measure. That
  is the entire point of printing the mainplate first: it is the reference.

**First-print calibration loop:** print the mainplate → with calipers,
measure against these designed values (they already include running
clearance):

- a train pivot bushing (third/fourth positions): **Ø3.0**
- the central minute through-bore: **Ø3.2**
- the barrel recess: **Ø58.0**
- plate thickness: **6.5**

FDM typically comes out with holes *slightly under* nominal (elephant-foot
and over-extrusion pull them in). If yours are consistently ~0.1–0.2 mm
small, add that as X-Y hole compensation and record it in your build log.
Only then print mating parts.

## Global settings (all parts, PLA)

| setting | value | why |
|---|---|---|
| Nozzle | 0.4 mm | 0.2 would be finer for teeth but far slower; 0.4 proven at this module |
| Layer height | **0.12 mm** gears/arbors, **0.20 mm** plate/bridge | teeth need the resolution; the big flat parts don't |
| Walls (perimeters) | **4** | small parts become nearly solid; teeth print as walls, not infill |
| Top/bottom layers | 4 / 4 | seals faces on the flat parts |
| Infill | **100%** small parts, **20% gyroid** plate & bridge | gears must be solid; the plate is stiff enough at 20% |
| Nozzle temp | 210 °C (first layer 220) | standard PLA |
| Bed temp | 55 °C | Bambu textured PEI |
| Print speed | **50 mm/s** outer walls, default elsewhere | slow outer walls = clean teeth |
| Seam | Aligned, tucked to a bore or spoke | keeps the seam off tooth flanks |

## Per-part-class profiles

**Class A — big flat plates** (`mainplate`, `bridge_DRAFT`, `dial_platform`)
- 0.20 mm layers, 20% gyroid, **brim 5 mm** (warp control on the Ø170 disc).
- Mainplate: **dial face DOWN**, tree/organic supports **in the dial
  pockets only** (not under the whole part). Bridge: **top face DOWN**.
- First layer slow (`≤ 30 mm/s`) and a clean bed — adhesion is everything
  on a part this wide.

**Class B — gears, arbors, wheels** (train arbors, escape wheel, crown
wheel, ratchet, motion/moon wheels, roller, balance wheel)
- **0.12 mm layers, 4 walls, 100% infill, 50 mm/s outer walls.**
- Arbors print **vertical** (small pivot up), **brim on** — they're tall and
  thin. Flat wheels print flat.
- Print the **spares** the manifest calls for. Small gears are cheap and
  bench tuning consumes escape wheels and forks.

**Class C — flexures & grips (PETG ONLY** — PLA creeps and snaps here)
`mainspring`, `hairspring`, `click`, `transfer_pinion`, `stem_clip`
- PETG-HF: nozzle ~250 °C, bed 70 °C, **cooling 50%** (PETG wants less than
  PLA), 0.12 mm layers.
- Hairspring is a 0.45 mm single-line wall — do a flow calibration first;
  print 3, keep the best.
- Mainspring: 100% infill, flat as-printed spiral; print 2 spares.

**Class D — register pins** (`center_post`, `arbor_post_*`, `balance_staff`)
- Printable in PLA vertical, but these are the parts to swap for **metal**:
  Ø3 and Ø2 steel rod / dowel pin cut to length. The bores are sized for a
  press fit either way. This is the cheapest "feels like a real movement"
  upgrade.

## First-print sequence (recommended)

1. **`mainplate.stl` alone** — longest print; go do other things.
   Measure it (calibration loop above) before printing anything that mates.
2. **`bridge_DRAFT.stl`** + the barrel group (`drum`, `drum_cover`,
   `barrel_arbor`, `ratchet`, `crown_wheel`, `crown_stud`) on one plate.
   Fit the bridge to the measured mainplate — check the four pillars seat
   and the stem tunnel lines up.
3. Train arbors + escapement set (with spares).
4. Balance group + dial-side gears + platform + feet.
5. PETG parts (Class C) once your PETG spool arrives.

Hold the final **wave bridge** and the **decorated balance cock** — the
decorative pass replaces those; `bridge_DRAFT` is only to prove the fit.

## Hardware (not printed — from the manifest)

M3×8 ×7 + nuts (pillars, cock, feet), M2 ×6 (strap, click, platform),
Super Lube (PTFE grease) on every pivot before assembly.
