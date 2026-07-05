"""Caliber K2 gates: the frozen two-cluster placement stays globally
clean (clock + metronome jointly), the energy budget holds, and the
beat arithmetic is exact."""
from caliber_k2.movement import (BEAT_BUDGET, K2_COUNTS, K2_PLACEMENT,
                                 beats_available, k2_gate)


def test_k2_layout_globally_clean():
    assert k2_gate() == []


def test_k2_energy_budget():
    beats, energy_J = beats_available()
    assert beats >= BEAT_BUDGET, f"only {beats} beats of {BEAT_BUDGET}"


def test_k2_beat_gearing():
    C = K2_COUNTS
    ratio = (C["barrel"] / C["p1"]) * (C["w1"] / C["p2"])
    assert ratio == 76.0
    assert ratio * 2 * C["esc_teeth"] * 3.0 > BEAT_BUDGET


def test_k2_two_crowns_apart():
    """Two barrels, two crowns: the clock's stem exits north of the
    clock disc; the metronome's winding station lives on its own disc
    -- the stations must not share rim territory."""
    from math import hypot
    cx, cy = K2_PLACEMENT["offset"]
    assert hypot(cx, cy) > 60          # clusters genuinely apart
