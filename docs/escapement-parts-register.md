# Escapement & balance parts register (after ciechanow.ski/mechanical-watch)

Jon's reference: Bartosz Ciechanowski's "Mechanical Watch". Full analysis
in the research transcript; this register maps every part to K1 status
and variant assignment. Print scale is ~5x: lock depth ~1.2mm vs FDM
error +-0.15 — THE reason 5x works where 1x FDM cannot.

| Part | K1 status | print variant | metal variant |
|---|---|---|---|
| Escape wheel (club) | BUILT, probed | printed | steel, watch angles |
| Pallet fork body | BUILT, probed | printed | steel |
| Pallet stones | BUILT (integral faces) | integral, polished; upgrade: slotted acetal stones = adjustable lock | ruby/insert pockets (DFM) |
| Guard element | BUILT (floor finger) | printed; upgrade: pressed wire pin (bendable tuning) | steel dart |
| Fork horns + slot | BUILT (two-level) | printed | steel |
| Banking | BUILT (bridge pins) — essay's movement banks on bridge knobs too | printed pins; upgrade: M3 brass grub screws = master adjustment | eccentric pins |
| Pallet bridge | BUILT (removable, 2x M3) | printed | milled |
| Impulse pin | BUILT (printed, on roller) | UPGRADE: steel/brass dowel, one flat filed (the D matters) | jewel |
| Two-tier roller + crescent | BUILT | printed one-piece (essay's double roller) | steel |
| Balance staff | BUILT printed — TO CHANGE | **steel rod (non-negotiable — amplitude lives on pivot friction)** | turned steel |
| Balance bearings / end stones | printed bushings — TO CHANGE | brass/PTFE bushings or MR52 + polished shim thrust | hole jewels + cap jewels |
| Shock protection | absent | omit (steel staff at desk scale doesn't need it); great content later | Incabloc-style (DFM) |
| Hairspring | BUILT printed PLA | printed (Laimer precedent; creep = recalibration story) | Nivarox-class, sourced |
| Collet | BUILT solid — TO CHANGE | slit it: friction-rotatable = BEAT ADJUSTMENT (audible in a metronome!) | split steel |
| Stud / regulator / curb pins | absent | printed arm + wire curb pins + eccentric-screw fine adjust (essay's design) | conventional |

## System notes adopted
- Train torque starvation is a FEATURE (anti-rebanking) — size the spring
  to minimum healthy amplitude.
- 5x printed balance lands 0.5-2 Hz naturally — metronome territory;
  a gift for the M6 haptic complication.
- Print-variant metal shortlist (the honest BOM): steel staff rod,
  impulse dowel pin, guard/curb wire, balance bushings + thrust shims.

Queued geometry changes: steel-staff adapter hubs, slit collet,
regulator assembly, grub-screw banking bosses.
