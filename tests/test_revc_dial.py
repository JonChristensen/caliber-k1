"""Rev C dial-side gates: the frozen face layout, exact ratios, all
eight meshes phase-aligned, and the assembled face against the REAL
pocketed plate (the depth rules made physical)."""
from math import atan2, degrees, hypot

import pytest
from build123d import Pos, Rot

from caliber_k1.revc import REVC_LAYOUT
from caliber_k1.revc_dial import (DIAL_BANDS, DIAL_LAYOUT, DIAL_TRAIN,
                                  check_dial, dial_parts_list)
from caliber_k1 import revc_dial_parts as dp


def test_dial_layout_gate():
    assert check_dial() == []


def test_dial_ratios_exact():
    T = DIAL_TRAIN
    motion = (T["motion_w"][0] / T["cannon"][0]) * (T["hour"][0] / T["motion_p"][0])
    assert motion == 12.0
    xfer = (T["idler"][0] / T["transfer"][0]) * 1.0 * (T["transfer"][0] / T["idler"][0])
    assert xfer == 1.0
    moon = (T["w1_w"][0] / T["moon_p"][0]) * (T["w2_w"][0] / T["w1_p"][0]) \
        * (T["disc"][0] / T["w2_p"][0])
    assert moon == 59.0625
    period_days = moon * 12 / 24
    synodic = 29.530589
    years_per_day_error = 1 / (abs(period_days - synodic) * 12.368)
    assert period_days == 29.53125
    assert years_per_day_error > 100


def _mesh_pair(A0, B0, a_xy, b_xy, za, zb, m, t):
    """Thresholds scale with module and face width — a 1mm push into
    m0.6 x t0.75 teeth displaces far less volume than m1 x t3."""
    th = degrees(atan2(b_xy[1] - a_xy[1], b_xy[0] - a_xy[0]))
    rot_a = th - round(th / (360 / za)) * (360 / za)
    th_b = th + 180
    rot_b = (th_b - round(th_b / (360 / zb)) * (360 / zb)) + 180 / zb
    A = Pos(a_xy[0], a_xy[1], 0) * Rot(0, 0, rot_a) * A0
    B = Pos(b_xy[0], b_xy[1], 0) * Rot(0, 0, rot_b) * B0
    inter = A & B
    assert (inter.volume if inter else 0) < 0.15, "interferes at true centers"
    d = hypot(b_xy[0] - a_xy[0], b_xy[1] - a_xy[1])
    B2 = Pos((a_xy[0] - b_xy[0]) / d, (a_xy[1] - b_xy[1]) / d, 0) * B
    inter2 = A & B2
    assert (inter2.volume if inter2 else 0) > 0.4 * m * t, "teeth don't reach"


def test_dial_meshes_phase_aligned():
    """All eight dial meshes engage cleanly at their true distances."""
    L, T = DIAL_LAYOUT, DIAL_TRAIN
    mxy = REVC_LAYOUT["minute"]
    o = (0.0, 0.0)
    cannon, hour = dp.cannon_d(), dp.hour_wheel_d()
    motion, w1, w2 = dp.motion_arbor_d(), dp.w1_d(), dp.w2_d()
    disc, xfer, idler = dp.moon_disc_d(), dp.xfer_pinion_d(), dp.idler_d()
    _mesh_pair(hour, motion, o, L["motion"], T["hour"][0], T["motion_p"][0],
               0.96, 0.75)
    _mesh_pair(cannon, motion, o, L["motion"], T["cannon"][0],
               T["motion_w"][0], 1.0, 0.85)
    _mesh_pair(hour, w1, o, L["w1"], T["moon_p"][0], T["w1_w"][0], 0.75, 0.6)
    _mesh_pair(w1, w2, L["w1"], L["w2"], T["w1_p"][0], T["w2_w"][0], 0.6, 0.85)
    _mesh_pair(w2, disc, L["w2"], L["disc"], T["w2_p"][0], T["disc"][0],
               0.6, 0.75)
    _mesh_pair(xfer, idler, mxy, L["i1"], T["transfer"][0], T["idler"][0],
               0.8, 0.8)
    _mesh_pair(idler, idler, L["i1"], L["i2"], T["idler"][0], T["idler"][0],
               0.8, 0.8)
    _mesh_pair(idler, cannon, L["i2"], o, T["idler"][0], T["transfer"][0],
               0.8, 0.8)


def test_dial_assembled_face_no_interference():
    """The exported face: every dial part clear of the POCKETED plate
    (the depth rules made physical), the platform clear of the works,
    and no non-meshing pair touching at the builder poses."""
    import tools.build_revc_movement as m
    parts = {k.label: k for k in m.kids}
    get = lambda s: next(v for k, v in parts.items() if s in k)
    plate = get("mainplate")
    dial_labels = ["cannon (", "hour wheel", "motion arbor",
                   "moon w1", "moon w2", "moon disc", "transfer pinion",
                   "transfer idler 1", "transfer idler 2"]
    for lab in dial_labels:
        p = get(lab)
        inter = p & plate
        v = inter.volume if inter else 0
        assert v < 0.05, f"{lab} embedded in the plate ({v:.2f})"
    # register pins are PRESSED: interference is the fit, bounded not zero
    for lab in ["center post"] + [f"arbor post {k}" for k in range(1, 7)]:
        inter = get(lab) & plate
        v = inter.volume if inter else 0
        assert 0.05 < v < 3.0, f"{lab} press fit wrong ({v:.2f})"
    platform = get("dial platform")
    for lab in dial_labels:
        inter = platform & get(lab)
        v = inter.volume if inter else 0
        assert v < 0.05, f"platform x {lab} ({v:.2f})"
    # meshing pairs at the phased poses
    mesh_labs = [("cannon (", "motion arbor"), ("hour wheel", "motion arbor"),
                 ("hour wheel", "moon w1"), ("moon w1", "moon w2"),
                 ("moon w2", "moon disc"), ("transfer pinion", "transfer idler 1"),
                 ("transfer idler 1", "transfer idler 2"),
                 ("transfer idler 2", "cannon (")]
    for a, b in mesh_labs:
        inter = get(a) & get(b)
        v = inter.volume if inter else 0
        assert v < 0.4, f"assembled dial mesh {a} x {b} interferes ({v:.2f})"
    # the transfer pinion FRICTION-grips the minute stub (the hand-
    # setting slip): bounded press interference, not zero
    inter = get("minute arbor") & get("transfer pinion")
    assert 0.01 < (inter.volume if inter else 0) < 1.0
