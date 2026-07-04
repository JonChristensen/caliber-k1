"""Rev C massing: the solver's layout as labeled true-size cylinders.
The composition gate — collisions are already proven by the global test."""
from build123d import Align, Compound, Cylinder, Pos, export_step
from caliber_k1.revc import (REVC_LAYOUT, revc_sweeps, PLATE_T, RING,
                             SPRING_Z, COCK, ROLLER_Z)

B = (Align.CENTER, Align.CENTER, Align.MIN)


def L(name, part):
    part.label = name
    return part


plate = Cylinder(85, PLATE_T, align=B)
bx, by = REVC_LAYOUT["barrel"]
plate -= Pos(bx, by, 2.2) * Cylinder(REVC_LAYOUT["counts"][0] / 2 - 1.0,
                                     10, align=B)          # barrel recess
# escapement bay: pocket under the escape wheel / lever / roller so they
# sink 2.5 into the plate (Jon's massing r2 note). Floor 0.2 below the
# residents; plan outline = their sweeps + 1.5 wall clearance.
bay_floor = ROLLER_Z[0] - 0.2
for s in revc_sweeps():
    if abs(s.z0 - ROLLER_Z[0]) < 1e-9:
        plate -= Pos(s.x, s.y, bay_floor) * Cylinder(
            s.r + 1.5, PLATE_T - bay_floor + 0.1, align=B)
kids = [L("mainplate (barrel + escapement recesses)", plate)]
for s in revc_sweeps():
    kids.append(L(s.name, Pos(s.x, s.y, s.z0) * Cylinder(s.r, s.z1 - s.z0,
                                                         align=B)))
Bx, By = REVC_LAYOUT["balance"]
kids.append(L("cock (arm zone)", Pos(Bx, By, COCK[0]) * Cylinder(
    8, COCK[1] - COCK[0], align=B)))
# the bridge itself, massed as its cover zone: over the train, coplanar
# with the cock, open around the balance — so the side view shows ONE
# top plane at z17.7 with nothing standing above it
bridge = Pos(-4.0, -14.0, COCK[0]) * Cylinder(60, COCK[1] - COCK[0], align=B)
bridge -= Pos(Bx, By, COCK[0] - 0.1) * Cylinder(
    30, COCK[1] - COCK[0] + 0.2, align=B)
kids.append(L("bridge (cover zone)", bridge))
asm = Compound(label="revc_massing_r4", children=kids)
export_step(asm, "exports/revc/massing_r4.step")
bb = asm.bounding_box()
print(f"rev C massing: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm, "
      f"{len(kids)} components")
