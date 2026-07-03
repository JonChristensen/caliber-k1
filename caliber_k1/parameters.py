"""Caliber K1 — master parameter file.

Every dimension in the caliber derives from the values here. Change a value,
re-run `python -m caliber_k1.export`, and every affected part regenerates.

Units: millimeters, degrees.

Naming follows horological convention where one exists (barrel, arbor,
click, ratchet). "Stand" parts are the Milestone 1 test fixture, not part
of the final movement.
"""

from dataclasses import dataclass
from math import pi


# ---------------------------------------------------------------------------
# Global print/fit tolerances (tuned per printer+material; H2C defaults)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Tolerances:
    # Radial clearance for a shaft spinning in a printed bushing.
    pivot_clearance: float = 0.20
    # Clearance for parts that slide together but shouldn't rattle (covers, keys).
    snug_clearance: float = 0.15
    # Clearance for a press/no-slip fit (squares, D-bores that must transmit torque).
    drive_clearance: float = 0.10
    # Vertical clearance between rotating parts and static plates.
    endshake: float = 0.50


TOL = Tolerances()


# ---------------------------------------------------------------------------
# Movement-wide targets
# ---------------------------------------------------------------------------

MOVEMENT_DIAMETER = 150.0     # main plate diameter (H2C bed allows up to ~300)
GEAR_MODULE = 1.0             # train gear module (Laimer proved >=0.7 printable)
BALANCE_FREQ_HZ = 1.0         # 1 Hz beat: majestic desk-scale tick
TARGET_RUNTIME_MIN = 60       # goal for the finished going train


# ---------------------------------------------------------------------------
# Milestone 2 — Going train
#
# Timing chain, all ratios exact by construction:
#   drum (72t) --> W1 pinion (16)     : x4.5
#   W1 wheel (50t) --> W4 pinion (12) : x4.1667
#   W4 wheel (24t) --> escape pinion (12) : x2
#
# The spring yields ~3.2 usable turns. Drum period is set to 1125 s
# (18.75 min/rev) so that 3.2 turns x 1125 s = 60 min runtime, and:
#   W4 period = 1125 / 4.5 / (50/12) = exactly 60 s  --> seconds arbor
#   escape period = 30 s --> a 30-tooth escape wheel at 1 Hz beat (M3)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Train:
    module: float = GEAR_MODULE
    drum_teeth: int = 72              # ring gear cut on the drum's lower band
    w1_wheel: int = 50
    w1_pinion: int = 16
    w4_wheel: int = 24
    w4_pinion: int = 12
    esc_pinion: int = 12
    esc_wheel: int = 30               # Milestone 3 (sets 30 s escape period)
    backlash: float = 0.15            # tangential, at the pitch circle
    wheel_addendum: float = 1.0       # x module
    wheel_dedendum: float = 1.3       # x module
    pivot_d: float = 3.0              # printed pivots for rig v1 (steel later)
    pinion_h: float = 5.0
    wheel_h: float = 4.0
    drum_band_h: float = 5.0          # toothed band height at drum bottom


TRAIN = Train()


def train_layout() -> dict:
    """XY centers of train arbors + wave-bridge feet, barrel at (0, 0).

    Angles chosen so every wheel clears the drum (tip r37), the three
    stand pillars (r43, Ø10), and the rig plate rim (r75). Every clearance
    is asserted pairwise in tests/test_geometry.py.
    """
    from math import cos, sin, radians

    m = TRAIN.module
    d_w1 = m * (TRAIN.drum_teeth + TRAIN.w1_pinion) / 2       # 44.0
    d_w1_w4 = m * (TRAIN.w1_wheel + TRAIN.w4_pinion) / 2      # 31.0
    d_w4_esc = m * (TRAIN.w4_wheel + TRAIN.esc_pinion) / 2    # 18.0

    # The whole train sits in the pillar gap centered on azimuth 245.7°
    # (pillars are at 65.7/185.7/305.7), then folds counterclockwise.
    a1 = radians(245.7)
    w1 = (d_w1 * cos(a1), d_w1 * sin(a1))
    a2 = radians(160)
    w4 = (w1[0] + d_w1_w4 * cos(a2), w1[1] + d_w1_w4 * sin(a2))
    a3 = radians(120)
    esc = (w4[0] + d_w4_esc * cos(a3), w4[1] + d_w4_esc * sin(a3))
    return {
        "w1": w1,
        "w4": w4,
        "esc": esc,
        "foot_a": (12.0, -51.0),      # wave-bridge feet (integral posts)
        "foot_b": (-62.7, -2.6),
    }


# Vertical stack above the rig plate top (z=0), keeping the whole train
# UNDER the Milestone 1 spider plate (whose underside sits at z=22.8):
#   drum gear band 0.5..5.5 | W1 pinion 0.5..5.5 | W1 wheel 6..10
#   W4 pinion 6..11 | W4 wheel 11.5..15.5 | esc pinion 11.5..16.5
#   bridge 17..21  (1.8 mm clear of the spider underside)
TRAIN_LEVELS = {
    "w1_pinion_z": 0.5,
    "w1_wheel_z": 6.0,
    "w4_pinion_z": 6.0,
    "w4_wheel_z": 11.5,
    "esc_pinion_z": 11.5,
    "bridge_z": 17.0,
    "bridge_t": 4.0,
    "post_h": 17.0,
}


def train_periods() -> dict:
    """Rotation period of each arbor in seconds, from the 60 min runtime goal."""
    drum_period = TARGET_RUNTIME_MIN * 60 / approx_winding_turns_nominal()
    w1 = drum_period / (TRAIN.drum_teeth / TRAIN.w1_pinion)
    w4 = w1 / (TRAIN.w1_wheel / TRAIN.w4_pinion)
    esc = w4 / (TRAIN.w4_wheel / TRAIN.esc_pinion)
    return {"drum": drum_period, "w1": w1, "w4": w4, "esc": esc}


def approx_winding_turns_nominal() -> float:
    """The design-point usable turns (3.2) that set the drum period."""
    return 3.2


# ---------------------------------------------------------------------------
# Milestone 1 — Going barrel
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Barrel:
    drum_outer_d: float = 72.0        # outer diameter of the barrel drum
    wall_t: float = 3.0               # drum wall thickness
    floor_t: float = 2.4              # drum floor thickness
    inner_h: float = 17.0             # interior height (mainspring space)
    cover_t: float = 2.4              # snap-on cover thickness
    cover_lip_h: float = 2.0          # cover locating lip depth into drum
    spring_slot_w: float = 2.4        # slot in drum wall for the spring's outer tab
    spring_slot_h: float = 16.5       # must exceed mainspring strip height
    lock_pin_hole_d: float = 4.0      # drum-lock pull pin passes cover -> top plate

    @property
    def inner_d(self) -> float:
        return self.drum_outer_d - 2 * self.wall_t

    @property
    def total_h(self) -> float:
        return self.floor_t + self.inner_h + self.cover_t


@dataclass(frozen=True)
class Arbor:
    hub_d: float = 22.0               # hub the mainspring's inner end grips (D-drive)
    hub_flat_depth: float = 4.0       # depth of the D-flat on the hub
    pivot_d: float = 8.0              # printed pivots, run in stand bushings
    pivot_len: float = 5.5            # engagement length in each bushing
    # Winding square drives ratchet wheel + key. Its DIAGONAL must pass the
    # top-plate bushing hole during assembly: 5.5 * sqrt(2) = 7.78 < 8.4. ✓
    square_side: float = 5.5
    square_len: float = 12.0          # length above top plate: ratchet + key grip


@dataclass(frozen=True)
class Mainspring:
    thickness: float = 1.6            # PETG strip thickness (torque tuning knob #1)
    height: float = 16.0              # strip height (torque tuning knob #2)
    coils: int = 6                    # printed (relaxed) coil count
    inner_tab: str = "D-ring"         # inner end: ring with D-bore over arbor hub
    outer_tab_w: float = 2.0          # outer end: radial tab into drum wall slot
    outer_tab_len: float = 4.5


@dataclass(frozen=True)
class Ratchet:
    wheel_d: float = 40.0             # ratchet wheel tip diameter
    tooth_count: int = 24
    tooth_depth: float = 3.0
    wheel_t: float = 5.0
    click_arm_len: float = 22.0       # flexure click: arm length sets stiffness
    click_arm_t: float = 2.0
    click_t: float = 5.0


@dataclass(frozen=True)
class Stand:
    plate_d: float = 100.0            # round plates, Milestone 1 fixture
    plate_t: float = 5.0
    pillar_d: float = 10.0
    pillar_count: int = 4
    pillar_bolt: str = "M3"           # 4x M3x30 + nuts — the entire metal BOM
    bolt_clear_d: float = 3.4
    nut_pocket_w: float = 5.7         # M3 hex nut across-flats + fit
    nut_pocket_t: float = 2.6

    @property
    def pillar_circle_d(self) -> float:
        return self.plate_d - self.pillar_d - 4.0


BARREL = Barrel()
ARBOR = Arbor()
SPRING = Mainspring()
RATCHET = Ratchet()
STAND = Stand()


# Pillar height = barrel height + endshake both sides.
def pillar_height() -> float:
    return BARREL.total_h + 2 * TOL.endshake


# ---------------------------------------------------------------------------
# Derived sanity values (also asserted in tests/)
# ---------------------------------------------------------------------------

def spring_radial_span() -> float:
    """Radial space available to the mainspring inside the drum."""
    return (BARREL.inner_d / 2) - (ARBOR.hub_d / 2)


def spring_pitch() -> float:
    """Relaxed printed coil pitch: fill the annulus evenly, leave breathing gaps."""
    return spring_radial_span() / (SPRING.coils + 1)


def approx_winding_turns() -> float:
    """Rough usable winding turns: annular area / (strip thickness * mean length).

    Classic estimate — turns available ≈ turns when spring fills half the
    annulus wound tight on the arbor minus relaxed-against-wall turns.
    Good enough to sanity-check the design; reality is measured on the bench.
    """
    r_arbor = ARBOR.hub_d / 2
    r_wall = BARREL.inner_d / 2
    area = pi * (r_wall**2 - r_arbor**2)
    strip_len = area / 2 / SPRING.thickness  # strip occupies half the annulus
    turns_wound = (
        ((r_arbor**2 + strip_len * SPRING.thickness / pi) ** 0.5) - r_arbor
    ) / SPRING.thickness
    turns_relaxed = (
        (r_wall - ((r_wall**2 - strip_len * SPRING.thickness / pi) ** 0.5))
        / SPRING.thickness
    )
    return turns_wound - turns_relaxed
