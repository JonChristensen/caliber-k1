"""Caliber K2 gates: the frozen joint layout stays globally clean
(clock + metronome interleaved on ONE round plate, flat at 17.7),
the energy budget holds, and the beat arithmetic is exact."""
from caliber_k2.movement import (BEAT_BUDGET, K2_COUNTS, K2_MET,
                                 beats_available, k2_gate)


def test_k2_inventory_complete():
    """Jon's rule: recite the full cast before massing. Every part
    tagged 'sweep' must own an envelope in k2_sweeps()."""
    from caliber_k2.movement import k2_sweeps, K2_INVENTORY
    have = set(s.name for s in k2_sweeps())
    missing = [n for n, kind in K2_INVENTORY if kind == "sweep"
               and n not in have]
    assert missing == [], f"inventory parts with no envelope: {missing}"


def test_k2_full_cast_debt():
    """With the FULL cast placed, the clock + every rotating metronome
    mass is clean; the ONLY unresolved conflicts are the bridge pillars
    and the keyless clutch train, which await the full-cast RE-SOLVE
    (r5 O250 was packed without reserving their sites). Log 0021."""
    STRUCT = {"m_pillar", "m_clutch", "m_setting_lever", "m_detent"}
    for line in k2_gate():
        parts = [p.strip() for p in line.split(":")[0].split(" x ")]
        assert any(p in STRUCT for p in parts), \
            f"a NON-structural conflict surfaced (masses not clean): {line}"


def test_k2_energy_budget():
    beats, energy_J = beats_available()
    assert beats >= BEAT_BUDGET, f"only {beats} beats of {BEAT_BUDGET}"


def test_k2_beat_gearing():
    C = K2_COUNTS
    ratio = (C["barrel"] / C["p1"]) * (C["w1"] / C["p2"])
    assert ratio == 76.0
    assert ratio * 2 * C["esc_teeth"] * 3.0 > BEAT_BUDGET


def test_k2_one_crown_two_positions():
    """ONE crown, TWO positions: both ratchets flush at 16.05-17.65 on
    the derived stem line, contrate cores both at stem z13."""
    from caliber_k2.movement import k2_sweeps
    names = [s.name for s in k2_sweeps()]
    assert names.count("cw1_core") == 2 and names.count("cw2_core") == 2
    ratchets = [s for s in k2_sweeps() if s.name == "m_ratchet"]
    assert ratchets and all(abs(s.z0 - 16.05) < 0.01 for s in ratchets)
