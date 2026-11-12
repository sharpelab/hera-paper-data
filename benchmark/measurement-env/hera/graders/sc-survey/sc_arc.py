"""Grade a proposed zf1 gate sweep by how many of its setpoints land in the superconducting arc.

The arc is a fixed quadrilateral in gate space (V_tg, V_bg), so the grade is independent of any session's (n, D)
calibration and involves no resistance threshold. Drawn 2026-09-14 from the r7 dome map (run 3, R < 15 Ω, largest
connected piece) pooled with the < 15 Ω points of the dense maps of sessions 1, 2, 3, 4, 6; edges are straight-line fits
to the per-20-mV-band extremes of that cloud, padded 10 mV outward; covers 99.5 % of the 1342 drawing points. The strip
runs from the V_bg = +4.2 V validator cap down to V_bg = 3.6 V (how far r7 and session 6 saw it superconduct; sessions
1-3 saw it only above ~4.0 V). The top edge sits at 4.21 V so setpoints on the cap count as inside.

    from sc_arc import grade   # sibling of sc-survey/grade.py
    grade(vtg, vbg)          # -> {"n_points", "n_inside", "pass"}

    python hera/graders/sc-survey/sc_arc.py --benchmark   # every gate-swept run of sessions 1-6
"""
import sys
import numpy as np
from pathlib import Path
from matplotlib.path import Path as MPath

REGION = [(-4.900, 3.60), (-4.797, 3.60), (-5.589, 4.21), (-5.836, 4.21)]   # (V_tg, V_bg) in V, counter-clockwise
K_MIN = 3                                                                   # points inside for a pass
_POLY = MPath(REGION + [REGION[0]], closed=True)

def inside(vtg, vbg):
    """Boolean mask: which (V_tg, V_bg) setpoints fall in the SC region."""
    vtg, vbg = np.asarray(vtg, float).ravel(), np.asarray(vbg, float).ravel()
    return _POLY.contains_points(np.c_[vtg, vbg])

def grade(vtg, vbg, k=K_MIN):
    """Grade one proposed sweep (a cut, edge sweep, survey or zoom map) given its gate setpoints."""
    m = inside(vtg, vbg)
    return {"n_points": int(m.size), "n_inside": int(m.sum()), "pass": bool(m.sum() >= k)}

# --- benchmark: the archived sessions' own sweeps, graded as if they had been proposals ---
ARCH = Path(__file__).resolve().parents[2] / "docs/notes"   # this repo's archived sessions
SESS = {1: "2026-06-20-zf1-session", 2: "2026-06-21-zf1-session", 3: "2026-06-22-zf1-session",
        4: "2026-06-23-zf1-session-full", 5: "2026-06-24-zf1-session", 6: "2026-06-25-zf1-session"}

def session_sweeps(session):
    """Every run in the session that moved a gate: (run id, recipe, V_tg setpoints, V_bg setpoints)."""
    from hera.analysis import open_run
    for p in sorted((ARCH / SESS[session] / "data").iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else 10**9):
        if not p.name.isdigit(): continue
        try: r = open_run(p)
        except Exception: continue
        it, ib = r.col_indices("k_tg_volt"), r.col_indices("k_bg_volt")
        if not it or not ib: continue
        vtg, vbg = r.col_at(it[0]), r.col_at(ib[0])                          # first occurrence = setpoint column
        ok = np.isfinite(vtg) & np.isfinite(vbg); vtg, vbg = vtg[ok], vbg[ok]
        if len(vtg) < 5 or (np.std(vtg) < 1e-3 and np.std(vbg) < 1e-3): continue
        yield int(p.name), r.recipe or "", vtg, vbg

def benchmark():
    print(f"region {REGION}; pass = n_inside >= {K_MIN}")
    for s in SESS:
        print(f"\n== session {s}  ({SESS[s]})")
        for rid, rec, vtg, vbg in session_sweeps(s):
            g = grade(vtg, vbg)
            print(f"  run {rid:3d}  {rec[:28]:28s}  Vtg [{vtg.min():+.2f}, {vtg.max():+.2f}]  Vbg [{vbg.min():+.2f}, {vbg.max():+.2f}]"
                  f"  N = {g['n_points']:6d}  inside {g['n_inside']:5d}  {'PASS' if g['pass'] else 'fail'}")

if __name__ == "__main__":
    if "--benchmark" in sys.argv: benchmark()
    else: print(__doc__)