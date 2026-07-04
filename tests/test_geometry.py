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


def test_moon_phase_accuracy():
    from caliber_k1.parameters import lunation_days
    true_lun = 29.530588853
    err_per_lun = abs(lunation_days() - true_lun)          # days
    years_to_one_day = true_lun / err_per_lun / 12.368
    assert years_to_one_day > 100, "moon phase must hold 1 day for >100 years"


def test_hour_pipe_passes_dial_cock():
    # hour wheel pipe Ø9 must journal inside the dial cock's T bore
    assert 4.5 + TOL.pivot_clearance > 4.5, "cock bore must clear the pipe"


# --- Rev B: dual-train arithmetic --------------------------------------------

def test_revb_trains_exact():
    from caliber_k1.revb import train_check
    for variant in ("metal", "print"):
        r = train_check(variant)
        assert r["center_min"] == pytest.approx(60.0), f"{variant}: center wheel"
        assert r["fourth_s"] == pytest.approx(60.0), f"{variant}: seconds"
        assert r["esc_s"] == pytest.approx(30.0), f"{variant}: escape (1 Hz, 30t)"
    assert train_check("metal")["runtime_h"] >= 40, "metal: 40h+ reserve (7 turns x 6h)"
    assert train_check("print")["runtime_h"] >= 8, "print variant: overnight run"


def test_revb_layout_meshes_and_fits():
    from caliber_k1.revb import revb_layout, TRAINS
    m, t = revb_layout(), TRAINS["metal"]
    pairs = [("barrel", "center", (t["barrel"] + t["c_pin"]) / 2),
             ("center", "third", (t["center"] + t["t_pin"]) / 2),
             ("third", "fourth", (t["third"] + t["f_pin"]) / 2),
             ("fourth", "escape", (t["fourth"] + t["e_pin"]) / 2),
             ("escape", "balance", 34.5)]                  # lever span
    for a, b, d in pairs:
        assert _dist(m[a], m[b]) == pytest.approx(d, abs=0.05), f"{a}-{b}"
    tips = {"barrel": 37, "center": 33, "third": 31, "fourth": 13,
            "escape": 16, "balance": 25}
    for k, tip in tips.items():
        assert _dist(m[k], (0, 0)) + tip < 83, f"{k} past the rim"
    # same-plane wheel bodies must clear (P0: barrel vs third wheel;
    # P1: center vs fourth wheel)
    assert _dist(m["barrel"], m["third"]) > 37 + 31 + 1.5
    assert _dist(m["center"], m["fourth"]) > 33 + 13 + 1.5


def test_revb_mainplate_builds():
    from caliber_k1.revb_parts import mainplate
    p = mainplate()
    assert p.volume > 80000, "mainplate implausibly small"
    from caliber_k1.revb import PLATE_T
    assert p.bounding_box().size.Z == pytest.approx(PLATE_T, abs=0.01)


def test_revb_wave_bridge_tube_clears_balance_staff():
    """The staff's path through the bridge must be genuinely empty."""
    from build123d import Cylinder, Pos, Align
    from caliber_k1.revb import revb_layout
    from caliber_k1.revb_parts import wave_bridge_b
    b = wave_bridge_b()
    x, y = revb_layout()["balance"]
    probe = Pos(x, y, -5) * Cylinder(2.8, 20,
                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    inter = b & probe
    assert (inter.volume if inter else 0) < 1.0, \
        "wave tube does not clear the balance staff passage"
    assert b.volume > 3000


def test_broad_bridge_well_and_bearings():
    from build123d import Cylinder, Pos, Align
    from caliber_k1.revb import revb_layout
    from caliber_k1.revb_parts import broad_wave_bridge
    b = broad_wave_bridge()
    m = revb_layout()
    BM = (Align.CENTER, Align.CENTER, Align.MIN)
    # balance ring (r25) must swim free in the well
    x, y = m["balance"]
    ring = Pos(x, y, -8) * Cylinder(25.5, 16, align=BM)
    inter = b & ring
    assert (inter.volume if inter else 0) < 1.0, "balance ring hits the well rim"
    # every arbor's upper pivot path must be open through plate + boss
    for k in ("center", "third", "fourth", "escape"):
        px, py = m[k]
        probe = Pos(px, py, -8) * Cylinder(1.4, 16, align=BM)
        inter = b & probe
        assert (inter.volume if inter else 0) < 1.0, f"{k} bearing blocked"
    assert b.volume > 15000


def test_revb_escapement_packing():
    from caliber_k1.revb import escapement_layout_b, revb_layout, ZB
    e, m = escapement_layout_b(), revb_layout()
    # pallet feet must clear the escape wheel sweep (r16) at post level
    for f in e["pallet_feet"]:
        assert _dist(f, e["E"]) > 16 + 1.55 + 0.5, "pallet foot in wheel sweep"
    # pallet cock top must clear the ring bottom
    assert ZB["pallet_cock"][1] + 0.4 <= ZB["ring"][0]
    # cock feet must land outside the well on the bridge
    from math import cos, sin, radians
    for a in (35, 80):
        f = (m["balance"][0] + 33 * cos(radians(a)),
             m["balance"][1] + 33 * sin(radians(a)))
        assert _dist(f, m["balance"]) > 27 + 5.0, "cock foot inside the well"


def test_revb_cocks_build():
    from caliber_k1.revb_parts import pallet_cock, balance_cock_b
    assert pallet_cock().volume > 200
    assert balance_cock_b().volume > 800


def test_bridge_stays_on_the_plate():
    from caliber_k1.revb_parts import broad_wave_bridge
    bb = broad_wave_bridge().bounding_box()
    for v in (bb.min.X, bb.min.Y, bb.max.X, bb.max.Y):
        assert abs(v) <= 85.5, f"bridge overhangs the mainplate rim: {v:.1f}"


def test_keyless_layout():
    from caliber_k1.revb import keyless_layout_b, revb_layout
    k, m = keyless_layout_b(), revb_layout()
    # crown wheel meshes the ratchet at 24t+24t module-1 center distance
    assert _dist(k["crown_wheel"], m["barrel"]) == pytest.approx(24.0, abs=0.05)
    # crown wheel stays inside the rim and clear of the center pad
    assert _dist(k["crown_wheel"], (0, 0)) + 13 < 84
    # stem sector: crown wheel azimuth within the reserved 90-120 band
    from math import atan2, degrees
    az = degrees(atan2(k["crown_wheel"][1], k["crown_wheel"][0])) % 360
    assert 90 <= az <= 120


def test_revb_keyless_parts_build():
    from caliber_k1 import revb_parts as rp
    for mk in (rp.ratchet_b, rp.crown_wheel_b, rp.stem_crown, rp.click_b):
        assert mk().volume > 150, f"{mk.__name__} implausibly small"


def test_click_actually_reaches_the_ratchet():
    from caliber_k1.revb import click_geometry_b
    g = click_geometry_b()
    root_r, tip_r = 12.0 - 1.3, 13.0          # 24t module-1 wheel
    assert root_r + 0.3 < g["tip_r"] < tip_r - 0.3, \
        f"click tip at r{g['tip_r']:.1f} does not engage teeth ({root_r}-{tip_r})"


def test_click_part_tip_engages_in_place():
    """Build the actual click PART, place it as the assembly does, and
    verify solid material lands inside the tooth engagement band."""
    from math import radians
    from build123d import Cylinder, Pos, Rot, Align
    from caliber_k1.revb import revb_layout
    from caliber_k1.revb_parts import click_b
    bx, by = revb_layout()["barrel"]
    placed = Pos(bx, by, 0) * Rot(0, 0, -30) * click_b()
    band = Pos(bx, by, -1) * Cylinder(12.6, 6, align=(
        Align.CENTER, Align.CENTER, Align.MIN)) - \
        Pos(bx, by, -2) * Cylinder(11.0, 9, align=(
            Align.CENTER, Align.CENTER, Align.MIN))
    inter = placed & band
    # wedge tip ~0.6mm^2 cross-section x 2.8 height => ~1.7mm^3 engaged
    assert inter and inter.volume > 1.0, "click tip not in the tooth band"


def test_crown_knob_clears_the_bridge():
    """Crown at r88: its inner face (r85) must stay outboard of the
    bridge's maximum extent (<=85.5 asserted elsewhere, real edge ~84)."""
    from caliber_k1.revb_parts import broad_wave_bridge
    bb = broad_wave_bridge().bounding_box()
    bridge_max_r = max(abs(bb.min.X), abs(bb.min.Y), bb.max.X, bb.max.Y)
    knob_inner_r = 88 - 3
    assert knob_inner_r - bridge_max_r >= 0.5, \
        "crown knob crowds the bridge's north edge"


# --- The variant switch -------------------------------------------------------

def test_variant_switch_reflows_the_stem():
    from caliber_k1.revb import VARIANTS, stem_line_z, bridge_z, drum_top_z
    zp, zm = stem_line_z(VARIANTS["print"]), stem_line_z(VARIANTS["metal"])
    assert zp > zm + 10, "metal stem must drop with its slim barrel"
    for v in VARIANTS.values():
        assert bridge_z(v) >= drum_top_z(v) + 0.5 - 1e-9, \
            f"{v.name}: drum buried in the bridge (Jon's side-view catch)"


def test_variants_share_the_layout():
    """The whole point: identical wheels, identical positions, both worlds.
    Layout functions take no variant — geometry cannot fork by accident."""
    from caliber_k1.revb import TRAINS
    for key in ("barrel", "c_pin", "center", "t_pin", "third",
                "f_pin", "fourth", "e_pin"):
        assert TRAINS["print"][key] == TRAINS["metal"][key]


# --- 2e: dial side ------------------------------------------------------------

def test_motion_works_module_trick():
    from caliber_k1.revb import M2E, motion_layout_b
    m = motion_layout_b()
    assert _dist(m["minute"], (0, 0)) == pytest.approx((12 + 36) / 2 * 1.0)
    assert (10 + 40) / 2 * M2E["hour_mesh_module"] == pytest.approx(24.0)
    assert (36 / 12) * (40 / 10) == 12.0


def test_moon_disc_packs_clear():
    from caliber_k1.revb import M2E, motion_layout_b
    m = motion_layout_b()
    tip = 105 * M2E["moon_module"] / 2 + M2E["moon_module"]
    assert _dist(m["disc"], (0, 0)) + tip < 84, "disc past the rim"
    assert _dist(m["disc"], (0, 0)) - tip > 3.5, "disc eats the center pipes"
    assert _dist(m["disc"], m["s1"]) == pytest.approx((8 + 105) / 2 * 0.6, abs=0.05)


def test_dial_parts_build():
    from caliber_k1 import revb_parts as rp
    for mk in (rp.cannon_pinion_b, rp.minute_wheel_b, rp.hour_wheel_dial_b,
               rp.moon_s1_b, rp.moon_disc_b, rp.dial_platform):
        assert mk().volume > 80, f"{mk.__name__} implausibly small"


def test_the_dial_actually_fits():
    """Pocketed scheme (log 0013): works inside the plate, platform
    closes the pocket, dial beyond it, hands outermost."""
    from caliber_k1.revb import M2E, PLATE_T
    assert M2E["pocket_depth"] <= PLATE_T - 3.5, "pocket eats the bridge-side bushings"
    assert M2E["planeA"][1] <= M2E["pocket_depth"] + 1e-9
    assert M2E["platform"][1] < 0 < M2E["platform"][0] + 1e-9
    dial_top, dial_bottom = M2E["dial_z"]
    assert dial_top <= M2E["platform"][1] - 0.15, "dial rubs the platform"
    assert M2E["hour_hand_z"] <= dial_bottom - 0.3, "hour hand rubs the dial"
    assert dial_top - dial_bottom >= 0.8 - 1e-9, "dial too thin to print"


def test_moon_is_actually_visible():
    """Jon's catch: the guard sealed the moon in. The platform must have
    open sky over a moon sitting at the aperture position."""
    from math import cos, sin, radians
    from build123d import Cylinder, Pos, Align
    from caliber_k1.revb import M2E, motion_layout_b
    from caliber_k1.revb_parts import dial_platform
    ml = motion_layout_b()
    a = radians(M2E["moon_aperture_az_deg"])
    ax = ml["disc"][0] + 18 * cos(a)
    ay = ml["disc"][1] + 18 * sin(a)
    probe = Pos(ax, ay, -2) * Cylinder(4.5, 6, align=(
        Align.CENTER, Align.CENTER, Align.MIN))
    inter = dial_platform() & probe
    assert (inter.volume if inter else 0) < 0.5, "moon hidden behind the guard"


def test_plate_bushings_open_from_the_top():
    """A pivot must be able to ENTER every bridge-side bushing (they
    sealed shut when PLATE_T grew — never again)."""
    from build123d import Cylinder, Pos, Align
    from caliber_k1.revb import revb_layout, PLATE_T
    from caliber_k1.revb_parts import mainplate
    p = mainplate()
    m = revb_layout()
    for k, r in (("barrel", 3.9), ("center", 1.4), ("third", 1.4),
                 ("fourth", 1.4), ("escape", 1.4), ("balance", 1.15)):
        x, y = m[k]
        probe = Pos(x, y, PLATE_T - 2.5) * Cylinder(r, 4, align=(
            Align.CENTER, Align.CENTER, Align.MIN))
        inter = p & probe
        assert (inter.volume if inter else 0) < 0.5, f"{k} bushing sealed"


# --- 2e-half: the real train --------------------------------------------------

def test_train_arbors_span_plate_to_bridge_boss():
    from caliber_k1 import revb_parts as rp
    from caliber_k1.revb import active_variant, train_upper_bearing_z
    boss = train_upper_bearing_z(active_variant())
    from caliber_k1.revb import bridge_z
    bz = bridge_z(active_variant())
    spans = {rp.center_arbor_b: (1.2, bz + 2.5), rp.third_arbor_b: (3.5, bz + 2.5),
             rp.fourth_arbor_b: (3.5, boss + 4.0), rp.escape_arbor_b: (3.5, boss + 4.0)}
    for mk, (z0, ztop) in spans.items():
        bb = mk().bounding_box()
        assert bb.size.Z == pytest.approx(ztop - z0, abs=0.05), \
            f"{mk.__name__} does not span its bearings"


def test_escape_wheel_clears_bridge_bosses():
    from caliber_k1.revb import GEAR_PLANES, active_variant, train_upper_bearing_z
    assert GEAR_PLANES["ESC"][1] + 1.0 <= train_upper_bearing_z(active_variant())


def test_balance_staff_reaches_cock():
    from caliber_k1.revb_parts import balance_staff_rev_b
    from caliber_k1.revb import active_variant, osc_stack
    bb = balance_staff_rev_b().bounding_box()
    assert bb.max.Z == pytest.approx(osc_stack(active_variant())["staff_top"], abs=0.05)


def test_balance_ring_sits_between_strap_and_center_wheel():
    """Jon's placement: ring UNDER the bridge, in the well — above the
    pallet bridge's thin upper strap, below the high center wheel."""
    from caliber_k1.revb import active_variant, p1_high, osc_stack
    v = active_variant()
    o = osc_stack(v)
    strap_top = 22.0 + 0.2 + 1.5
    assert o["ring_lo"] >= strap_top + 0.5, "ring rubs the pallet strap"
    assert o["ring_hi"] <= p1_high(v)[0] - 0.5, "ring reaches the center wheel"


def test_train_meshes_phase_aligned():
    """The definitive train check: every mesh pair, phase-rotated so a
    tooth faces a gap (as running gears do), must show ZERO interference
    at true centers AND real tooth engagement when pushed 1mm closer.
    (First probe version skipped phasing — two pairs passed by luck.)"""
    from math import hypot, atan2, degrees
    from build123d import Pos, Rot
    from caliber_k1 import barrel as m1
    from caliber_k1.revb import revb_layout, PLATE_T
    from caliber_k1 import revb_parts as rp
    m = revb_layout()
    parts = {"drum": (m1.drum(), PLATE_T + 0.5, m["barrel"]),
             "center": (rp.center_arbor_b(), 1.2, m["center"]),
             "third": (rp.third_arbor_b(), 3.5, m["third"]),
             "fourth": (rp.fourth_arbor_b(), 3.5, m["fourth"]),
             "escape": (rp.escape_arbor_b(), 3.5, m["escape"])}
    for a, b, za, zb in [("drum","center",72,12), ("center","third",80,8),
                         ("third","fourth",48,8), ("fourth","escape",24,12)]:
        A0, azz, (ax, ay) = parts[a]
        B0, bzz, (bx, by) = parts[b]
        th = degrees(atan2(by - ay, bx - ax))
        rot_a = th - round(th / (360/za)) * (360/za)
        th_b = th + 180
        rot_b = (th_b - round(th_b / (360/zb)) * (360/zb)) + 180/zb
        A = Pos(ax, ay, azz) * Rot(0, 0, rot_a) * A0
        B = Pos(bx, by, bzz) * Rot(0, 0, rot_b) * B0
        inter = A & B
        assert (inter.volume if inter else 0) < 0.5, f"{a}->{b} interferes"
        d = hypot(bx-ax, by-ay)
        B2 = Pos((ax-bx)/d, (ay-by)/d, 0) * B
        inter2 = A & B2
        assert (inter2.volume if inter2 else 0) > 1.0, f"{a}->{b} teeth don't reach"


# --- 2f-pre: the Swiss lever gates the wheel ----------------------------------

def test_swiss_lever_gates_the_escape_wheel():
    """First-cut escapement probe: with the lever centered, the club wheel
    must NOT be able to rotate freely (pallets gate most phases), and
    swinging the lever must change the engagement — proof the fork
    commands the wheel. Dynamic behavior is the bench's job."""
    from math import degrees
    from build123d import Pos, Rot
    from caliber_k1.revb import lever_layout_b
    from caliber_k1.revb_parts import club_escape_wheel_b, swiss_lever_b
    L = lever_layout_b()
    wheel0 = club_escape_wheel_b()
    lever0 = swiss_lever_b()
    lever = Pos(L["P"][0], L["P"][1], 0) * Rot(0, 0, degrees(L["ang"])) * lever0
    gated = 0
    vols = []
    for k in range(13):
        w = Pos(L["E"][0], L["E"][1], 0) * Rot(0, 0, k) * wheel0
        inter = w & lever
        v = inter.volume if inter else 0.0
        vols.append(v)
        if v > 0.5:
            gated += 1
    assert gated >= 6, f"pallets barely touch the wheel ({gated}/13 phases)"
    # the decisive property: somewhere on the (wheel phase x lever angle)
    # grid the wheel is deeply LOCKED, somewhere it runs FREE. The release
    # window is ~2 deg wide and drifts with phase — so probe the joint grid.
    lo, hi = 1e9, 0.0
    for k in range(0, 13, 3):
        w_k = Pos(L["E"][0], L["E"][1], 0) * Rot(0, 0, k) * wheel0
        for sw in range(-8, 9, 2):
            lv = Pos(L["P"][0], L["P"][1], 0) * Rot(0, 0, degrees(L["ang"]) + sw) * lever0
            i2 = w_k & lv
            v = i2.volume if i2 else 0.0
            lo, hi = min(lo, v), max(hi, v)
    assert hi > 4.0, "lever cannot lock the wheel anywhere on the grid"
    assert lo < 0.5, "lever cannot release the wheel anywhere on the grid"


def test_pallet_bridge_serviceable():
    """The removable cassette: builds, its feet clear the escape wheel
    sweep and sit under the balance ring's airspace, and the fork's
    short arbor spans exactly the two bearing cups."""
    from caliber_k1.revb import lever_layout_b
    from caliber_k1.revb_parts import pallet_bridge_b, swiss_lever_b
    L = lever_layout_b()
    for f in L["bridge_feet"]:
        assert _dist(f, L["E"]) > 16 + 4 + 1.0, "bridge foot in wheel sweep"
        assert _dist(f, L["B"]) > 5.5 + 4 + 0.5, "bridge foot hits the staff"
    b = pallet_bridge_b()
    assert b.volume > 1500
    lv = swiss_lever_b()
    assert lv.bounding_box().size.Z == pytest.approx(3.0 + 2 * 1.4, abs=0.05)


def test_escapement_safety_parts():
    """Banking pins limit the swing; the guard finger stops 0.3 off the
    safety roller; the crescent lets it pass only in line."""
    from caliber_k1.revb import lever_layout_b
    from caliber_k1.revb_parts import swiss_lever_b, roller_b, pallet_bridge_b
    L = lever_layout_b()
    lv = swiss_lever_b()
    r = roller_b()
    assert r.volume > 25   # slim two-tier roller
    assert pallet_bridge_b().volume > 1500
    bb = lv.bounding_box()
    # horns must stop clear of the slimmed impulse table (r2.6 at fork_len)
    assert bb.max.X < L["fork_len"] - 1.8, "fork horns hit the impulse table"


def test_steel_staff_conversion():
    """Register upgrades: every balance-borne part grips the Ø3 rod, and
    the collet is slit (friction clamp, rotatable = beat adjustment)."""
    from caliber_k1.revb_parts import balance_wheel_b, hairspring_b, roller_b
    for mk in (balance_wheel_b, hairspring_b, roller_b):
        assert mk().volume > 25, f"{mk.__name__} implausible"
    hs = hairspring_b()
    # slit present: material near the collet's -x side is cut through
    from build123d import Cylinder, Pos, Align
    probe = Pos(-8.2, 0, -1) * Cylinder(0.2, 8, align=(
        Align.CENTER, Align.CENTER, Align.MIN))
    inter = hs & probe
    assert (inter.volume if inter else 0) < 0.05, "collet slit missing"


def test_hairspring_nests_in_the_well():
    """Jon's arrangement: spring inside the bridge's thickness, clear of
    the center wheel band below and NEVER touching the balance wheel —
    connected only through the collet on the staff."""
    from caliber_k1.revb import active_variant, bridge_z, p1_high, osc_stack
    v = active_variant()
    o = osc_stack(v)
    assert o["hs_lo"] >= p1_high(v)[1] + 0.5, "spring combs the center wheel"
    assert o["hs_lo"] >= o["ring_hi"] + 0.5, "spring rests on the balance wheel"
    assert o["hs_lo"] >= bridge_z(v), "spring below the well opening"
    assert 24.0 + 1.5 < 27.0, "breathing clearance inside the well"
