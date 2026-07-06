"""K2 two-sided massing r1 — the first real sandwich artifact.

Front (dial) -> back (caseback):
  base dial/hands · BASE PLATE · base time works + base bridge ·
  MODULE PLATE · metronome works + module bridge.
Both plates O166 (same as K1); the metronome shows through the caseback.
Collisions on each plate are proven by their own gates (K1 + module).
"""
from math import cos, sin, radians

from build123d import Align, Compound, Cylinder, Pos, export_step

from caliber_k1.revc import revc_sweeps, PLATE_T, REVC_LAYOUT
from caliber_k2.movement import (module_sweeps, winding_link_zone, K2_MODULE,
                                 K2_PLATE, MODULE_PLATE_Z, MMZ, K2_COUNTS,
                                 OUTSIDE_OK)

B = (Align.CENTER, Align.CENTER, Align.MIN)
R = K2_PLATE["radius"]


def L(name, part):
    part.label = name
    return part


def recessed_plate(z0, barrel_xy, drum_r):
    """A plate with its barrel recess cut from the caseback-facing top."""
    p = Pos(0, 0, z0) * Cylinder(R, PLATE_T, align=B)
    p -= Pos(barrel_xy[0], barrel_xy[1], z0 + 2.2) * Cylinder(
        drum_r - 1.0, PLATE_T, align=B)
    return p


kids = []

# --- BASE: K1 time movement -------------------------------------------------
kids.append(L("base plate", recessed_plate(
    0.0, REVC_LAYOUT["barrel"], REVC_LAYOUT["counts"][0] / 2)))
for s in revc_sweeps():
    kids.append(L("base: " + s.name, Pos(s.x, s.y, s.z0) * Cylinder(
        s.r, s.z1 - s.z0, align=B)))

# --- module-support standoffs: base plate top -> module plate ---------------
for az in (70, 160, 250, 340):
    x, y = 80.5 * cos(radians(az)), 80.5 * sin(radians(az))
    kids.append(L("module standoff", Pos(x, y, PLATE_T) * Cylinder(
        3.0, MODULE_PLATE_Z - PLATE_T, align=B)))

# --- MODULE: metronome on its own plate -------------------------------------
kids.append(L("module plate", recessed_plate(
    MODULE_PLATE_Z, K2_MODULE["barrel"], K2_COUNTS["barrel"] / 2)))
for s in module_sweeps():
    kids.append(L("mod: " + s.name, Pos(s.x, s.y, s.z0) * Cylinder(
        s.r, s.z1 - s.z0, align=B)))
kids.append(L("module bridge (cover zone)", Pos(0, 0, MMZ["bridge"][0]) *
             Cylinder(R - 4, MMZ["bridge"][1] - MMZ["bridge"][0], align=B)))

# --- the winding-link corridor (reserved; log 0023) + the one crown ---------
for s in winding_link_zone():
    kids.append(L("winding corridor (reserved)", Pos(s.x, s.y, s.z0) *
                 Cylinder(s.r, s.z1 - s.z0, align=B)))
kids.append(L("crown (one, two positions)", Pos(0, R + 6, 12.0) *
             Cylinder(7, 12, align=B)))

asm = Compound(label="k2_two_sided_r1", children=kids)
export_step(asm, "exports/k2/two_sided_r1.step")
bb = asm.bounding_box()
sc = 40.0 / (2 * R)
print(f"K2 two-sided r1: O{2*R:.0f} x {bb.size.Z:.1f} mm print "
      f"({len(kids)} comps); metal O40 x {bb.size.Z*sc:.1f} mm (fits 44x15 case)")
