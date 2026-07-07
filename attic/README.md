# The attic — superseded generations, kept buildable

Nothing in here is print-worthy; nothing in here is deletable. These are
the designs the current calibers were carved from, kept importable and
covered by the test suite so the record stays executable.

- **`reva/`** — K1's milestone-era storey tower (M1 going barrel → M5
  moon phase). Designed, probed, never printed as a whole: Jon's Fusion
  review flattened it into two-plate watch construction
  ([log 0009](../docs/log/0009-rev-b-architecture.md)). Its barrel frame
  (M1) WAS printed and bench-verified — the manufacture's first plastic.
- **`revb/`** — the first two-plate flatten. Every rev C part was ported
  from here ([log 0017](../docs/log/0017-rev-c-parts-port.md)); the
  print/metal variant switch it introduced now lives in
  `calibers/k1/variants.py`.
- **`k2_round_plate.py`** — K2's one-plate era: clock + metronome
  interleaved on a single round plate (massing r1–r5). The two-sided
  call ([log 0022](../docs/log/0022-k2-two-sided.md)) dissolved it.
- **`tools/`** — their exporters and mockups. `k2_massing.py` is
  stale-broken (r5-era globals) and kept only as the record of how
  `exports/k2/massing_r5.step` was made.

Old review STEPs were pruned from `exports/` (latest kept per line);
every pruned revision is in git history.
