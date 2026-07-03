"""Geometry sanity checks — these run in CI before any printer wastes plastic.

Pure-math checks validate the parameter set; the build checks actually
construct the OCCT solids and assert basic physical plausibility.
"""

from math import sqrt

import pytest

from caliber_k1.parameters import (
    ARBOR, BARREL, RATCHET, SPRING, STAND, TOL,
    approx_winding_turns, pillar_height, spring_pitch, spring_radial_span,
)


# --- parameter-level checks (fast, always run) -----------------------------

def test_spring_fits_annulus():
    assert spring_radial_span() > SPRING.coils * SPRING.thickness, \
        "printed coils cannot physically fit in the barrel annulus"


def test_coil_gaps_positive():
    assert spring_pitch() > SPRING.thickness + 0.6, \
        "coils need >=0.6mm air gap or they fuse while printing"


def test_spring_shorter_than_chamber():
    assert SPRING.height <= BARREL.inner_h - 0.8


def test_slot_taller_than_spring():
    assert BARREL.spring_slot_h >= SPRING.height


def test_square_passes_top_bushing():
    # the winding square must fit through the top plate bushing on assembly
    hole_d = ARBOR.pivot_d + 2 * TOL.pivot_clearance
    assert ARBOR.square_side * sqrt(2) < hole_d


def test_useful_winding_turns():
    assert approx_winding_turns() >= 3.0, "less than 3 turns isn't worth winding"


def test_ratchet_clears_pillars():
    pillar_inner_r = STAND.pillar_circle_d / 2 - STAND.pillar_d / 2
    assert RATCHET.wheel_d / 2 + RATCHET.click_arm_len / 2 < pillar_inner_r + 10


def test_drum_clears_pillars():
    pillar_inner_r = STAND.pillar_circle_d / 2 - STAND.pillar_d / 2
    assert BARREL.drum_outer_d / 2 < pillar_inner_r, \
        "drum would rub the stand pillars"


def test_stack_height_consistent():
    assert pillar_height() == pytest.approx(BARREL.total_h + 2 * TOL.endshake)


# --- solid-construction checks (build real OCCT geometry) ------------------

def test_parts_build_and_have_volume():
    from caliber_k1 import barrel, stand

    for maker in (barrel.ratchet_wheel, barrel.click, barrel.lock_pin, stand.pillar):
        part = maker()
        assert part.volume > 100, f"{maker.__name__} built with implausible volume"


def test_arbor_length_matches_stack():
    from caliber_k1.barrel import arbor, arbor_total_length

    part = arbor()
    bb = part.bounding_box()
    assert bb.size.Z == pytest.approx(arbor_total_length(), abs=0.01)


# --- Milestone 2: train math, layout clearances, and the tripod fix --------

from caliber_k1.parameters import TRAIN, train_layout, train_periods


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def test_pillar_positions_distinct():
    from caliber_k1.stand import _pillar_positions
    pts = _pillar_positions()
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            assert _dist(pts[i], pts[j]) > STAND.pillar_d, \
                f"pillars {i} and {j} overlap — the v1 duplicate-pillar bug"


def test_train_ratios_exact():
    p = train_periods()
    assert p["w4"] == pytest.approx(60.0), "seconds arbor must be exactly 60 s"
    assert p["esc"] == pytest.approx(30.0)
    # 30-tooth escape wheel at 30 s/rev = 1 tooth/s = 1 Hz balance in M3
    assert TRAIN.esc_wheel / p["esc"] == pytest.approx(1.0)


def test_mesh_center_distances():
    lay = train_layout()
    m = TRAIN.module
    assert _dist((0, 0), lay["w1"]) == pytest.approx(
        m * (TRAIN.drum_teeth + TRAIN.w1_pinion) / 2)
    assert _dist(lay["w1"], lay["w4"]) == pytest.approx(
        m * (TRAIN.w1_wheel + TRAIN.w4_pinion) / 2)
    assert _dist(lay["w4"], lay["esc"]) == pytest.approx(
        m * (TRAIN.w4_wheel + TRAIN.esc_pinion) / 2)


def test_layout_clearances():
    """Every rotating tip circle clears every static obstacle by >=1.5mm."""
    from caliber_k1.stand import _pillar_positions
    from caliber_k1.parameters import MOVEMENT_DIAMETER
    lay = train_layout()
    m = TRAIN.module
    add = TRAIN.wheel_addendum * m
    tip = {
        "w1": m * TRAIN.w1_wheel / 2 + add,
        "w4": m * TRAIN.w4_wheel / 2 + add,
        "esc": m * TRAIN.esc_pinion / 2 + 1.0,
    }
    drum_tip = m * TRAIN.drum_teeth / 2 + add
    obstacles = [(p, STAND.pillar_d / 2, "pillar") for p in _pillar_positions()]
    obstacles += [(lay["foot_a"], 4.0, "foot_a"), (lay["foot_b"], 4.0, "foot_b")]
    for key, r in tip.items():
        c = lay[key]
        # inside the plate rim
        assert _dist(c, (0, 0)) + r < MOVEMENT_DIAMETER / 2 - 2, \
            f"{key} pokes past the rig plate rim"
        for (ox, oy), orad, oname in obstacles:
            assert _dist(c, (ox, oy)) > r + orad + 1.5, \
                f"{key} tip circle hits {oname}"
    # wheels that must NOT touch the drum (only W1's pinion meshes it)
    for key in ("w4", "esc"):
        assert _dist(lay[key], (0, 0)) > drum_tip + tip[key] - add + 1.5, \
            f"{key} wheel fouls the drum teeth"


def test_train_under_spider():
    from caliber_k1.parameters import TRAIN_LEVELS
    bridge_top = TRAIN_LEVELS["bridge_z"] + TRAIN_LEVELS["bridge_t"]
    assert bridge_top < pillar_height() - 1.0, \
        "wave bridge must clear the spider plate underside"


def test_m2_parts_build():
    from caliber_k1 import train_parts
    w1 = train_parts.w1_arbor()
    bridge = train_parts.wave_bridge()
    plate = train_parts.rig_plate()
    assert w1.volume > 500
    assert bridge.volume > 1000
    assert plate.volume > 10000
    from caliber_k1.parameters import TRAIN_LEVELS
    expected = 4 + TRAIN_LEVELS["bridge_z"] + 4  # pivot..bridge-pivot top
    assert w1.bounding_box().size.Z == pytest.approx(expected, abs=0.01)


def test_bridge_band_clears_pillars_and_drum():
    """The bridge body (half-width 6.5) must not sweep through a pillar,
    and its inner edge must clear the spinning drum wall (r36)."""
    from caliber_k1.stand import _pillar_positions
    lay = train_layout()
    path = [lay["foot_a"], lay["w1"], lay["w4"], lay["esc"], lay["foot_b"]]
    half_w = 6.5

    def seg_dist(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        cx, cy = ax + t * dx, ay + t * dy
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

    for pil in _pillar_positions():
        for i in range(len(path) - 1):
            d = seg_dist(pil, path[i], path[i + 1])
            assert d > half_w + STAND.pillar_d / 2 + 0.5, \
                f"bridge segment {i} sweeps through pillar at {pil}"
    # drum wall clearance: nearest approach of the band centerline to origin
    for i in range(len(path) - 1):
        d = seg_dist((0.0, 0.0), path[i], path[i + 1])
        assert d - half_w > 36.0 + 1.0, \
            f"bridge segment {i} edge too close to the drum wall"


def test_wave_tube_is_a_balance_seat():
    """Milestone 3 contract: the wave tube center must stay at Swiss-lever
    span from the escape arbor (2.0-2.4x escape pitch radius), so the
    balance jewel can live in the barrel of the wave."""
    from caliber_k1.decor import wave_tube_center
    lay = train_layout()
    path = [lay["foot_a"], lay["w1"], lay["w4"], lay["esc"], lay["foot_b"]]
    tube = wave_tube_center(path)
    esc_r = TRAIN.esc_wheel * TRAIN.module / 2
    span = _dist(tube, lay["esc"])
    assert 2.0 * esc_r < span < 2.4 * esc_r, \
        f"tube at {span:.1f}mm from escape arbor — outside lever-escapement reach"


# --- Milestone 3: escapement + balance --------------------------------------

from caliber_k1.parameters import (
    BAL, ESC, M3_LEVELS, MOVEMENT_DIAMETER, m3_layout, predicted_period,
)


def test_predicted_period_in_trim_band():
    assert 0.80 < predicted_period() < 1.25, \
        "balance/hairspring combo can't be trimmed to 1 Hz with rim nuts"


def test_pallet_pins_symmetric():
    m = m3_layout()
    d0 = _dist(m["pins"][0], m["P"])
    d1 = _dist(m["pins"][1], m["P"])
    assert d0 == pytest.approx(d1, abs=0.01), "anchor arms must be symmetric"


def test_hairspring_coils_dont_fuse():
    pitch = (BAL.hs_r_out - BAL.hs_r_in) / BAL.hs_coils
    assert pitch - BAL.hs_t > 0.55, "hairspring coils too close to print"


def test_balance_fits_plate():
    m = m3_layout()
    reach = _dist(m["B"], (0, 0)) + BAL.ring_od / 2
    assert reach < MOVEMENT_DIAMETER / 2 - 2


def test_cock_column_clears_balance():
    m = m3_layout()
    assert _dist(m["cock_foot"], m["B"]) > BAL.ring_od / 2 + 5.0 + 1.5, \
        "cock column inside the balance sweep"


def test_platform_pillars_clear_moving_parts():
    m = m3_layout()
    lay = train_layout()
    for key in ("pillar_a", "pillar_b"):
        c = m[key]
        assert _dist(c, m["E"]) > ESC.wheel_tip_r + 3.5 + 1.5, \
            f"{key} inside the escape wheel sweep"
        assert _dist(c, (0, 0)) > 37.0 + 3.5 + 1.5, f"{key} hits the drum"
        assert _dist(c, lay["w1"]) > 26.0 + 3.5 + 1.5, f"{key} hits W1"
        assert _dist(c, lay["w4"]) > 13.0 + 3.5 + 1.5, f"{key} hits W4"
        assert _dist(c, m["B"]) > 5.5 + 3.5 + 1.0, f"{key} hits the staff/roller"
        assert _dist(c, (0, 0)) + 3.5 < MOVEMENT_DIAMETER / 2 - 2


def test_balance_ring_clears_platform():
    assert M3_LEVELS["balance_z"] >= M3_LEVELS["platform_z"] + M3_LEVELS["platform_t"] + 0.5


def test_m3_parts_build():
    from caliber_k1 import escapement
    for maker in (escapement.escape_wheel, escapement.pallet_lever,
                  escapement.balance_cock, escapement.hairspring):
        part = maker()
        assert part.volume > 200, f"{maker.__name__} implausibly small"


# --- Milestone 4: motion works arithmetic ------------------------------------

def test_motion_works_exact():
    from caliber_k1.parameters import motion_periods
    p = motion_periods()
    assert p["minute_s"] == pytest.approx(3600.0), "minute hand must be exactly 1 hr"
    assert p["hour_s"] == pytest.approx(43200.0), "hour hand must be exactly 12 hr"


# --- Milestone 4: upper-deck motion works layout -----------------------------

def test_m4_mesh_distances_exact():
    from caliber_k1.parameters import m4_layout
    m = m4_layout()
    W1 = train_layout()["w1"]
    assert _dist(W1, m["R1"]) == pytest.approx((16 + 24) / 2, abs=0.05)
    assert _dist(m["R1"], m["R2"]) == pytest.approx((10 + 32) / 2, abs=0.05)
    assert _dist(m["R2"], m["T"]) == pytest.approx((10 + 30) / 2, abs=0.05)
    assert _dist(m["T"], m["M"]) == pytest.approx((12 + 36) / 2, abs=0.05)


def test_m4_deck_clearances():
    from caliber_k1.parameters import m4_layout, m3_layout
    m, e = m4_layout(), m3_layout()
    tips = {"R1": 13, "R2": 17, "T": 16, "M": 19}
    # R1's wheel lives DOWN at z10.5-15.5: check the ground-floor gap
    lay = train_layout()
    assert _dist(m["R1"], lay["foot_a"]) > 13 + 4.5 + 1.5, "R1 hits foot_a post"
    # rim, cock column, balance ring (z36+ meshes), winding-knob sweep r23.5
    for k, tip in tips.items():
        c = m[k]
        assert _dist(c, (0, 0)) + tip < 83, f"{k} past rim"
        assert _dist(c, e["cock_foot"]) > tip + 5.5 + 1.5, f"{k} hits cock column"
        if k in ("R2", "T", "M"):
            assert _dist(c, e["B"]) > tip + 25 + 1.5, f"{k} hits balance ring"
            assert _dist(c, (0, 0)) - tip > 23.5, f"{k} hits winding knob sweep"
    # deck pillars clear all rotating tips + R1's lower wheel (z10.5-15.5)
    for pk in ("deck_pillar_a", "deck_pillar_b"):
        p = m[pk]
        for k, tip in tips.items():
            assert _dist(p, m[k]) > tip + 3.5 + 1.4, f"{pk} hits {k}"
        assert _dist(p, (0, 0)) + 3.5 < 83, f"{pk} past rim"


def test_m4_zstack_consistent():
    from caliber_k1.parameters import M4_LEVELS as L
    assert L["deck_plate_z"] > 27.8        # flies over the spider
    assert L["mesh1_z"] >= L["deck_plate_z"] + L["deck_plate_t"]
    assert L["mesh2_z"] >= L["mesh1_z"] + 5.5 and L["mesh3_z"] >= L["mesh2_z"] + 5.5
    assert L["dial_cock_z"] >= L["mesh4_z"] + 5.0
    assert L["hands_z"] > L["dial_cock_z"] + L["dial_cock_t"]


def test_m4_parts_build():
    from caliber_k1 import motion
    for maker in (motion.r1_arbor, motion.t_arbor, motion.deck_plate,
                  motion.dial_cock, motion.winding_knob):
        assert maker().volume > 150, f"{maker.__name__} implausibly small"
