"""Rev C massing: the solver's layout as labeled true-size cylinders.
The composition gate — collisions are already proven by the global test."""
from build123d import Align, Compound, Cylinder, Pos, export_step
from caliber_k1.revc import REVC_LAYOUT, revc_sweeps, PLATE_T, RING, SPRING_Z, COCK

B = (Align.CENTER, Align.CENTER, Align.MIN)


def L(name, part):
    part.label = name
    return part


plate = Cylinder(85, PLATE_T, align=B)
bx, by = REVC_LAYOUT["barrel"]
plate -= Pos(bx, by, 2.2) * Cylinder(REVC_LAYOUT["counts"][0] / 2 - 1.0,
                                     10, align=B)          # barrel recess
kids = [L("mainplate (with barrel recess)", plate)]
for s in revc_sweeps():
    kids.append(L(s.name, Pos(s.x, s.y, s.z0) * Cylinder(s.r, s.z1 - s.z0,
                                                         align=B)))
Bx, By = REVC_LAYOUT["balance"]
kids.append(L("cock (arm zone)", Pos(Bx, By, COCK[0]) * Cylinder(
    8, COCK[1] - COCK[0], align=B)))
asm = Compound(label="revc_massing_r1", children=kids)
export_step(asm, "exports/revc/massing_r1.step")
bb = asm.bounding_box()
print(f"rev C massing: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm, "
      f"{len(kids)} components")
