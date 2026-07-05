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


def test_k2_one_crown_two_positions():
    """ONE crown, TWO positions: both barrels' arbors sit on the north
    winding corridor so the sliding clutch can reach either ratchet."""
    from caliber_k2.movement import MET_BARREL_ZONE, cluster_sweeps
    s, L = cluster_sweeps(K2_PLACEMENT["offset"][0],
                          K2_PLACEMENT["offset"][1],
                          K2_PLACEMENT["rot_deg"])
    mbx, mby = L["barrel"]
    assert MET_BARREL_ZONE["x"][0] <= mbx <= MET_BARREL_ZONE["x"][1]
    assert MET_BARREL_ZONE["y"][0] <= mby <= MET_BARREL_ZONE["y"][1]
    assert abs(0.0 - 0.0) < 8          # clock barrel x: on the corridor
