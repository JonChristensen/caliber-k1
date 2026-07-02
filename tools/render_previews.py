"""Render PNG previews of exported STLs (matplotlib, no GPU needed).

Usage: python tools/render_previews.py [out_dir]
Writes <out_dir>/preview_<part>.png and a combined contact sheet.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def render(stl_path: Path, ax, elev=35, azim=-60):
    mesh = trimesh.load_mesh(stl_path)
    tris = mesh.vertices[mesh.faces]
    # simple lambert shading off a fixed light
    normals = mesh.face_normals
    light = np.array([0.4, -0.3, 0.85])
    light = light / np.linalg.norm(light)
    shade = np.clip(normals @ light, 0.15, 1.0)
    colors = plt.cm.cividis(0.25 + 0.6 * shade)
    coll = Poly3DCollection(tris, facecolors=colors, edgecolors="none")
    ax.add_collection3d(coll)
    lo, hi = mesh.bounds
    center, span = (lo + hi) / 2, max(hi - lo) / 2 * 1.15
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(stl_path.stem, fontsize=9)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out")
    stls = sorted(p for p in out.glob("*.stl"))
    # contact sheet
    cols = 4
    rows = (len(stls) + cols - 1) // cols
    fig = plt.figure(figsize=(4 * cols, 4 * rows))
    for i, p in enumerate(stls):
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        render(p, ax)
    fig.tight_layout()
    fig.savefig(out / "preview_all_parts.png", dpi=80)
    print(f"wrote {out / 'preview_all_parts.png'}")

    # top view of tricky 2D-critical parts
    for name in ("mainspring", "ratchet_wheel", "click", "top_plate", "cover"):
        p = out / f"{name}.stl"
        if p.exists():
            fig = plt.figure(figsize=(6, 6))
            ax = fig.add_subplot(111, projection="3d")
            render(p, ax, elev=88, azim=-90)
            fig.savefig(out / f"preview_top_{name}.png", dpi=90)
            plt.close(fig)
    print("wrote top views")


if __name__ == "__main__":
    main()
