"""The FDM print kit: every part as its own STL + a manifest with
material, quantity, orientation and spares. Jon prints from exports/print/."""
import os

from build123d import export_stl

from caliber_k1 import revc_parts as rp
from caliber_k1 import revc_dial_parts as dp

os.makedirs("exports/print", exist_ok=True)

# (file, builder, qty, material, orientation + notes)
KIT = [
    ("mainplate", rp.mainplate_c, 1, "PLA",
     "dial face DOWN; tree supports in the dial pockets only"),

    ("drum", rp.drum_c, 1, "PLA",
     "gear band DOWN with brim; supports under the band overhang"),
    ("drum_cover", rp.drum_cover_c, 1, "PLA", "flat, either face"),
    ("barrel_arbor", rp.barrel_arbor_c, 1, "PLA",
     "square end UP (prints vertical); brim"),
    ("mainspring", rp.mainspring_c, 1, "PETG ONLY",
     "flat spiral as printed; 100% infill, 0.2 layers; print 2 spares"),
    ("ratchet", rp.ratchet_c, 1, "PLA", "flat"),
    ("click", rp.click_c, 1, "PETG preferred",
     "flat, pegs UP; flexure arm — PLA acceptable short-term"),
    ("crown_wheel", rp.crown_wheel_c, 1, "PLA", "slots UP (top face down)"),
    ("crown_stud", rp.crown_stud_c, 1, "PLA", "head DOWN"),
    ("stem_and_crown", rp.stem_c, 1, "PLA",
     "crown face DOWN, axis vertical; supports under pinion"),
    ("stem_clip", rp.stem_clip_c, 1, "PETG preferred", "flat; print 3"),
    ("minute_arbor", rp.minute_arbor_c, 1, "PLA",
     "vertical, small end UP; brim; print a spare"),
    ("third_arbor", rp.third_arbor_c, 1, "PLA", "vertical; brim; spare"),
    ("fourth_arbor", rp.fourth_arbor_c, 1, "PLA", "vertical; brim; spare"),
    ("escape_arbor", rp.escape_arbor_c, 1, "PLA", "vertical; brim; spare"),
    ("escape_wheel", rp.club_escape_wheel_c, 1, "PLA",
     "flat; print 3 (bench tuning consumes them)"),
    ("pallet_fork", rp.swiss_lever_c, 1, "PLA",
     "body flat, pivots vertical need supports; print 3"),
    ("bay_strap", rp.bay_strap_c, 1, "PLA", "flat; print 2"),
    ("roller", rp.roller_c, 1, "PLA", "flat, crescent side down; print 2"),
    ("balance_staff", rp.balance_staff_c, 1, "PLA",
     "vertical; or cut from O3 steel rod (the register option)"),
    ("balance_wheel", rp.balance_wheel_c, 1, "PLA", "flat"),
    ("hairspring", rp.hairspring_c, 1, "PETG ONLY",
     "flat; 0.45 walls = single-line: tune flow; print 3 spares"),
    ("balance_cock", rp.balance_cock_c, 1, "PLA",
     "arm flat, columns UP; supports under the stud post"),
    ("stand_foot", rp.stand_foot_c, 3, "PLA", "vertical"),
    ("center_post", dp.center_post_d, 1, "PLA",
     "vertical; or O3 steel rod (register)"),
    ("cannon", dp.cannon_d, 1, "PLA", "pipe vertical, hand-seat UP"),
    ("hour_wheel", dp.hour_wheel_d, 1, "PLA", "pipe vertical"),
    ("motion_arbor", dp.motion_arbor_d, 1, "PLA", "vertical"),
    ("moon_w1", dp.w1_d, 1, "PLA", "flat"),
    ("moon_w2", dp.w2_d, 1, "PLA", "vertical shaft"),
    ("moon_disc", dp.moon_disc_d, 1, "PLA",
     "moons DOWN (two-color swap at 0.3 if using AMS)"),
    ("transfer_pinion", dp.xfer_pinion_d, 1, "PETG preferred",
     "flat; slit collet is the hand-setting slip; print 2"),
    ("transfer_idler", dp.idler_d, 2, "PLA", "flat"),
    ("dial_platform", dp.dial_platform_d, 1, "PLA", "flat, proud face down"),
    ("dial_sheet", dp.dial_sheet_d, 1, "PLA (face color!)",
     "face DOWN; engraved markers paint-fill at the bench"),
    ("minute_hand", dp.minute_hand_d, 1, "PLA (hand color)", "flat; print 2"),
    ("hour_hand", dp.hour_hand_d, 1, "PLA (hand color)", "flat; print 2"),
]


def arbor_posts():
    from caliber_k1.revc_dial import post_specs
    return [(f"arbor_post_{n}", (lambda L=(top - 0.1 - tip): dp.arbor_post_d(L)),
             1, "PLA", "vertical; or O2 steel pin (register)")
            for (n, x, y, tip, top) in post_specs()]


# the wave bridge: one skeleton show plate
KIT.append(("bridge_wave", rp.bridge_c, 1, "PLA (show face — pick a color!)",
            "SHOW FACE DOWN (pillars point up); 100%% infill; supports "
            "only in the ratchet pocket + stem tunnel; brim on"))

rows = []
for name, fn, qty, mat, note in KIT + arbor_posts():
    part = fn()
    export_stl(part, f"exports/print/{name}.stl", tolerance=0.02)
    rows.append((name, qty, mat, note))
with open("exports/print/MANIFEST.md", "w") as f:
    f.write("# Caliber K1 rev C — print kit (movement r6)\n\n"
            "Hardware (not printed): M3x8 x7 + nuts (pillars, cock, feet), "
            "M2 x6 (strap, click, platform), superlube on every pivot.\n\n"
            "| part | qty | material | orientation / notes |\n"
            "|---|---|---|---|\n")
    for name, qty, mat, note in rows:
        f.write(f"| {name} | {qty} | {mat} | {note} |\n")
print(f"print kit: {len(rows)} part files + MANIFEST.md")
