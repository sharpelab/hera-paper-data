import numpy as np
from pathlib import Path
from hera.analysis import open_run, fan_grids, resistance_grids, resolve_channels
r5 = open_run("data/5"); t = r5.col("time"); nf = 66
dt = np.diff(t); rows = len(t)//nf
intra = np.concatenate([dt[i*nf:(i+1)*nf-1] for i in range(rows)])
inter = np.array([t[(i+1)*nf]-t[(i+1)*nf-1] for i in range(rows-1)])
print(f"run5: fast_delay {r5.meta['fast_delay']} slow_delay {r5.meta['slow_delay']}: intra-row dt median {np.median(intra):.3f} s (p90 {np.percentile(intra,90):.3f}); row gap median {np.median(inter):.2f} s; total {(t[-1]-t[0])/60:.1f} min, {len(t)} pts")
r6 = open_run("data/6"); t6 = r6.col("time"); B6 = r6.col_at(1); d6 = np.diff(t6); dB = np.diff(B6)
m = np.isclose(dB, 0.01, atol=1e-4); print(f"run6: 10 mT step dt median {np.median(d6[m]):.2f} s -> overhead beyond bare ramp {np.median(d6[m]) - 0.01/(0.137/60):.2f} s")
m = np.isclose(dB, 0.05, atol=1e-4); print(f"run6: 50 mT step dt median {np.median(d6[m]):.2f} s -> overhead {np.median(d6[m]) - 0.05/(0.137/60):.2f} s")
r7 = open_run("data/7"); d7 = np.diff(r7.col("time")); print(f"run7: 20 mT step dt median {np.median(d7):.2f} s -> overhead {np.median(d7) - 0.02/(0.137/60):.2f} s")
# noise floor: point-to-point scatter at low field
for rid, sens in ((6, 50e-6), (7, 50e-6)):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain))
    o = np.argsort(B); B, R = B[o], R[o]
    for lo, hi in ((1.0, 1.5), (2.5, 3.0), (8.5, 9.5)):
        s = (B > lo) & (B < hi); d = np.diff(R[s]); print(f"run{rid} {lo}-{hi} T: R med {np.median(R[s]):.1f}, pt-pt rms/sqrt2 {np.std(d)/np.sqrt(2):.2f} Ohm")
g = fan_grids("data/5"); rg = resistance_grids(g); R = np.abs(rg.R["sr1"])
d = np.diff(R, axis=1); lowR = R[:, 1:] < 150
print(f"run5 (100 uV): pt-pt rms/sqrt2 where R<150: {np.std(d[lowR])/np.sqrt(2):.2f} Ohm (includes real structure)")
print("run5 sr1 X max / sens:", np.abs(g.grid("sr1_X")).max()/100e-6)
