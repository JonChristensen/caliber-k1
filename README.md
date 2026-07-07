# Caliber K1 — an open-source, 3D-printable, complication-ready watch movement

**Nobody has published a working, printable, conventional watch movement designed
as a platform for complications. This project builds one — in public.**

The movement itself is the road, not the destination. The destination is two
complications that don't exist yet in mechanical horology:

1. **A haptic metronome** — taps your wrist at an adjustable musical tempo,
   powered by its own dedicated mainspring barrel (the architecture of
   mechanical alarm watches like the Vulcain Cricket, pointed at a new job).
2. **A world-class tide indication** — going beyond every existing tide watch
   (Corum, IWC, CVDK all model a single tidal constituent) by mechanically
   summing a second constituent — the "priming and lagging" of the tides —
   plus perigean spring tides via an anomalistic-month cam.

Everything is **parametric Python ([build123d](https://github.com/gumyr/build123d))**:
the CAD is code, every dimension traces to [`caliber_k1/parameters.py`](caliber_k1/parameters.py),
every design decision is a reviewable git diff, and geometry is unit-tested
before any printer wastes plastic.

## Status

**Rev B in progress** — after a design review of the assembled rev A, the
movement is being rearchitected from a storey stack into classic two-plate
watch construction (see [log 0009](docs/log/0009-rev-b-architecture.md)).
Rev A remains fully documented below as the proving ground for every
library rev B is built from.

| Rev B step | What | Status |
|---|---|---|
| Frame | Mainplate (pocketed dial face), broad bridge, removable pallet bridge | 🟢 designed, inspection-passed |
| Dial side | Motion works + moon train in-pocket, guard platform, moon window | 🟢 designed, inspection-passed |
| Winding | Crown/stem/face-gear crown wheel, celebrated ratchet, click | 🟢 designed, inspection-passed |
| Train | 6h barrel -> exactly 60min center -> 60s fourth -> 30s escape, phase-aligned mesh proofs | 🟢 designed, probe-proven |
| Escapement | Swiss lever (variant angles), club wheel, banking/guard/crescent, steel staff, slit collet | 🟢 designed, lock+release probed |
| 2f: the wave | Bridge outline + Cotes de Geneve over the packed movement | 🔜 next |
| M5-M7 | Moon display, haptic metronome, tide | ⚪ after 2f |

Milestone 1's barrel frame is PRINTED and bench-verified; rev A remains
in-tree as the proving ground. Full review assembly:
`exports/k1/revb/review_full_movement_r13.step` (versioned; always grab
the highest r-number).

Scale: this is a desk-scale movement (Ø150 mm plate) — watch architecture at a
size FDM printing genuinely masters. Proven precedent: [Christoph Laimer's
printed tourbillon](https://www.thingiverse.com/thing:1249221) (Ø102 mm, runs).

The ocean — the tide complication's destination — lives in the frame itself:
the train bridge is a breaking wave, and the wheels spin on whirlpool spokes.

![the wave bridge](docs/images/m2-wave-bridge.png)

## Build it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/          # geometry sanity checks
.venv/bin/python -m caliber_k1.export      # writes STEP/STL/SVG to out/
.venv/bin/python tools/render_previews.py  # PNG previews of every part
```

Slice the STLs (or the STEPs directly) in Bambu Studio / your slicer of choice.
Print settings and the metal-parts shopping list are in
[docs/k1/milestones/01-going-barrel.md](docs/k1/milestones/01-going-barrel.md).

## Repository layout

- `caliber_k1/parameters.py` — every dimension in the caliber, one file
- `caliber_k1/barrel.py` — Milestone 1 parts (drum, spring, arbor, ratchet, click…)
- `caliber_k1/stand.py` — test-stand fixture
- `caliber_k1/export.py` — regenerates all output files
- `tests/` — geometry checks that run in CI before anything gets printed
- `docs/k1/milestones/` — build guides, print settings, BOMs
- `docs/log/` — the engineering log (decisions and why)

## Licensing

Two permissive licenses, chosen so anyone can build a business on this movement
without asking us or paying us.

- **Hardware designs** (everything under `caliber_k1/`, plus the generated
  STEP/STL geometry): [CERN-OHL-P v2](LICENSE), the permissive variant of CERN's
  open hardware license. You can manufacture the movement, sell it, modify it,
  and keep your modifications closed. It carries an explicit patent grant, which
  a copyright-only license like CC0 or CC BY does not, and that grant is what
  protects a functional mechanical design. No reciprocity, no share-alike, no
  obligation to credit us on the movement.
- **Tooling** (`tools/`, CI): [MIT](LICENSE-MIT).

This is a deliberately more open position than the current open watch movement,
[openmovement's OM10](https://openmovement.org/project/om10/). The OM10 is
copyleft (CC BY-SA 3.0): it requires you to engrave its calibre number on the
movement, requires your derivatives to carry the same license, and reserves the
production 2D/3D data for sale under its own purchase terms. Caliber K1 asks for
none of that. Take the geometry, put it in a product, sell the product, and you
owe us nothing.

## Follow along

Build-in-public links (site, TikTok, videos) land here as they go live.
