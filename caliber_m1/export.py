"""Regenerate every Milestone 1 part: STEP + STL per part, assembly STEP + SVG.

Usage:  python -m caliber_m1.export [out_dir]
"""

import sys
from math import cos, pi, sin
from pathlib import Path

from build123d import Compound, Pos, export_step, export_stl

from . import barrel, stand
from .parameters import (
    ARBOR, BARREL, SPRING, STAND, TOL,
    approx_winding_turns, pillar_height, spring_radial_span, spring_pitch,
)


def build_parts() -> dict:
    return {
        "drum": barrel.drum(),
        "cover": barrel.cover(),
        "arbor": barrel.arbor(),
        "mainspring": barrel.mainspring(),
        "ratchet_wheel": barrel.ratchet_wheel(),
        "click": barrel.click(),
        "winding_key": barrel.winding_key(),
        "lock_pin": barrel.lock_pin(),
        "bottom_plate": stand.bottom_plate(),
        "top_plate": stand.top_plate(),
        "pillar": stand.pillar(),
    }


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
        Pos(0, 0, 0) * parts["bottom_plate"],
        Pos(0, 0, drum_z) * parts["drum"],
        Pos(0, 0, spring_z) * parts["mainspring"],
        Pos(0, 0, 0) * parts["arbor"],
        Pos(0, 0, cover_z) * parts["cover"],
        Pos(0, 0, top_plate_z) * parts["top_plate"],
        Pos(0, 0, square_z) * parts["ratchet_wheel"],
        Pos(0, 0, top_plate_z + STAND.plate_t) * parts["click"],
        Pos(0, 0, square_z + ARBOR.square_len + 3) * parts["winding_key"],
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
    return Compound(label="caliber_m1_milestone1", children=children)


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
    print(f"exports written to   : {out.resolve()}")


if __name__ == "__main__":
    main()
