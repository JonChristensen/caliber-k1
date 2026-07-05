"""Rev C full movement r1 — every ported part on REVC_LAYOUT coordinates,
the whole train phase-CHAINED into true mesh (each arbor's single rotation
satisfies both of its meshes via za*ta + zb*tb = const), labeled for the
STEP browser."""
from math import atan2, degrees

from build123d import Compound, Pos, Rot, export_step

from caliber_k1.revc import REVC_LAYOUT, cock_layout_c, lever_layout_c
from caliber_k1.revc_dial import DIAL_LAYOUT, DIAL_TRAIN
from caliber_k1 import revc_parts as rp
from caliber_k1 import revc_dial_parts as dp


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
    L("ratchet (flush in the bridge pocket)",
      Pos(*lay["barrel"], 0) * rp.ratchet_c()),
    L("click (M1's flexure, bridge pocket)",
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
]
_plates = [s for s in rp.bridge_c().solids() if s.volume > 200]
for i, s in enumerate(sorted(_plates, key=lambda s: -s.volume)):
    kids.append(L(f"wave bridge (traced){'' if i == 0 else f' piece {i+1}'}", s))

# winding stage: crown wheel phased to the ratchet (which stays square-
# aligned on the arbor); stem rolled so a tooth centers on a slot
from caliber_k1.revc import WINDING
cw = WINDING["crown_wheel"]
ra, rb = mesh_rots(lay["barrel"], cw, 24, 24)
R_crown = rb + ra                      # ratchet phase 0 (square-aligned)
kids += [
    L("crown wheel (underside slots)", Pos(*cw, 0) * Rot(0, 0, R_crown)
      * rp.crown_wheel_c()),
    L("crown wheel stud", Pos(*cw, 0) * rp.crown_stud_c()),
    L("stem + crown (winds by ~9 turns)",
      rp.stem_c().rotate(__import__("build123d").Axis(
          (0, 80, WINDING["stem_z"]), (0, 1, 0)), 48)),
    L("stem clip", rp.stem_clip_c()),
]

# --- the dial side: phase the 8-mesh chain off the minute arbor ---------------
DL = DIAL_LAYOUT
mxy = lay["minute"]


def chained(a_xy, b_xy, za, zb, R_a):
    """b's rotation meshing a, given a's already-fixed rotation R_a."""
    ra, rb = mesh_rots(a_xy, b_xy, za, zb)
    return rb + (ra - R_a) * za / zb


Zt, Zi = DIAL_TRAIN["transfer"][0], DIAL_TRAIN["idler"][0]
R_i1 = chained(mxy, DL["i1"], Zt, Zi, R_minute)
R_i2 = chained(DL["i1"], DL["i2"], Zi, Zi, R_i1)
R_cannon = chained(DL["i2"], (0, 0), Zi, Zt, R_i2)
R_motion = chained((0, 0), DL["motion"], DIAL_TRAIN["cannon"][0],
                   DIAL_TRAIN["motion_w"][0], R_cannon)
R_hour = chained(DL["motion"], (0, 0), DIAL_TRAIN["motion_p"][0],
                 DIAL_TRAIN["hour"][0], R_motion)
R_w1 = chained((0, 0), DL["w1"], DIAL_TRAIN["moon_p"][0],
               DIAL_TRAIN["w1_w"][0], R_hour)
R_w2 = chained(DL["w1"], DL["w2"], DIAL_TRAIN["w1_p"][0],
               DIAL_TRAIN["w2_w"][0], R_w1)
R_disc = chained(DL["w2"], DL["disc"], DIAL_TRAIN["w2_p"][0],
                 DIAL_TRAIN["disc"][0], R_w2)

kids += [
    L("center post (O3 register pin)", dp.center_post_d()),
    L("cannon (pinion + transfer wheel)", Rot(0, 0, R_cannon) * dp.cannon_d()),
    L("hour wheel + moon pinion (short pipe)", Rot(0, 0, R_hour) * dp.hour_wheel_d()),
    L("motion arbor (10t + 36t)",
      Pos(*DL["motion"], 0) * Rot(0, 0, R_motion) * dp.motion_arbor_d()),
    L("moon w1 (36t + 12t)", Pos(*DL["w1"], 0) * Rot(0, 0, R_w1) * dp.w1_d()),
    L("moon w2 (54t + 8t)", Pos(*DL["w2"], 0) * Rot(0, 0, R_w2) * dp.w2_d()),
    L("moon disc (70t, 29.53125d)",
      Pos(*DL["disc"], 0) * Rot(0, 0, R_disc) * dp.moon_disc_d()),
    L("transfer pinion (on the minute stub)",
      Pos(*mxy, 0) * Rot(0, 0, R_minute) * dp.xfer_pinion_d()),
    L("transfer idler 1", Pos(*DL["i1"], 0) * Rot(0, 0, R_i1) * dp.idler_d()),
    L("transfer idler 2", Pos(*DL["i2"], 0) * Rot(0, 0, R_i2) * dp.idler_d()),
    L("dial platform (moon window NW)", dp.dial_platform_d()),
]
from caliber_k1.revc_dial import post_specs
for k, (name, px, py, tip, top) in enumerate(post_specs()):
    kids.append(L(f"arbor post {k+1}: {name} (O2 register pin)",
                  Pos(px, py, tip) * dp.arbor_post_d(top - 0.1 - tip)))

asm = Compound(label="revc_movement_r5", children=kids)
export_step(asm, "exports/revc/movement_r9.step")
bb = asm.bounding_box()
print(f"rev C movement r9: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.1f} mm "
      f"(z {bb.min.Z:.1f}..{bb.max.Z:.1f}), {len(kids)} components")
