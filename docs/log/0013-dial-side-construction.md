# 0013 — Dial-side construction corrected (Jon's 2824/NH35 anatomy check)

2e as first committed floated the motion works in 7.4mm of open air
under the plate. Real construction (Jon's correction, confirmed):

- Motion + moon works sit in SHALLOW RECESSES pocketed into the plate's
  dial face; wheels are thin; axial confinement comes from recess floors
  plus a retaining platform (the date-platform analog — ours doubles as
  the moon guard). Only the hour wheel stands proud (2824-style), kept
  honest by a dial-washer analog (printed wave washer).
- Target dial-side protrusion beyond the plate face: <= 2mm print,
  ~0.8mm metal — variant tables, heights derived.
- Mainplate thickens (4 -> ~6.5) to host pockets below and bushings
  above; every assembly z that assumed plate_t=4 must derive from a
  single PLATE_T constant during the rework (they are hardcoded today —
  that is the real cost of this fix, and worth paying once).
- Optional later: dial-side windowing for a skeleton dial.

Sequence: 2e-r (this rework) -> 2e-half (rev B train/escapement part
ports) -> 2f (bridge beauty pass). Marked as the next session's opener.
