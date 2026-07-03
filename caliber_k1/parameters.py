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

MOVEMENT_DIAMETER = 170.0     # main plate diameter (grew for the balance; H2C fits ~300)
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


# ---------------------------------------------------------------------------
# Milestone 3 — Escapement + balance ("the jewel in the wave")
#
# Architecture: the escapement is a storey ABOVE the wave bridge.
#   z 17-21  wave bridge (M2)                  z 26.5-29.5 lever + roller
#   z 23-26  escape wheel                      z 31-34     escapement platform
#   z 35-40  balance ring (sweeps the crest)   z 41-44     hairspring
#   z ~45-49 balance cock arm
# Balance center = decor.wave_tube_center() — CI-enforced contract.
#
# Escapement type: PIN-PALLET lever (Roskopf). Chosen for FDM: cylindrical
# pallet pins + pointed teeth tolerate print error far better than club-tooth
# Swiss lever faces; proven in printed-watch practice. Upgrade path later.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Escapement:
    wheel_teeth: int = 30             # = TRAIN.esc_wheel (30 s/rev, 1 Hz)
    wheel_tip_r: float = 16.0
    wheel_root_r: float = 12.5
    tooth_lean_deg: float = 4.0       # face draw angle
    wheel_t: float = 3.0
    pin_d: float = 2.0                # pallet pins (printed; 2mm steel later)
    engage: float = 1.6               # pin dip inside the tip circle
    span_half_deg: float = 21.0       # pins subtend 3.5 tooth spaces (42 deg)
    pallet_offset_deg: float = 25.0   # pallet line rotated off the balance line
    lever_swing_deg: float = 5.5      # each side of center (banking-limited)
    fork_slot_w: float = 3.1          # impulse pin 2.5 + play
    roller_r: float = 5.5             # impulse pin orbit radius
    impulse_pin_d: float = 2.5


@dataclass(frozen=True)
class Balance:
    ring_od: float = 50.0
    ring_id: float = 40.0
    ring_h: float = 5.0
    staff_d: float = 5.0
    pivot_d: float = 2.5
    timing_holes: int = 6             # M3 rim holes; nuts = timing weights
    # hairspring (printed, PLA — stiffness sets the rate)
    hs_t: float = 0.45                # strip thickness (single-ish wall)
    hs_h: float = 4.0
    hs_r_in: float = 8.0
    hs_r_out: float = 24.0
    hs_coils: int = 11
    pla_modulus_gpa: float = 3.3      # +-20%; bench-trimmed via rim nuts
    pla_density: float = 1.24e-3      # g/mm^3


ESC = Escapement()
BAL = Balance()

M3_LEVELS = {
    "esc_wheel_z": 23.0,
    "lever_z": 26.5, "lever_t": 3.0,
    "platform_z": 31.0, "platform_t": 3.0,
    "balance_z": 35.0,
    "hairspring_z": 41.0,
    "cock_arm_z": 45.0, "cock_arm_t": 4.0,
}


def balance_inertia() -> float:
    """Ring inertia in kg*m^2 (spokes ~+10%)."""
    r_o, r_i = BAL.ring_od / 2, BAL.ring_id / 2
    vol = pi * (r_o**2 - r_i**2) * BAL.ring_h            # mm^3
    mass = vol * BAL.pla_density * 1e-3                  # kg
    r_g2 = (r_o**2 + r_i**2) / 2 * 1e-6                  # m^2
    return 1.10 * mass * r_g2


def hairspring_length() -> float:
    return pi * (BAL.hs_r_in + BAL.hs_r_out) * BAL.hs_coils  # mm


def hairspring_stiffness() -> float:
    """Torsional stiffness k = E*I/L in N*m/rad."""
    E = BAL.pla_modulus_gpa * 1e9
    I_sec = BAL.hs_h * BAL.hs_t**3 / 12 * 1e-12          # m^4
    return E * I_sec / (hairspring_length() * 1e-3)


def predicted_period() -> float:
    """T = 2*pi*sqrt(I/k) — must land near 1.0 s (trim via rim nuts)."""
    return 2 * pi * (balance_inertia() / hairspring_stiffness()) ** 0.5


def m3_layout() -> dict:
    """Escapement geometry, all derived. E=escape, P=pallet, B=balance."""
    from math import atan2, cos, sin, radians
    from .decor import wave_tube_center

    lay = train_layout()
    path = [lay["foot_a"], lay["w1"], lay["w4"], lay["esc"], lay["foot_b"]]
    E = lay["esc"]
    B = wave_tube_center(path)
    ang_EB = atan2(B[1] - E[1], B[0] - E[0])
    # pallet center: on a ray rotated off the balance line, at locking distance
    rho = ESC.wheel_tip_r + ESC.pin_d / 2 - ESC.engage      # pin orbit about E
    a = rho / cos(radians(ESC.span_half_deg))
    ang_EP = ang_EB + radians(ESC.pallet_offset_deg)
    P = (E[0] + a * cos(ang_EP), E[1] + a * sin(ang_EP))
    # pallet pins: symmetric about the E->P line, on the rho circle
    pins = []
    for s in (+1, -1):
        th = ang_EP + s * radians(ESC.span_half_deg)
        pins.append((E[0] + rho * cos(th), E[1] + rho * sin(th)))
    # unit vectors
    u_pb = ((B[0] - P[0]), (B[1] - P[1]))
    L_pb = (u_pb[0] ** 2 + u_pb[1] ** 2) ** 0.5
    u_pb = (u_pb[0] / L_pb, u_pb[1] / L_pb)
    u_pe = ((P[0] - E[0]) / a, (P[1] - E[1]) / a)
    n_pe = (-u_pe[1], u_pe[0])
    # platform supports: two plate-rooted pillars in verified-open zones
    # (clear of drum r37, W1 r26 sweep, W4 r13 sweep, escape wheel r16,
    # the lever fan, the crest art, and the balance staff)
    pillar_a = (-72.0, -28.0)
    pillar_b = (-60.0, -44.0)
    cock_foot = (-28.0, -73.4)
    return {"E": E, "B": B, "P": P, "pins": pins, "fork_len": L_pb,
            "u_pb": u_pb, "n_pe": n_pe, "pillar_a": pillar_a,
            "pillar_b": pillar_b, "cock_foot": cock_foot}


# ---------------------------------------------------------------------------
# Milestone 4 — Motion works (time display) + module interface
#
# The train has no 1-hour arbor, so time display derives from W1 (250 s/rev):
#   W1 pinion (16, already cut) --> R wheel (48)  : x3.0   -> 750 s
#   R pinion (10) --> T wheel (48)                : x4.8   -> 3600 s = MINUTE
#   cannon (12) --> M wheel (36), M pinion (10) --> hour wheel (40) : x12
# Total W1->minute = 14.4 exactly; minute->hour = 12 exactly.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MotionWorks:
    r1_wheel: int = 24    # 1.5 x 3.2 x 3.0 = 14.4 exact (log 0007:
    r1_pinion: int = 10   # R1 shrunk to pass the foot_a/cock gap;
    r2_wheel: int = 32    # the big wheel moved up to the open deck)
    r2_pinion: int = 10
    t_wheel: int = 30                 # the minute arbor ("dial center")
    cannon: int = 12
    m_wheel: int = 36
    m_pinion: int = 10
    hour_wheel: int = 40


MOTION = MotionWorks()


def motion_periods() -> dict:
    w1 = train_periods()["w1"]
    minute = w1 * (MOTION.r1_wheel / TRAIN.w1_pinion) \
        * (MOTION.r2_wheel / MOTION.r1_pinion) * (MOTION.t_wheel / MOTION.r2_pinion)
    hour = minute * (MOTION.m_wheel / MOTION.cannon) * (MOTION.hour_wheel / MOTION.m_pinion)
    return {"minute_s": minute, "hour_s": hour}


# --- M4 upper-deck layout (log 0006/0007): verified coordinates -------------
# Deck plate z28.2-30.2 flies 0.4 over the spider; R1 climbs from L2 to the
# deck; all motion-works meshing happens at z>=30.5 where the plate is open.
M4_LEVELS = {
    "deck_plate_z": 28.2, "deck_plate_t": 2.0,
    "r1_wheel_z": 10.5,                  # meshes W1's second 16t pinion
    "mesh1_z": 30.5,                     # R1 pinion 10 -> R2 wheel 24 (h5)
    "mesh2_z": 36.0,                     # R2 pinion 10 -> T wheel 30 (h5)
    "mesh3_z": 41.5,                     # cannon 12 -> M wheel 36 (h5)
    "mesh4_z": 47.0,                     # M pinion 10 -> hour wheel 40 (h5)
    "dial_cock_z": 52.5, "dial_cock_t": 3.0,
    "hands_z": 56.0,
}


def m4_layout() -> dict:
    """Motion-works arbor centers (mesh distances exact by construction)."""
    from math import cos, sin, radians
    W1 = train_layout()["w1"]
    R1 = (W1[0] + 20 * cos(radians(-65)), W1[1] + 20 * sin(radians(-65)))
    T = (14.8, -36.8)                    # the dial center
    # R2: intersection of circle(R1, 21) and circle(T, 20), upper branch
    dx, dy = T[0] - R1[0], T[1] - R1[1]
    d = (dx * dx + dy * dy) ** 0.5
    a = (21**2 - 20**2 + d * d) / (2 * d)
    h = (21**2 - a * a) ** 0.5
    mx, my = R1[0] + a * dx / d, R1[1] + a * dy / d
    R2 = (mx + h * dy / d, my - h * dx / d)   # outboard branch
    return {
        "R1": R1, "R2": R2, "T": T,
        "M": (T[0] + 24, T[1]),          # 24.0 from T
        "deck_pillar_a": (57.0, -17.0),  # plate-rooted, carry deck + cock
        "deck_pillar_b": (2.0, -79.0),
    }


# --- M5 moon phase (kickoff): two-stage lunation train ----------------------
# hour arbor (0.5 d/rev) --46/9--> --104/9--> moon disc
# lunation modeled 29.5308642 d vs 29.530588853 true: 23.8 s/lunation,
# ~1 day of phase error in 290 years. Found by exhaustive search (<=120t).
@dataclass(frozen=True)
class MoonPhase:
    s1_wheel: int = 46
    s1_pinion: int = 9
    s2_wheel: int = 104
    s2_pinion: int = 9


MOON = MoonPhase()


def lunation_days() -> float:
    return 0.5 * (MOON.s1_wheel / MOON.s1_pinion) * (MOON.s2_wheel / MOON.s2_pinion)
