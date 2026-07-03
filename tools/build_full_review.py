"""One-file review of the ENTIRE movement as designed so far.
Real parts + labeled placeholder cylinders for not-yet-ported stations.
All bridge-side heights derive from PLATE_T (log 0013 debt, paid)."""
import sys
from math import cos, sin, radians
from build123d import Align, Compound, Cylinder, Pos, Rot, export_step, export_stl
from caliber_k1 import barrel as m1
from caliber_k1.revb import (revb_layout, keyless_layout_b, motion_layout_b,
                             M2E, PLATE_T)
from caliber_k1.revb_parts import (mainplate, broad_wave_bridge, pallet_cock,
                                   balance_cock_b, ratchet_b, crown_wheel_b,
                                   stem_crown, click_b, cannon_pinion_b,
                                   minute_wheel_b, hour_wheel_dial_b,
                                   moon_s1_b, moon_disc_b, dial_platform)

B = (Align.CENTER, Align.CENTER, Align.MIN)
zo = PLATE_T - 4.0          # bridge-side stack offset vs the old 4mm plate
m, k, ml = revb_layout(), keyless_layout_b(), motion_layout_b()
bx, by = m["barrel"]; cwx, cwy = k["crown_wheel"]
az = radians(105); sp = (88 * cos(az), 88 * sin(az))
drum_z = PLATE_T + 0.5

def L(name, part):
    part.label = name
    return part

kids = [
    L("mainplate", Pos(0, 0, 0) * mainplate()),
    # dial side (in-pocket + platform)
    L("cannon_pinion (in pocket)", Pos(0, 0, M2E["planeA"][0]) * cannon_pinion_b()),
    L("minute_wheel (in pocket)", Pos(ml["minute"][0], ml["minute"][1], M2E["planeA"][0]) * minute_wheel_b()),
    L("hour_wheel (in pocket)", Pos(0, 0, M2E["planeB"][0]) * hour_wheel_dial_b()),
    L("moon_s1 (in pocket)", Pos(ml["s1"][0], ml["s1"][1], M2E["moon_p"][0]) * moon_s1_b()),
    L("moon_disc (in pocket)", Pos(ml["disc"][0], ml["disc"][1], M2E["moon_d"][0]) * moon_disc_b()),
    L("dial_platform (guard)", Pos(0, 0, M2E["platform"][1]) * dial_platform()),
    # barrel group (drum internals; arbor port pending 2e-half)
    L("barrel_drum", Pos(bx, by, drum_z) * m1.drum()),
    L("mainspring", Pos(bx, by, drum_z + 2.9) * m1.mainspring()),
    L("barrel_cover", Pos(bx, by, drum_z + 19.4) * m1.cover()),
    # bridge side
    L("wave_bridge (broad)", Pos(0, 0, 21 + zo) * broad_wave_bridge()),
    L("pallet_cock", Pos(0, 0, 16.5 + zo) * pallet_cock()),
    L("balance_cock", Pos(0, 0, 29 + zo) * balance_cock_b()),
    L("ratchet_wheel (recessed)", Pos(bx, by, 23.5 + zo) * ratchet_b()),
    L("crown_wheel (recessed)", Pos(cwx, cwy, 23.5 + zo) * crown_wheel_b()),
    L("stem_and_crown", Pos(sp[0], sp[1], 29.5 + zo) * Rot(0, 0, 285) * stem_crown()),
    L("click", Pos(bx, by, 24.2 + zo) * Rot(0, 0, -30) * click_b()),
]
# labeled placeholders: stations awaiting the 2e-half part ports
PH = [("center", 33, 0.5, 5.5), ("center", 7, 6.5, 11.5),
      ("third", 31, 0.5, 5.5), ("third", 5, 6.5, 11.5),
      ("fourth", 13, 6.5, 11.5), ("fourth", 5, 0.5, 5.5),
      ("escape", 16, 12.5, 15.5), ("balance", 25, 18.5 + zo, 23.5 + zo)]
for key, r, z0, z1 in PH:
    x, y = m[key]
    ph = (Pos(x, y, PLATE_T + z0) * Cylinder(r, z1 - z0, align=B)
          if key != "balance" else
          Pos(x, y, z0) * Cylinder(r, z1 - z0, align=B))
    kids.append(L(f"PLACEHOLDER_{key} (2e-half pending)", ph))
asm = Compound(label="k1_revb_full_r3", children=kids)
export_step(asm, "exports/revb/review_full_movement_r3.step")
export_stl(asm, "/tmp/full.stl")
bb = asm.bounding_box()
print(f"full movement r2: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm, "
      f"{len(kids)} components")
