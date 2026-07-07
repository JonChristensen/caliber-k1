"""The shared horological engine — everything a caliber needs that isn't
caliber-specific: the cycloidal gear generator (`movement.gears`), the
whole-movement sweep solver (`movement.solver`), and the printed-spring
energy model (`movement.springs`).

Calibers bind their own parameters: e.g. calibers/k1 wraps `gears` with
its TRAIN defaults and `check_sweeps` with its rim + mesh-pair list.
This package must stay parameter-free — if a number is caliber-specific,
it does not belong here.
"""
