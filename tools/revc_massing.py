"""Rev C massing: THE COMPLETE CAST as labeled true-size volumes, built
from revc.INVENTORY (Jon's rule: recite every component before massing;
the run fails loudly if any inventory item is missing from the output).
Collisions are already proven by the global gate."""
from build123d import Align, Box, Compound, Cylinder, Pos, export_step, extrude

from caliber_k1.revc import (BAY_FLOOR, INVENTORY, PLATE_T, REVC_LAYOUT,
                             WINDING, ZC, bay_band, bay_stations,
                             cock_layout_c, lever_layout_c, revc_sweeps)
from caliber_k1.revc_dial import DIAL_BANDS, dial_parts_list
from caliber_k1.revc_parts import _band

B = (Align.CENTER, Align.CENTER, Align.MIN)


def L(name, part):
    part.label = name
    return part


kids = []

# --- the plate (with its carvings shown) ---------------------------------------
plate = Cylinder(85, PLATE_T, align=B)
bx, by = REVC_LAYOUT["barrel"]
Zd = REVC_LAYOUT["counts"][0]
plate -= Pos(bx, by, 2.2) * Cylinder(Zd / 2 - 1.0, 10, align=B)
for (cx, cy), wall_r in bay_stations():
    plate -= Pos(cx, cy, BAY_FLOOR) * Cylinder(wall_r, PLATE_T, align=B)
bpath, bhw = bay_band()
plate -= Pos(0, 0, BAY_FLOOR) * extrude(_band(bpath, bhw), PLATE_T)
kids.append(L("mainplate (recesses shown)", plate))

# --- every sweep in the gate model (train, oscillator, winding station) -------
seg = {}
for s in revc_sweeps():
    n = seg.get(s.name, 0)
    seg[s.name] = n + 1
    label = s.name if n == 0 else f"{s.name} ({n + 1})"
    kids.append(L(label, Pos(s.x, s.y, s.z0) * Cylinder(s.r, s.z1 - s.z0,
                                                        align=B)))

# --- static zones: bridge, cock, strap -----------------------------------------
Bx, By = REVC_LAYOUT["balance"]
bridge = Pos(-4.0, 4.0, ZC["bridge"][0]) * Cylinder(
    62, ZC["bridge"][1] - ZC["bridge"][0], align=B)
bridge -= Pos(Bx, By, ZC["bridge"][0] - 0.1) * Cylinder(
    31, ZC["bridge"][1] - ZC["bridge"][0] + 0.2, align=B)
kids.append(L("bridge (cover zone)", bridge))
kids.append(L("balance cock (arm zone)", Pos(Bx, By, ZC["bridge"][0]) *
             Cylinder(8, ZC["bridge"][1] - ZC["bridge"][0], align=B)))
lv = lever_layout_c()
kids.append(L("pallet strap", Pos(0, 0, ZC["strap"][0]) * extrude(
    _band([lv["strap_feet"][0], lv["P"], lv["strap_feet"][1]], 3.5),
    ZC["strap"][1] - ZC["strap"][0])))

# --- the dial side, sunken in its pockets --------------------------------------
for (name, x, y, tip_r, band) in dial_parts_list():
    lo, hi = DIAL_BANDS[band]
    kids.append(L(f"dial works: {name}", Pos(x, y, lo) * Cylinder(
        tip_r, hi - lo, align=B)))
kids.append(L("dial platform", Pos(0, 0, -0.8) * Cylinder(60, 0.8, align=B)))

# --- the stem pendant, honestly PROUD (the r5 gate question) -------------------
kids.append(L("stem pendant boss (PROUD of the bridge)",
              Pos(0, 74, 17.7) * Box(10, 30, WINDING["stem_z"] + 2.6 - 17.7,
                                     align=B)))
kids.append(L("crown (outside the rim)",
              Pos(0, 91, WINDING["stem_z"] - 6) * Cylinder(7, 12, align=B)))

asm = Compound(label="revc_massing_r5", children=kids)
export_step(asm, "exports/revc/massing_r5.step")
bb = asm.bounding_box()
labels = [k.label for k in kids]
missing = [n for n, kind in INVENTORY
           if not any(n.split(" ")[0] in lab for lab in labels)]
assert not missing, f"INVENTORY items missing from the massing: {missing}"
print(f"rev C massing r5: {bb.size.X:.0f} x {bb.size.Y:.0f} x "
      f"{bb.size.Z:.1f} mm, {len(kids)} components; inventory complete")
