"""K2 massing: the metronome's cast as labeled true-size volumes."""
from build123d import Align, Compound, Cylinder, Pos, export_step

from caliber_k2.movement import (K2_LAYOUT, K2_RIM, K2_PLATE_T, MZ,
                                 k2_check, k2_sweeps)

B = (Align.CENTER, Align.CENTER, Align.MIN)


def L(name, part):
    part.label = name
    return part


bad = k2_check(k2_sweeps())
assert not bad, bad
kids = [L("K2 mainplate (O140)", Cylinder(70, K2_PLATE_T, align=B))]
seen = {}
for s in k2_sweeps():
    n = seen.get(s.name, 0)
    seen[s.name] = n + 1
    label = s.name if n == 0 else f"{s.name} ({n + 1})"
    kids.append(L(label, Pos(s.x, s.y, s.z0) * Cylinder(s.r, s.z1 - s.z0,
                                                        align=B)))
bx, by = K2_LAYOUT["barrel"]
kids.append(L("K2 bridge (cover zone)",
              Pos(0, 0, MZ["bridge"][0]) * Cylinder(64, 3.0, align=B)))
kids.append(L("anvil boss (the thump lands here)",
              Pos(*K2_LAYOUT["anvil"], K2_PLATE_T) *
              Cylinder(6.0, MZ["esc"][1] - K2_PLATE_T, align=B)))
asm = Compound(label="k2_massing_r1", children=kids)
export_step(asm, "exports/k2/massing_r1.step")
bb = asm.bounding_box()
print(f"K2 massing r1: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm, "
      f"{len(kids)} components")
