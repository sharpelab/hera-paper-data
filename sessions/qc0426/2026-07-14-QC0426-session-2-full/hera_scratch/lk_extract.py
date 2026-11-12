"""Per-rung LK extraction: absolute FFT amplitudes of f_s/f_B/f_top + measured T.
Usage: menv python hera_scratch/lk_extract.py <run_id> [<run_id> ...]
Appends rows to hera_scratch/lk_table.csv (idempotent per run_id)."""
import sys, os, csv
import numpy as np
from hera.analysis import open_run, sdh_fft

I = 20e-9
F_L = 66.6          # Hall-pinned at n=+6.44e12
BANDS = {"f_s": (6, 20), "f_B": (45, 60), "f_top": (61, 74)}
TABLE = "hera_scratch/lk_table.csv"

rows_done = set()
if os.path.exists(TABLE):
    with open(TABLE) as f:
        rows_done = {r["run"] for r in csv.DictReader(f)}

out = []
for rid in sys.argv[1:]:
    if rid in rows_done:
        print(f"run {rid}: already in table"); continue
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); o = np.argsort(B)
    T = r.col_at(r.col_indices("T_sample")[-1]) if r.col_indices("T_sample") else None
    if T is None:
        # fallback: first float column ~ K scale
        T = r.col_at(2)
    Tm, Ts = float(np.mean(T)), float(np.std(T))
    row = {"run": rid, "T_mean": round(Tm, 3), "T_std": round(Ts, 3)}
    for ch in ("sr1", "sr2"):
        R = (r.col_at(r.col_indices(f"{ch}_X")[-1]) / I)[o]
        fr, spec = sdh_fft(R[:, None], B[o], b_range=(4.0, 8.0), bg_degree=3, log=False)
        mag = spec[0]
        for name, (flo, fhi) in BANDS.items():
            m = (fr >= flo) & (fr <= fhi)
            row[f"{ch}_{name}"] = float(mag[m].max()) if m.any() else np.nan
        noise = np.median(mag[(fr > 100) & (fr < 160)]) if (fr > 100).any() else np.nan
        row[f"{ch}_noise"] = float(noise)
    out.append(row)
    print(f"run {rid}: T={Tm:.3f}+-{Ts:.3f} K | " +
          " ".join(f"{k}={v:.3g}" for k, v in row.items() if k not in ("run","T_mean","T_std")))

if out:
    exists = os.path.exists(TABLE)
    with open(TABLE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        if not exists: w.writeheader()
        w.writerows(out)
    print(f"appended {len(out)} row(s) to {TABLE}")
