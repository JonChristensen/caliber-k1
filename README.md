# The Kelsus Manufacture — open-source, 3D-printable watch movements

**Nobody has published a working, printable, conventional watch movement designed
as a platform for complications. This project builds them — in public.**

The movements are the road, not the destination. The destination is two
complications that don't exist yet in mechanical horology:

1. **A haptic metronome** — taps your wrist at an adjustable musical tempo,
   powered by its own dedicated mainspring barrel (the architecture of
   mechanical alarm watches like the Vulcain Cricket, pointed at a new job).
   This is **Caliber K2**.
2. **A world-class tide indication** — going beyond every existing tide watch
   (Corum, IWC, CVDK all model a single tidal constituent) by mechanically
   summing a second constituent — the "priming and lagging" of the tides —
   plus perigean spring tides via an anomalistic-month cam.

Everything is **parametric Python ([build123d](https://github.com/gumyr/build123d))**:
the CAD is code, every dimension traces to a parameters file, every design
decision is a reviewable git diff, and geometry is unit-tested in CI before
any printer wastes plastic.

Like a real manufacture, this repo holds multiple calibers sharing one
engine (`movement/` — cycloidal gears, the sweep solver, the spring model):

| Caliber | What | Status |
|---|---|---|
| [**K1**](calibers/k1/) | Time + moon phase; the proven base movement | **First physical build underway** — rev C is printing; dry-train assembly next (PETG flexures to follow) |
| [**K2**](calibers/k2/) | Time + the haptic metronome | Two-sided layout frozen; winding link solved (log 0023); parts stage next |

Scale: these are desk-scale movements (Ø170 mm mainplate) — watch architecture
at a size FDM printing genuinely masters, with a metal-transferable topology
(K2's target is a 44×15 mm wristwatch case). Proven precedent: [Christoph
Laimer's printed tourbillon](https://www.thingiverse.com/thing:1249221)
(Ø102 mm, runs).

The ocean — the tide complication's destination — lives in the frame itself:
K1's train bridge is a breaking wave, and the wheels spin on whirlpool spokes.

![the wave bridge](docs/images/m2-wave-bridge.png)

## Build it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/            # the geometry gate (runs in CI)
.venv/bin/python tools/export_print_kit.py   # K1 print kit -> exports/k1/print/
.venv/bin/python tools/render_previews.py    # PNG previews of every part
```

Print from [`exports/k1/print/`](exports/k1/print/MANIFEST.md): the MANIFEST
carries per-part orientation, support maps and quantities; the
[printing guide](docs/k1/printing-guide.md) carries the bench-proven Bambu
Studio settings. Curated, support-painted Bambu plates live in
[`exports/k1/print/plates/`](exports/k1/print/plates/README.md).

## Repository layout

- `movement/` — the shared engine: cycloidal gear generator, sweep solver,
  spring energy model. Caliber-agnostic by rule.
- `calibers/k1/` — Caliber K1 rev C: parameters, layout solver, parts, dial
  side, the traced wave bridge
- `calibers/k2/` — Caliber K2: frozen brief + metal target, the two-sided
  layout, the one-crown/two-position winding link
- `attic/` — superseded generations, kept buildable and tested: the rev A
  storey tower, the rev B flatten, K2's round-plate era
- `exports/` — print kits and review STEPs, per caliber (latest per line;
  history keeps the rest)
- `docs/log/` — the engineering journal (decisions and why), one unified
  timeline across calibers; `docs/k1/` — build guides, milestones, registers
- `tests/` — the geometry gate: clearances, mesh ratios, stack heights,
  assembled poses. CI runs it on every push.
- `tools/` — exporters and massing/review builders

## Licensing

Two permissive licenses, chosen so anyone can build a business on these
movements without asking us or paying us.

- **Hardware designs** (everything under `movement/`, `calibers/`, and
  `attic/`, plus the generated STEP/STL geometry):
  [CERN-OHL-P v2](LICENSE), the permissive variant of CERN's
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
production 2D/3D data for sale under its own purchase terms. This manufacture
asks for none of that. Take the geometry, put it in a product, sell the
product, and you owe us nothing.

## Follow along

Build-in-public links (site, TikTok, videos) land here as they go live.
