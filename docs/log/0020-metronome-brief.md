# 0020 — M6 brief: the haptic metronome module

**Date:** 2026-07-05 · **Status:** requirements frozen (Jon), mechanism
concept chosen; massing + solve next

## Jon's requirements

- **Tempo: 60–180 BPM, continuously adjustable** (3:1 range)
- **Beat: hammer tick + desk thump** — hear it AND feel it through the desk
- **Start/stop: chronograph-style pusher** — press to run, press to stop
- Own barrel (independent of the timekeeping train), winds like the clock

## The mechanism concept

**A variable-inertia balance.** The movement lies flat, so gravity
pendulums (Maelzel-style) are out — the oscillator must be a balance +
hairspring, which is orientation-free. The 3:1 tempo range is the hard
part: rate ∝ √(k/I), so a 3:1 rate span needs a **9:1 inertia span** —
far beyond regulator pins. The answer is horologically delicious: **two
weights sliding radially in the balance arms** (r≈5→15mm gives the ~9:1
on the dominant inertia term), driven symmetrically by a lead screw or
scroll cam through the **tempo knob**. A Gyromax taken to its logical
extreme — the tempo dial literally moves the balance's mass outward for
largo, inward for presto.

- Oscillator: 0.5–1.5 Hz (beat = 2/period = 60–180 BPM)
- Escapement: our proven club wheel + Swiss lever, module-scaled
- **Hammer**: pin wheel on the escape arbor lifts a weighted hammer that
  drops on the mainplate/base — one strike per beat, tick + thump
- **Pusher**: pen-cam (retractable-ballpoint) two-state toggle pressing a
  brake finger onto the balance rim; press-run, press-stop
- Tempo calibration: engraved BPM arc under the knob, bench-calibrated

## Reality check on space

The reserved module bay (r18 at (56,18)) holds a barrel OR the
oscillator, not both plus a hammer and pusher. Expect the module to
claim the whole eastern sector, possibly as its own **module plate**
above the bridge band (the massing will decide honestly). The module
interface (0004) still governs: the metronome must mount/dismount as a
unit.

## Next steps (massing-first, as always)

1. Station list + sweeps: m-barrel, m-train (2 wheels), variable
   balance (its sweep grows with the weights OUT), lever, hammer arc,
   pusher line, tempo knob.
2. Energy model: beat torque for an audible strike × runtime target
   (≥30 min practice session per wind? Jon to confirm).
3. Solve the module layout in/over the east sector; massing render;
   Jon's gate; then parts.
