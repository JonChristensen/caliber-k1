"""Printed-spring energy model — sizes every barrel in the manufacture."""
from math import pi


def spring_model(drum_id, hub_d, strip_t, strip_h, module_E=2.0e9):
    """PETG spiral in a drum: usable turns (half-fill rule), mean torque
    (N*mm, linearized), strip length (mm)."""
    r_wall, r_hub = drum_id / 2, hub_d / 2
    area = pi * (r_wall**2 - r_hub**2)
    L = area / 2 / strip_t
    turns_wound = ((r_hub**2 + L * strip_t / pi) ** 0.5 - r_hub) / strip_t
    turns_relax = (r_wall - (r_wall**2 - L * strip_t / pi) ** 0.5) / strip_t
    turns = turns_wound - turns_relax
    I_sec = strip_h * strip_t**3 / 12          # mm^4
    k = module_E * I_sec / (L * 1e3)           # N*mm per radian-ish
    tau_mean = k * (turns * 2 * pi) / 2 / 1e3  # rough mean torque N*mm... keep relative
    return {"turns": turns, "length": L, "tau_rel": strip_h * strip_t**3 / L}
