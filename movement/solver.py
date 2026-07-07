"""Whole-movement solver machinery: swept envelopes + the global
clearance check. The discipline every caliber inherits: nothing is
geometry until a layout of Sweeps passes the check.

Calibers bind their own rim radius, mesh-pair exemptions and rim
exemptions (e.g. a stem that legitimately exits the rim toward its
crown) — see calibers.k1.revc.check_all for the K1 binding.
"""
from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class Sweep:
    """A part's swept envelope: cylinder (rotating) or disc (static)."""
    name: str
    x: float
    y: float
    r: float
    z0: float
    z1: float
    rotating: bool = True


def check_sweeps(sweeps, clearance=2.0, rim=None, mesh_pairs=frozenset(),
                 rim_exempt=()):
    """THE global test: every pair involving a rotating part must clear
    radially (if z-bands overlap) and stay inside the rim — EXCEPT
    meshing pairs, whose intentional engagement is verified by
    phase-aligned probes at part level instead."""
    bad = []
    if rim is not None:
        for s in sweeps:
            if s.name in rim_exempt:
                continue
            if hypot(s.x, s.y) + s.r > rim:
                bad.append(f"{s.name}: past rim by "
                           f"{hypot(s.x, s.y) + s.r - rim:.1f}")
    for i, a in enumerate(sweeps):
        for b in sweeps[i + 1:]:
            if not (a.rotating or b.rotating):
                continue
            if a.name == b.name:
                continue                # segments of one part
            if frozenset((a.name, b.name)) in mesh_pairs:
                continue
            if a.z1 <= b.z0 + 1e-9 or b.z1 <= a.z0 + 1e-9:
                continue
            d = hypot(a.x - b.x, a.y - b.y)
            if d < 0.01:
                continue
            need = a.r + b.r + clearance
            if d < need:
                bad.append(f"{a.name} x {b.name}: {need - d:.2f} short "
                           f"(z {max(a.z0,b.z0):.1f}-{min(a.z1,b.z1):.1f})")
    return bad
