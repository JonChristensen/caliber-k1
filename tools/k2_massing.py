"""K2 massing r2: the TWO-BARREL caliber — K1's clock core (west disc)
+ the metronome cluster (east disc), every can labeled."""
from build123d import Align, Compound, Cylinder, Pos, export_step

from caliber_k1.revc import PLATE_T
from caliber_k2.movement import (K2_PLATE, MZ, clock_neighbors, k2_gate,
                                 k2_sweeps)

B = (Align.CENTER, Align.CENTER, Align.MIN)


def L(name, part):
    part.label = name
    return part


bad = k2_gate()
assert not bad, bad
pcx, pcy = K2_PLATE["center"]
plate = Pos(pcx, pcy, 0) * Cylinder(K2_PLATE["radius"], PLATE_T, align=B)
kids = [L(f"K2 plate (ROUND, O{2*K2_PLATE['radius']:.0f})", plate)]
seen = {}
for s in list(clock_neighbors()) + list(k2_sweeps()):
    n = seen.get(s.name, 0)
    seen[s.name] = n + 1
    label = s.name if n == 0 else f"{s.name} ({n + 1})"
    kids.append(L(label, Pos(s.x, s.y, s.z0) * Cylinder(s.r, s.z1 - s.z0,
                                                        align=B)))
kids.append(L("clock bridge zone",
              Pos(-4, 4, 14.7) * Cylinder(62, 3.0, align=B)))
from caliber_k2.movement import K2_PLACEMENT
ox, oy = K2_PLACEMENT["offset"]
kids.append(L("metronome bridge zone",
              Pos(ox, oy, MZ["bridge"][0]) * Cylinder(60, 3.0, align=B)))
asm = Compound(label="k2_massing_r4", children=kids)
export_step(asm, "exports/k2/massing_r4.step")
bb = asm.bounding_box()
print(f"K2 massing r4: {bb.size.X:.0f} x {bb.size.Y:.0f} x "
      f"{bb.size.Z:.1f} mm, {len(kids)} components")
