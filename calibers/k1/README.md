# Caliber K1 — time + moon phase (rev C)

The proven base movement of the manufacture: Ø170 two-plate construction,
6h going barrel → exactly-60-min center → 60s fourth → 30s escape (1 Hz
Swiss lever), indirect minute with a slip-collet hand-setting, moon train
on the dial side, and the traced-wave skeleton bridge as the show face.

**Status: first physical build underway (July 2026).** Mainplate, wave
bridge, barrel/winding group and the train + escapement set are printed;
dry-train assembly is next. The PETG flexures (mainspring, hairspring,
click, transfer pinion, stem clip) close the build after that.

## Where things are

- [`parameters.py`](parameters.py) — every dimension in the caliber
- [`revc.py`](revc.py) — the whole-movement model: z-grammar, layout
  solver, sweeps, the check_all gate (K1's binding of `movement.solver`)
- [`revc_parts.py`](revc_parts.py) / [`revc_dial.py`](revc_dial.py) /
  [`revc_dial_parts.py`](revc_dial_parts.py) — movement side and dial side
- [`variants.py`](variants.py) — the print/metal variant switch
  (`K1_VARIANT=metal` reflows the movement)
- [`gears.py`](gears.py) — TRAIN-default binding of the shared cycloidal
  engine

## Build artifacts

- Print kit: [`exports/k1/print/`](../../exports/k1/print/MANIFEST.md)
  (regenerate: `python tools/export_print_kit.py`)
- Printing guide: [`docs/k1/printing-guide.md`](../../docs/k1/printing-guide.md)
- Review STEP: `exports/k1/revc/movement_r11.step`
  (regenerate: `python tools/build_revc_movement.py`)

Earlier generations (the rev A storey tower, the rev B flatten) live in
[`attic/`](../../attic/) — buildable, tested, superseded.
