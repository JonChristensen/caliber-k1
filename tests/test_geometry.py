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
