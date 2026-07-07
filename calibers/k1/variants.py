"""The variant switch: one geometry, two material worlds.

Set K1_VARIANT=metal (env) or pass variant= explicitly. Print and metal
share ALL layout coordinates and wheel counts; they differ only in the
dimension tables below — and every derived height (like the stem line)
is computed FROM these, so flipping the switch reflows the movement.

(Born in rev B, but it's a caliber-wide contract: rev C and the tests
consume it too — which is why it lives here and not in the attic.)
"""
from dataclasses import dataclass
import os as _os


@dataclass(frozen=True)
class Variant:
    name: str
    drum_h: float           # barrel drum height (spring volume driver)
    usable_turns: float
    pivot_clearance: float  # running fits
    endshake: float
    spring: str             # mainspring spec
    escapement: str         # swiss_lever both worlds (log 0015); pin_pallet = fallback
    lock_deg: float         # pallet lock: deep for print error, fine for metal
    draw_deg: float
    backlash: float = 0.30  # train mesh backlash (probe-tuned print default)
    press_r: float = 0.03   # radial press-fit interference on the O3 staff


VARIANTS = {
    "print": Variant("print", 17.0, 1.5, 0.20, 0.50,
                     "PETG strip 1.6x16", "swiss_lever", 3.0, 15.0,
                     backlash=0.30, press_r=0.03),
    "metal": Variant("metal", 4.5, 7.0, 0.04, 0.10,
                     "steel 0.30x14 (spec at DFM pass)", "swiss_lever", 1.5, 13.0,
                     backlash=0.12, press_r=0.01),
}


def active_variant() -> Variant:
    return VARIANTS[_os.environ.get("K1_VARIANT", "print")]
