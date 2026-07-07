"""Rev B massing mockup: true diameters/positions/heights, no teeth.
For Fusion review of the flat layout BEFORE real geometry is modeled."""
from build123d import Align, Compound, Cylinder, Pos, export_step
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from attic.revb.revb import revb_layout, TRAINS

B = (Align.CENTER, Align.CENTER, Align.MIN)
m, t = revb_layout(), TRAINS["metal"]
kids = [Pos(0, 0, 0) * Cylinder(85, 3, align=B)]                 # mainplate
# (center_xy, radius, z0, z1) — P0 z3-9.5 (drum body), gear planes per revb
solids = [
    (m["barrel"], 37, 3.5, 20.5),      # drum body (spring inside)
    (m["barrel"], 38, 3.5, 8.5),       # 72t ring gear band
    (m["center"], 7, 3.5, 8.5),        # center pinion 12 (P0)
    (m["center"], 33, 9.5, 13.5),      # center wheel 64 (P1)
    (m["third"], 5, 9.5, 13.5),        # third pinion 8 (P1)
    (m["third"], 31, 3.5, 8.5),        # third wheel 60 (P0)
    (m["fourth"], 5, 3.5, 8.5),        # fourth pinion 8 (P0)
    (m["fourth"], 13, 9.5, 13.5),      # fourth wheel 24 (P1)
    (m["escape"], 7, 9.5, 13.5),       # escape pinion 12 (P1)
    (m["escape"], 16, 14.5, 17.5),     # escape wheel 30t (esc plane)
    (m["balance"], 25, 18.5, 23.5),    # balance ring over the bridge
    (m["balance"], 2, 3.5, 24.0),      # balance staff line
]
for (x, y), r, z0, z1 in solids:
    kids.append(Pos(x, y, z0) * Cylinder(r, z1 - z0, align=B))
asm = Compound(label="revb_massing", children=kids)
export_step(asm, "out/revb_massing.step")
print("out/revb_massing.step  | overall height:",
      max(z1 for *_, z1 in solids) + 0, "mm over a 3mm plate")
