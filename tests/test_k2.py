"""Caliber K2 gates: the frozen joint layout stays globally clean
(clock + metronome interleaved on ONE round plate, flat at 17.7),
the energy budget holds, and the beat arithmetic is exact."""
from caliber_k2.movement import (BEAT_BUDGET, K2_COUNTS,
                                 beats_available, k2_module_gate)


def test_k2_inventory_complete():
    """Jon's rule: recite the full cast before massing. Every 'sweep'
    part owns an envelope on the module plate; the 'pending' tier is
    exactly the winding-link + chrono works awaiting their solve (0023)."""
    from caliber_k2.movement import K2_INVENTORY, module_sweeps
    have = set(s.name for s in module_sweeps())
    missing = [n for n, k in K2_INVENTORY if k == "sweep" and n not in have]
    assert missing == [], f"placed parts with no envelope: {missing}"
    pending = {n for n, k in K2_INVENTORY if k == "pending"}
    assert pending == {"m_stem", "k2_crown", "cw1_core", "cw2_core",
                       "wind_idler", "m_clutch", "m_setting_lever",
                       "m_detent", "m_pusher"}, "pending tier drifted"


def test_k2_module_on_own_plate():
    """Two-sided architecture (Jon, July 5): the metronome ALONE on its
    own O166 module plate is globally clean and inside the rim — the
    plate no longer grows. Base time side is K1's own gated core."""
    assert k2_module_gate() == []


def test_k2_energy_budget():
    beats, energy_J = beats_available()
    assert beats >= BEAT_BUDGET, f"only {beats} beats of {BEAT_BUDGET}"


def test_k2_beat_gearing():
    C = K2_COUNTS
    ratio = (C["barrel"] / C["p1"]) * (C["w1"] / C["p2"])
    assert ratio == 76.0
    assert ratio * 2 * C["esc_teeth"] * 3.0 > BEAT_BUDGET


def test_k2_two_sided_stack():
    """Two-sided: base (K1 z-grammar, tops 17.7) + module plate stacked
    at 18.2, metronome works above it. The module ratchet is flush in the
    module bridge; the two plates share the O166 diameter."""
    from caliber_k2.movement import (module_sweeps, MODULE_PLATE_Z, MMZ,
                                     K2_PLATE)
    assert MODULE_PLATE_Z >= 17.7                    # module clears the base
    names = [s.name for s in module_sweeps()]
    assert "m_ratchet" in names and "m_drum" in names and "m_ring" in names
    rat = next(s for s in module_sweeps() if s.name == "m_ratchet")
    assert abs(rat.z0 - (MMZ["bridge"][0] + 1.35)) < 0.01
    assert K2_PLATE["radius"] == 83.0
