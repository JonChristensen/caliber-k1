"""K2 WINDING LINK — ONE crown, TWO positions (log 0023, SOLVED).

Position 1 (push): K1's base winding (crown wheel -> base ratchet), in
base_sweeps. Position 2 (pull): the base-level clutch drives a RISER up
the clear band north of both drums (both drums' north edge is y~71, rim
y81) to a HORIZONTAL transfer at module-bridge z (~34-36, above both
drums), into the module crown wheel -> module ratchet at plate center.
"""
from math import cos, sin, hypot, radians

from movement.solver import Sweep
from calibers.k1.revc import MESH_PAIRS, check_all as _core_check

from .brief import OUTSIDE_OK
from .layout import (K2_MODULE, MMZ, MODULE_R, base_sweeps, module_sweeps)


def winding_link_sweeps():
    """ONE crown at ~2 o'clock, TWO positions (SOLVED, log 0023). Both
    barrels wound from the NE flank cluster (clear of both drums):
      pos 1 (push): clutch -> base-level train -> base ratchet (0,41)
      pos 2 (pull): clutch -> riser -> module-level train -> module
                    ratchet (0,33)
    Shortest winding path 44.5mm."""
    mbr = MMZ["bridge"]; xz = (mbr[0] + 1.0, mbr[1]); bz = (13.0, 16.5)
    return [
        Sweep("cw2_core", 19.9, 41.5, 8.0, *xz),       # module crown wheel
        Sweep("wind_xfer", 30.4, 46.0, 6.0, *xz),      # module transfer
        Sweep("wind_riser", 40.9, 50.5, 3.0, 13.0, mbr[1]),  # NE-flank riser
        Sweep("m_clutch", 44.7, 55.2, 4.0, *bz),       # sliding clutch
        Sweep("m_setting_lever", 36.9, 61.5, 7.0, *bz, rotating=False),
        Sweep("m_detent", 52.5, 48.9, 4.0, *bz, rotating=False),
        Sweep("k2_crown", 56.0, 69.2, 7.0, 8.0, 18.0, rotating=False),
    ]


def winding_link_zone():
    return winding_link_sweeps()               # massing compat


def solve_winding_link(step_d=6):
    """Find a clean route for position 2: a riser on a clear FLANK (both
    drums cleared vertically) -> a transfer at module-bridge z inward to
    the module crown wheel -> the module ratchet. The crown follows the
    riser azimuth. Returns the placement, or None."""
    mbr = MMZ["bridge"]; xz = (mbr[0] + 1.0, mbr[1])
    mb = K2_MODULE["barrel"]                     # module barrel/ratchet (0,33)
    cbx, cby = 0.0, 41.0                         # base barrel
    base = base_sweeps(); mod = module_sweeps()
    def clear(name, x, y, r, z0, z1, extra):
        for o in base + mod + extra:
            if frozenset((name, o.name)) in MESH_PAIRS: continue
            if z1 <= o.z0+1e-9 or o.z1 <= z0+1e-9: continue
            if hypot(x-o.x, y-o.y) < r + o.r + 2.0: return False
        return hypot(x, y) + r <= MODULE_R - 2.0
    best = None
    for az in range(0, 360, step_d):
        ux, uy = cos(radians(az)), sin(radians(az))
        for R_r in range(44, 78, 3):             # riser radius from center
            rx, ry = R_r*ux, R_r*uy
            riser = Sweep("wind_riser", rx, ry, 3.0, 13.0, mbr[1])
            if not clear("wind_riser", rx, ry, 3.0, 13.0, mbr[1], []): continue
            # module crown wheel on the line riser->ratchet, meshing ratchet
            dx, dy = mb[0]-rx, mb[1]-ry; dl = hypot(dx, dy); ex, ey = dx/dl, dy/dl
            cwx, cwy = mb[0]-21.6*ex, mb[1]-21.6*ey     # 21.6 = ratchet+cw mesh
            if not clear("cw2_core", cwx, cwy, 8.0, *xz, [riser]): continue
            # one transfer wheel midway (riser-top -> cw), at module z
            txx, tyy = (rx+cwx)/2, (ry+cwy)/2
            xfer = Sweep("wind_xfer", txx, tyy, 6.0, *xz)
            if not clear("wind_xfer", txx, tyy, 6.0, *xz, [riser]): continue
            cw = Sweep("cw2_core", cwx, cwy, 8.0, *xz)
            # clutch + setting + detent just outboard of the riser
            clx, cly = rx+6*ux, ry+6*uy
            if not clear("m_clutch", clx, cly, 4.0, 13.0, 16.5, [riser, xfer, cw]): continue
            px, py = -uy, ux
            if not clear("m_setting_lever", clx+10*px, cly+10*py, 7.0, 13.0, 16.5, [riser,xfer,cw]): continue
            if not clear("m_detent", clx-10*px, cly-10*py, 4.0, 13.0, 16.5, [riser,xfer,cw]): continue
            path = hypot(rx - mb[0], ry - mb[1])      # riser -> barrel
            if best is None or path < best[0]:
                best = (path, dict(az=az, riser=(round(rx,1),round(ry,1)),
                        cw2=(round(cwx,1),round(cwy,1)),
                        xfer=(round(txx,1),round(tyy,1)),
                        clutch=(round(clx,1),round(cly,1))))
    return best


def k2_winding_gate():
    """The winding link vs BOTH plates' works + the module drum."""
    s = base_sweeps() + module_sweeps() + winding_link_sweeps()
    bad = [b for b in _core_check(s, 2.0) if "past rim" not in b]
    for sw in winding_link_sweeps():
        if sw.name in OUTSIDE_OK:
            continue
        if hypot(sw.x, sw.y) + sw.r > MODULE_R - 2.0:
            bad.append(f"{sw.name}: past the plate")
    return bad
