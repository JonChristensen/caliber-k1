# 0001 — Kickoff decisions (July 2026)

## What this project is

Open-source watch movement engineering, built in public, aiming at two novel
complications: a **haptic metronome** (dedicated barrel, wrist-tap output) and
a **high-accuracy tide indication**. The path: design our own printable,
complication-ready caliber (M1) and learn by printing and testing every stage.

## Decisions and why

**CAD = build123d Python code in git, not GUI CAD.**
Precision watch geometry (cycloidal profiles, escapements, springs) is scripted
even in professional GUI workflows; code-first gives us git diffs, pytest
geometry checks, parametric tolerance iteration, and zero-cost reproducibility
for contributors. Fusion 360's official MCP is paid-tier-only and its cloud
files fight version control. FreeCAD 1.1 is the reviewer/viewer (same OCCT
kernel as build123d → lossless STEP).

**Own caliber instead of printing an existing design.**
No proven running conventional printed watch movement exists (July 2026 —
verified sweep of Printables/MakerWorld/Thingiverse). Laimer's tourbillon
(proven, CC-BY) contributes print know-how — module ≥0.7, PLA gears + PETG
springs, printed spiral springs work, pin bearings — but is architecturally a
dead end for stacking complications. OpenMovement's OM10 (CC BY-SA, STEP
behind free registration) is the architecture textbook: base movement +
bolt-on module philosophy. We copy the concept, not the geometry.

**Scale: Ø110 mm desk movement.** Watch architecture, clock size. Laimer
proved the scale runs; FDM owns it.

**Licenses:** CERN-OHL-S v2 for hardware (also required for compatibility if
we port MrBunsy's CERN-OHL-S escapement/gear code), MIT for tooling.

**Winding convention:** clockwise (viewed from dial side). Mainspring spiral
opens CCW outward; ratchet blocks CCW.

## Milestone 1 scope

Going barrel + test stand (11 printed parts, 5 M3 fasteners). Success =
measurable stored energy: wind, hold on click, release drum via lock pin,
log turns/torque/spin-down. Torque curve feeds Milestone 2 train sizing.
