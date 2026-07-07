"""One-file review of the ENTIRE movement as designed so far.
Real parts + labeled placeholder cylinders for not-yet-ported stations.
All bridge-side heights derive from PLATE_T (log 0013 debt, paid)."""
import sys
from math import cos, sin, radians
from build123d import Align, Compound, Cylinder, Pos, Rot, export_step, export_stl
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from attic.reva import barrel as m1
from attic.revb.revb import (revb_layout, keyless_layout_b, motion_layout_b,
                             M2E, PLATE_T, active_variant, bridge_z,
                             winding_wheels_z, stem_line_z)
from attic.revb.revb_parts import (mainplate, broad_wave_bridge, pallet_bridge_b,
                                   balance_cock_b, ratchet_b, crown_wheel_b,
                                   stem_crown, click_b, cannon_pinion_b,
                                   minute_wheel_b, hour_wheel_dial_b,
                                   moon_s1_b, moon_disc_b, dial_platform)

B = (Align.CENTER, Align.CENTER, Align.MIN)
V = active_variant()
BZ = bridge_z(V)            # bridge underside, DERIVED from the drum
WZ = winding_wheels_z(V)
zo = BZ - 21.0              # legacy-relative offset for bridge-side parts
from attic.revb.revb import osc_stack
OS = osc_stack(V)
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
    L("balance_cock", Pos(0, 0, 29 + zo) * balance_cock_b()),
    L("ratchet_wheel (recessed)", Pos(bx, by, WZ) * ratchet_b()),
    L("crown_wheel (recessed)", Pos(cwx, cwy, WZ) * crown_wheel_b()),
    L("stem_and_crown", Pos(sp[0], sp[1], stem_line_z(V)) * Rot(0, 0, 285) * stem_crown()),
    L("click", Pos(bx, by, WZ + 0.7) * Rot(0, 0, -30) * click_b()),
]
# 2e-half: the REAL train (placeholders retired)
from attic.revb.revb_parts import (center_arbor_b, third_arbor_b,
                                   fourth_arbor_b, escape_arbor_b,
                                   balance_staff_rev_b)
from attic.reva import escapement as esc_a
kids.append(L("center_arbor (80t/12t, high wheel)", Pos(m["center"][0], m["center"][1], 1.2) * center_arbor_b()))
kids.append(L("third_arbor (48t/8t)", Pos(m["third"][0], m["third"][1], 3.5) * third_arbor_b()))
kids.append(L("fourth_arbor (24t/8t, seconds)", Pos(m["fourth"][0], m["fourth"][1], 3.5) * fourth_arbor_b()))
kids.append(L("escape_arbor (12t + D-seat)", Pos(m["escape"][0], m["escape"][1], 3.5) * escape_arbor_b()))
from attic.revb.revb_parts import club_escape_wheel_b, swiss_lever_b
from attic.revb.revb import lever_layout_b
from math import degrees
LL = lever_layout_b()
kids.append(L("escape_wheel (30t club-tooth)", Pos(m["escape"][0], m["escape"][1], 19.0) * club_escape_wheel_b()))
kids.append(L("swiss_lever (pallet fork)", Pos(LL["P"][0], LL["P"][1], 19.0) * Rot(0, 0, degrees(LL["ang"])) * swiss_lever_b()))
from attic.revb.revb_parts import roller_b
kids.append(L("roller (two-tier + crescent)", Pos(m["balance"][0], m["balance"][1], 19.0) * roller_b()))
kids.append(L("pallet_bridge (removable, 2x M3)", Pos(0, 0, PLATE_T) * pallet_bridge_b()))
kids.append(L("balance_staff (O3 steel rod - BOM)", Pos(m["balance"][0], m["balance"][1], 3.5) * Cylinder(1.5, OS["staff_top"] - 3.5, align=B)))
from attic.revb.revb_parts import balance_wheel_b, hairspring_b
kids.append(L("balance_wheel (in the well, under the bridge)", Pos(m["balance"][0], m["balance"][1], OS["ring_lo"]) * balance_wheel_b()))
kids.append(L("hairspring (slit collet, over the well)", Pos(m["balance"][0], m["balance"][1], OS["hs_lo"]) * hairspring_b()))
asm = Compound(label="k1_revb_full_r5", children=kids)
export_step(asm, "exports/k1/revb/review_full_movement_r13.step")
export_stl(asm, "/tmp/full.stl")
bb = asm.bounding_box()
print(f"full movement r2: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm, "
      f"{len(kids)} components")
