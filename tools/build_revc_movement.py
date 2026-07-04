"""Rev C full movement r1 — every ported part on REVC_LAYOUT coordinates,
the whole train phase-CHAINED into true mesh (each arbor's single rotation
satisfies both of its meshes via za*ta + zb*tb = const), labeled for the
STEP browser."""
from math import atan2, degrees

from build123d import Compound, Pos, Rot, export_step

from caliber_k1.revc import REVC_LAYOUT, cock_layout_c, lever_layout_c
from caliber_k1 import revc_parts as rp


def L(name, part):
    part.label = name
    return part


def mesh_rots(a_xy, b_xy, za, zb):
    """The probe-perfect pair: wheel a's tooth on the line, pinion b's
    gap facing it. Any (ta, tb) with za*ta + zb*tb == za*ra + zb*rb
    meshes identically."""
    th = degrees(atan2(b_xy[1] - a_xy[1], b_xy[0] - a_xy[0]))
    rot_a = th - round(th / (360 / za)) * (360 / za)
    th_b = th + 180
    rot_b = (th_b - round(th_b / (360 / zb)) * (360 / zb)) + 180 / zb
    return rot_a, rot_b


lay = REVC_LAYOUT
Zd, pm, Zm, p3, Z3, p4, Z4, pe = lay["counts"]
lv = lever_layout_c()
ck = cock_layout_c()

# chain from the escapement backward: each arbor gets ONE rotation; the
# invariant za*ta + zb*tb = za*ra* + zb*rb* keeps every mesh tooth-in-gap
fe_a, fe_b = mesh_rots(lay["fourth"], lay["escape"], Z4, pe)
R_esc = fe_b
R_fourth = fe_a                                   # satisfies fourth-escape
tf_a, tf_b = mesh_rots(lay["third"], lay["fourth"], Z3, p4)
R_third = tf_a + (tf_b - R_fourth) * p4 / Z3      # compensate fourth's phase
mt_a, mt_b = mesh_rots(lay["minute"], lay["third"], Zm, p3)
R_minute = mt_a + (mt_b - R_third) * p3 / Zm
bm_a, bm_b = mesh_rots(lay["barrel"], lay["minute"], Zd, pm)
R_drum = bm_a + (bm_b - R_minute) * pm / Zd

kids = [
    L("mainplate", rp.mainplate_c()),
    L("barrel drum (56t band)", Pos(*lay["barrel"], 0) * Rot(0, 0, R_drum) * rp.drum_c()),
    L("barrel arbor (winding square, dial side)",
      Pos(*lay["barrel"], 0) * rp.barrel_arbor_c()),
    L("drum cover", Pos(*lay["barrel"], 0) * rp.drum_cover_c()),
    L("ratchet (dial side, retains the arbor)",
      Pos(*lay["barrel"], 0) * rp.ratchet_c()),
    L("click (dial side, M1's flexure)",
      Pos(*lay["barrel"], 0) * Rot(0, 0, rp.click_geometry_c()["angle_deg"])
      * rp.click_c()),
    L("minute arbor: 14t pinion + 80t wheel",
      Pos(*lay["minute"], 0) * Rot(0, 0, R_minute) * rp.minute_arbor_c()),
    L("third arbor: 48t wheel + 8t pinion",
      Pos(*lay["third"], 0) * Rot(0, 0, R_third) * rp.third_arbor_c()),
    L("fourth arbor: 8t pinion + 36t wheel (60s)",
      Pos(*lay["fourth"], 0) * Rot(0, 0, R_fourth) * rp.fourth_arbor_c()),
    L("escape arbor: 18t pinion",
      Pos(*lay["escape"], 0) * Rot(0, 0, R_esc) * rp.escape_arbor_c()),
    L("club escape wheel (30t, in the bay)",
      Pos(*lay["escape"], 4.3) * rp.club_escape_wheel_c()),
    L("pallet fork (Swiss lever)",
      Pos(*lv["P"], 4.2) * Rot(0, 0, degrees(lv["ang"])) * rp.swiss_lever_c()),
    L("pallet bay strap (2x M2, removable)", rp.bay_strap_c()),
    L("roller (impulse pin + crescent)",
      Pos(*lay["balance"], 0) * Rot(0, 0, degrees(lv["ang"]) + 180) * rp.roller_c()),
    L("balance staff (O3 rod register)", Pos(*lay["balance"], 0) * rp.balance_staff_c()),
    L("balance wheel", Pos(*lay["balance"], 0) * rp.balance_wheel_c()),
    L("hairspring (slit collet, tab on the stud)",
      Pos(*lay["balance"], 0) * Rot(0, 0, degrees(ck["stud_az"]) )
      * rp.hairspring_c()),
    L("balance cock (cabochon on top)", rp.balance_cock_c()),
    L("train bridge (plain; wave pass later)", rp.bridge_c()),
]

asm = Compound(label="revc_movement_r1", children=kids)
export_step(asm, "exports/revc/movement_r1.step")
bb = asm.bounding_box()
print(f"rev C movement r1: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm "
      f"(z {bb.min.Z:.1f}..{bb.max.Z:.1f}), {len(kids)} components")
