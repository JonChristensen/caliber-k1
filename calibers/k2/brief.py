"""Caliber K2 — the frozen brief, the metal target, and the energy budget.

JON'S FROZEN BRIEF (log 0020): 60-180 BPM continuous, hammer tick +
desk thump, chronograph pen-cam pusher, own barrel, >=30 min at 180
per wind (the wind is a BEAT budget: the same wind lasts ~95 min at
largo 60). v2 dream: 1-2 h.

THE MOVEMENT (Jon's correction, July 5): K2 TELLS TIME TOO — it is a
TWO-BARREL, TWO-CROWN caliber: K1's proven clock core (hands, motion
works, indirect minute — minus the moon train) plus the metronome
cluster as its complication. (Since log 0022 the two clusters live on
TWO plates — see layout.py.)

ENERGY (sizes everything): drum id66 x strip 2.6x7.0 PETG stores
~6.7 J -> ~6700 beats at SAFETY 2.5 = 38 min @180 / 113 min @60 (with
the 10 g x 2.5 mm hammer). Beats per barrel rev = (76/8)(64/8)*2*15 =
2280; usable ~3.5 turns -> ~8000 beats of gearing: spring exhausts
first, as it should.

RATE (the 9:1 problem): rate = sqrt(k/I)/2pi. Two 10g weights sliding
r5 -> r15 give I_weights 9:1; the web adds a floor, so the real span
lands ~2.6-2.8:1 — the hairspring k and web mass are TUNED at parts
stage so 60 and 180 both sit inside the sliders' travel, with margin.
"""
from math import pi

from movement.springs import spring_model

# --- THE METAL TARGET (Jon, July 5): the real destination -----------------------
# K2 in metal must drop into a ~44 x 15 mm wristwatch case (47 max, be
# careful with lugs). Budget: 44 - case walls -> Ø40 movement; 15 -
# sapphire top (1) - dial/hands (2) - sapphire back + structure (2) ->
# ~10 mm movement. The PRINT and METAL are ONE topology at two scales:
# the diameter fit is scale-invariant (packs the print circle => packs
# Ø40), so GROWING THE PRINT PLATE IS FREE w.r.t. the metal. Metal is
# ~4x chunkier in ratio (3.7:1 vs the print's ~14:1) -> vertical room to
# spare; the metal z-table is TALL where the print is flat.
K2_METAL = dict(
    case_d=44.0, case_d_max=47.0, case_t=15.0,
    movement_d=40.0, movement_t=10.0,        # the envelope to hit
    module=None,                             # = 40 / (2 * print_reach): set
                                             # after the full-cast re-solve
    note="two barrels + metronome at Ø40x10 is grand-complication scale; "
         "the DFM pass decides if the met barrel wants the caseback side.",
)

# --- energy budget -------------------------------------------------------------
HAMMER = dict(mass_g=10.0, drop_mm=2.5, note="M3 steel nut in the head")
BEAT_BUDGET = 5400             # 30 min @ 180 BPM
SAFETY = 2.5
K2_SPRING = dict(drum_id=66.0, hub_d=12.0, strip_t=2.6, strip_h=7.0)


def beats_available():
    s = spring_model(**{k: v for k, v in K2_SPRING.items()})
    I_sec = K2_SPRING["strip_h"] * K2_SPRING["strip_t"] ** 3 / 12
    kappa = 2000.0 * I_sec / s["length"]
    theta = s["turns"] * 2 * pi
    energy_J = 0.5 * kappa * theta ** 2 / 1000.0
    per_beat = (HAMMER["mass_g"] / 1000 * 9.81 *
                HAMMER["drop_mm"] / 1000) + 0.15e-3
    return int(energy_J / (per_beat * SAFETY)), energy_J


# --- counts + the lever span -----------------------------------------------------
K2_COUNTS = dict(barrel=76, p1=8, w1=64, p2=8, esc_teeth=15)
LEVER_SPAN = 30.0

# rim furniture: these legitimately exit the plate (stems, crown, knob,
# pusher) and are exempt from every rim check
OUTSIDE_OK = ("stem", "m_stem", "k2_crown",
              "m_knob_line", "m_pusher")
