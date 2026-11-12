"""Fan design inputs: model F(n) tables (e-side + hole spot), run-6 onset on the >=1 T (Nyquist-sampled) record, run-5/6/7 timing."""
import sys, warnings, numpy as np
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
H = Path.home()/"measurement_env/hera/models"
sys.path.insert(0, str(H/"tetralayer_fs_count")); import fs_count_b0 as M4
D = Path(__file__).resolve().parent.parent / "data"
print("n[1e12]  F_L   | ABAB F (T) [m*]                         | ABCA F, topo, m* | ABCB F")
for n in [3.3, 3.2, 3.0, 2.8, 2.6, 2.4, 2.2, 2.0, 1.8, 1.6, 1.4, 1.2, 1.0, -1.2]:
    nm = n*1e16; FL = luttinger_frequency(abs(nm))
    fs = M4.abab_fs(nm)[1]; ms = M4.abab_mstar(nm)
    a = M4.abca_fs(nm); am = M4.abca_mstar(nm)
    try: cb = [round(F,1) for F, c in M4.abcb_fs(nm)[1]] if n > 0 else "-"
    except Exception as e: cb = f"err {e}"
    s = ", ".join(f"{F:.2f}({F/FL:.3f})[{m:.3f}]" for (F, _), (_, m) in zip(fs, ms))
    print(f"{n:+5.1f}  {FL:5.1f} | {s:40s} | {a[4]:.1f} {a[1]} nf={a[3]} m*={am[1]:.3f} | {cb}")
# trilayer dual-overlay family
try:
    sys.path.insert(0, str(H/"trilayer_fs_count")); import importlib
    import glob; print("trilayer files:", [Path(p).name for p in glob.glob(str(H/'trilayer_fs_count'/'*.py'))])
except Exception as e: print(e)
# ---- run-6 onset on the Nyquist-sampled part (10 mT steps from 1 T)
r = open_run(str(D/"6")); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); R = (r.col("sr1_X")/ch["sr1"].gain)/10e-9
for blo in (1.0, 1.2):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always"); on = sdh_onset(R, B, b_lo=blo, r_full_scale=5e3)
    for x in w: print("  warn:", x.message)
    print(on.summary())
# ---- timing
for rid in (5, 6, 7):
    r = open_run(str(D/str(rid))); t = r.col("time"); print(f"run {rid}: {len(t)} pts, wall {(t[-1]-t[0])/60:.1f} min, median dt {np.median(np.diff(t)):.3f} s, meta keys {list(r.meta)[:25]}")
r = open_run(str(D/"5")); t = r.col("time"); dt = np.diff(t)
nf = 66; per_row = dt.reshape(-1)[: (len(dt)//nf)*nf]
print("run5 within-row dt median", np.median(dt), " row-boundary dts:", np.sort(dt)[-65:][::8])
