"""Regenerate every Milestone 1 part: STEP + STL per part, assembly STEP + SVG.

Usage:  python -m caliber_k1.export [out_dir]
"""

import sys
from math import cos, pi, sin
from pathlib import Path

from build123d import Compound, Pos, export_step, export_stl

from . import barrel, escapement, motion, stand, train_parts
from .parameters import (
    ARBOR, BARREL, SPRING, STAND, TOL,
    approx_winding_turns, pillar_height, spring_radial_span, spring_pitch,
    train_layout, train_periods,
)


def build_parts() -> dict:
    parts = {
        # Milestone 1 (drum now ships toothed for M2; drum(toothed=False)
        # reproduces the original plain M1 print)
        "drum": barrel.drum(),
        "cover": barrel.cover(),
        "arbor": barrel.arbor(),
        "mainspring": barrel.mainspring(),
        "ratchet_wheel": barrel.ratchet_wheel(),
        "click": barrel.click(),
        "winding_key": barrel.winding_key(),
        "lock_pin": barrel.lock_pin(),
        "top_plate": stand.top_plate(),
        "pillar": stand.pillar(),
        # Milestone 2 (rig_plate supersedes M1's bottom_plate)
        "rig_plate": train_parts.rig_plate(),
        "w1_arbor": train_parts.w1_arbor(),
        "w4_arbor": train_parts.w4_arbor(),
        "esc_arbor": train_parts.esc_arbor(),
        "wave_bridge": train_parts.wave_bridge(),
        # Milestone 3
        "escape_wheel": escapement.escape_wheel(),
        "pallet_lever": escapement.pallet_lever(),
        "roller": escapement.roller(),
        "balance_staff": escapement.balance_staff(),
        "balance_wheel": escapement.balance_wheel(),
        "hairspring": escapement.hairspring(),
        "tube_chaton": escapement.tube_chaton(),
        "platform": escapement.platform(),
        "balance_cock": escapement.balance_cock(),
        # Milestone 4
        "r1_arbor": motion.r1_arbor(),
        "r2_arbor": motion.r2_arbor(),
        "t_arbor": motion.t_arbor(),
        "m_arbor": motion.m_arbor(),
        "hour_wheel": motion.hour_wheel(),
        "deck_plate": motion.deck_plate(),
        "dial_cock": motion.dial_cock(),
        "winding_knob": motion.winding_knob(),
        "minute_hand": motion.minute_hand(),
        "hour_hand": motion.hour_hand(),
    }
    # label each shape so STEP viewers (Fusion, etc.) show real part names;
    # Pos * part deep-copies, so positioned assembly children inherit these
    for name, part in parts.items():
        part.label = name
    return parts


def build_assembly(parts: dict) -> Compound:
    """Assembled positions, bottom plate on the table at z=0."""
    p = STAND.plate_t                       # 5.0  top of bottom plate
    drum_z = p + TOL.endshake               # 5.5
    spring_z = drum_z + BARREL.floor_t + (BARREL.inner_h - SPRING.height) / 2
    cover_z = drum_z + BARREL.floor_t + BARREL.inner_h
    top_plate_z = p + pillar_height()       # 27.8
    square_z = ARBOR.pivot_len + (BARREL.floor_t + (BARREL.inner_h - SPRING.height) / 2) \
        + SPRING.height + ((BARREL.inner_h - SPRING.height) / 2 + BARREL.cover_t + TOL.endshake) \
        + ARBOR.pivot_len

    children = [
        Pos(0, 0, 0) * parts["rig_plate"],
        Pos(0, 0, drum_z) * parts["drum"],
        Pos(0, 0, spring_z) * parts["mainspring"],
        Pos(0, 0, 0) * parts["arbor"],
        Pos(0, 0, cover_z) * parts["cover"],
        Pos(0, 0, top_plate_z) * parts["top_plate"],
        Pos(0, 0, square_z) * parts["ratchet_wheel"],
        Pos(0, 0, top_plate_z + STAND.plate_t) * parts["click"],
    ]
    for x, y in stand._pillar_positions():
        children.append(Pos(x, y, p) * parts["pillar"])
    # lock pin dropped through its top-plate hole
    pin_x = stand.PIN_R * cos(stand.PIN_ANGLE * pi / 180)
    pin_y = stand.PIN_R * sin(stand.PIN_ANGLE * pi / 180)
    pin_len = STAND.plate_t + TOL.endshake + BARREL.cover_t + 1.5
    children.append(
        Pos(pin_x, pin_y, top_plate_z + STAND.plate_t - pin_len) * parts["lock_pin"]
    )
    # going train + wave bridge
    lay = train_layout()
    az = train_parts.assembly_positions()
    for key, part_name in (("w1", "w1_arbor"), ("w4", "w4_arbor"),
                           ("esc", "esc_arbor")):
        x, y = lay[key]
        children.append(Pos(x, y, az["arbor_z0"]) * parts[part_name])
    children.append(Pos(0, 0, az["bridge_z"]) * parts["wave_bridge"])
    # escapement storey
    from .parameters import M3_LEVELS, m3_layout
    m3 = m3_layout()
    E, B = m3["E"], m3["P"]
    Bc = m3["B"]
    children += [
        Pos(E[0], E[1], p + M3_LEVELS["esc_wheel_z"]) * parts["escape_wheel"],
        Pos(B[0], B[1], p + M3_LEVELS["lever_z"]) * parts["pallet_lever"],
        Pos(Bc[0], Bc[1], p + M3_LEVELS["lever_z"]) * parts["roller"],
        Pos(Bc[0], Bc[1], p + 18.0) * parts["balance_staff"],
        Pos(Bc[0], Bc[1], p + M3_LEVELS["balance_z"]) * parts["balance_wheel"],
        Pos(Bc[0], Bc[1], p + M3_LEVELS["hairspring_z"]) * parts["hairspring"],
        Pos(Bc[0], Bc[1], p + 15.5) * parts["tube_chaton"],
        Pos(0, 0, p + M3_LEVELS["platform_z"]) * parts["platform"],
        Pos(0, 0, p) * parts["balance_cock"],
    ]
    # motion works + dial storey (Milestone 4)
    from .parameters import M4_LEVELS, m4_layout
    m4 = m4_layout()
    children += [
        Pos(m4["R1"][0], m4["R1"][1], p - 4.0) * parts["r1_arbor"],
        Pos(m4["R2"][0], m4["R2"][1], p + 28.7) * parts["r2_arbor"],
        Pos(m4["T"][0], m4["T"][1], p + 28.7) * parts["t_arbor"],
        Pos(m4["M"][0], m4["M"][1], p + 28.7) * parts["m_arbor"],
        Pos(m4["T"][0], m4["T"][1], p + M4_LEVELS["mesh4_z"]) * parts["hour_wheel"],
        Pos(0, 0, p + M4_LEVELS["deck_plate_z"]) * parts["deck_plate"],
        Pos(0, 0, p + M4_LEVELS["dial_cock_z"]) * parts["dial_cock"],
        Pos(m4["T"][0], m4["T"][1], p + M4_LEVELS["hands_z"]) * parts["minute_hand"],
        Pos(m4["T"][0], m4["T"][1], p + M4_LEVELS["mesh4_z"] + 5.0) * parts["hour_hand"],
        Pos(0, 0, square_z + 2) * parts["winding_knob"],
    ]
    return Compound(label="caliber_k1_milestone2", children=children)


def export_svg_views(assembly, out: Path):
    """Best-effort review drawings; never fail the export over SVG."""
    try:
        from build123d import ExportSVG, LineType

        for name, viewport in [("assembly_iso", (120, -100, 90)),
                               ("assembly_top", (0, 0, 200))]:
            visible, hidden = assembly.project_to_viewport(viewport)
            exp = ExportSVG(scale=3)
            exp.add_layer("visible")
            exp.add_layer("hidden", line_type=LineType.ISO_DASH, line_weight=0.2)
            exp.add_shape(visible, layer="visible")
            exp.add_shape(hidden, layer="hidden")
            exp.write(str(out / f"{name}.svg"))
    except Exception as e:  # noqa: BLE001
        print(f"  (svg views skipped: {e})")


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out")
    out.mkdir(parents=True, exist_ok=True)

    parts = build_parts()
    for name, part in parts.items():
        export_step(part, str(out / f"{name}.step"))
        export_stl(part, str(out / f"{name}.stl"))
        bb = part.bounding_box()
        print(f"  {name:14s} {bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:5.1f} mm"
              f"  vol {part.volume / 1000:7.1f} cm3/1000")

    assembly = build_assembly(parts)
    export_step(assembly, str(out / "assembly.step"))
    export_svg_views(assembly, out)

    print("\n--- design report ---")
    print(f"spring radial span   : {spring_radial_span():.1f} mm")
    print(f"printed coil pitch   : {spring_pitch():.2f} mm (strip {SPRING.thickness} mm)")
    print(f"spring strip length  : {barrel.spring_strip_length():.0f} mm")
    print(f"approx winding turns : {approx_winding_turns():.1f}")
    print(f"arbor length         : {barrel.arbor_total_length():.1f} mm")
    print(f"stand height overall : {STAND.plate_t * 2 + pillar_height():.1f} mm")
    periods = train_periods()
    print("--- train ---")
    print(f"drum period          : {periods['drum']:.2f} s ({periods['drum']/60:.2f} min/rev)")
    print(f"W1 period            : {periods['w1']:.2f} s")
    print(f"W4 (seconds) period  : {periods['w4']:.4f} s")
    print(f"escape pinion period : {periods['esc']:.4f} s")
    lay = train_layout()
    for k in ("w1", "w4", "esc"):
        print(f"{k:4s} center          : ({lay[k][0]:6.1f}, {lay[k][1]:6.1f})")
    print(f"exports written to   : {out.resolve()}")


if __name__ == "__main__":
    main()
