"""Caliber K2 gates: the frozen layout stays globally clean, the energy
budget holds, and the beat arithmetic is exact."""
from caliber_k2.movement import (BEAT_BUDGET, K2_COUNTS, K2_LAYOUT,
                                 beats_available, k2_check, k2_sweeps)


def test_k2_layout_globally_clean():
    assert k2_check(k2_sweeps()) == []


def test_k2_energy_budget():
    beats, energy_J = beats_available()
    assert beats >= BEAT_BUDGET, f"only {beats} beats of {BEAT_BUDGET}"


def test_k2_beat_gearing():
    C = K2_COUNTS
    ratio = (C["barrel"] / C["p1"]) * (C["w1"] / C["p2"])
    beats_per_barrel_rev = ratio * 2 * C["esc_teeth"]
    assert ratio == 76.0
    assert beats_per_barrel_rev * 3.0 > BEAT_BUDGET   # 3 conservative turns
