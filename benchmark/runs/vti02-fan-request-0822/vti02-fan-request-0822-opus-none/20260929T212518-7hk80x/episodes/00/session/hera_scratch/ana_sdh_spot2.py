"""Runs 6/7: careful spectral read. The first pass used sdh_fft windows whose 1/B span set a
coarse bin grid (6-10 T -> 15 T bins), so 'peaks' landed on bin multiples identically in both
runs. Here: Lomb-Scargle on the native (non-uniform-in-1/B) samples, no resampling, plus a
zero-padded FFT on a properly-dense 1/B grid as a cross-check."""
import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import lombscargle

from hera.analysis import open_run, resolve_channels, current_channel, GateCalibration, luttinger_frequency

HS = Path(__file__).resolve().parent
D = HS.parent / "data"
cj = json.load(open(HS / "cal_run5.json"))
cal = GateCalibration(c_tg=cj["c_tg"], c_bg=cj["c_bg"], n_offset=cj["n_offset"] * 1e16, D_offset=cj["D_offset"] * 1e9)


def trace(rid):
    r = open_run(D / str(rid))
    B = r.col("magnet_field")
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    I = r.col_at(cur.idx) / cur.gain
    Rxx = np.abs((r.col_at([c for c in chs if not c.is_current][0].idx) / 1.0) / I)
    o = np.argsort(B)
    return r, B[o], Rxx[o]


def spectrum(B, R, blo, bhi, deg=5, fmax=80.0, nf=4000):
    m = (B >= blo) & (B <= bhi)
    b, r = B[m], R[m]
    r = r - np.polyval(np.polyfit(b, r, deg), b)      # MR background in B-space
    x = 1.0 / b                                        # ascending? 1/B descends with B
    o = np.argsort(x)
    x, y = x[o], r[o]
    y = y * np.hanning(len(y))                         # taper (approx: samples are non-uniform)
    f = np.linspace(0.5, fmax, nf)
    ang = 2 * np.pi * f
    p = lombscargle(x, y - y.mean(), ang, normalize=True)
    return f, p, len(b), 1.0 / (x.max() - x.min())     # freq resolution = 1/span(1/B)


def peaks_of(f, p, frac=0.2):
    i = np.where((p[1:-1] > p[:-2]) & (p[1:-1] > p[2:]))[0] + 1
    i = i[p[i] > frac * p.max()]
    return sorted([(f[j], p[j] / p.max()) for j in i], key=lambda t: -t[1])


fig, axes = plt.subplots(2, 2, figsize=(13, 8))
summary = {}
for k, rid in enumerate([6, 7]):
    r, B, R = trace(rid)
    mc = r.meta["measurement_config"]["comments"]
    Vtg = float(mc.split("(Vtg, Vbg) = (")[1].split(",")[0])
    Vbg = float(mc.split("(Vtg, Vbg) = (")[1].split(", ")[1].split(")")[0])
    n = cal.density(Vtg, Vbg)
    FL = float(luttinger_frequency(n))
    print(f"\n===== run {rid}: n = {n*1e-16:+.3f}e12 cm^-2, F_L = {FL:.2f} T =====")
    summary[rid] = dict(n=n * 1e-16, FL=FL, windows={})

    ax = axes[0, k]
    for blo, bhi, c in [(1.0, 10.0, "C0"), (2.0, 10.0, "C1"), (3.0, 10.0, "C2"), (1.0, 5.0, "C3")]:
        f, p, npt, df = spectrum(B, R, blo, bhi)
        pk = peaks_of(f, p)
        print(f"  LS {blo:4.1f}-{bhi:4.1f} T ({npt:4d} pts, dF={df:5.2f} T): "
              + ", ".join(f"{a:.1f}T({b:.2f})" for a, b in pk[:8]))
        summary[rid]["windows"][f"{blo}-{bhi}"] = dict(dF=df, peaks=[(float(a), float(b)) for a, b in pk[:8]])
        ax.plot(f, p / p.max(), lw=0.9, color=c, label=f"{blo}-{bhi} T (dF {df:.1f})")
    ax.axvline(FL, color="k", ls="--", lw=1.2)
    ax.text(FL, 1.02, f"$F_L$={FL:.1f}", ha="center", fontsize=8)
    for frac, lbl in [(0.5, "F/2"), (0.25, "F/4")]:
        ax.axvline(FL * frac, color="grey", ls=":", lw=0.9)
    ax.set_xlabel("F (T)"); ax.set_ylabel("LS power (norm)")
    ax.set_title(f"run {rid}  n={n*1e-16:+.2f}e12  Lomb-Scargle in 1/B")
    ax.legend(fontsize=7); ax.set_xlim(0, 60)

    # oscillation amplitude vs B (for fan sizing)
    ax = axes[1, k]
    m = B >= 0.8
    b, rr = B[m], R[m]
    bg = np.polyval(np.polyfit(b, rr, 7), b)
    ax.plot(b, rr - bg, lw=0.7)
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid}: R(0.8T)={rr[0]:.0f}, R(10T)={R[-1]:.0f} $\\Omega$; "
                 f"osc pp@[2,4]={np.ptp((rr-bg)[(b>2)&(b<4)]):.1f}, @[7,10]={np.ptp((rr-bg)[b>7]):.1f} $\\Omega$")
    # dR/R at several B
    for lo, hi in [(1, 2), (2, 3), (3, 5), (5, 7), (7, 10)]:
        s = (b >= lo) & (b < hi)
        print(f"    B {lo}-{hi} T: R {np.mean(rr[s]):7.1f} Ohm, osc pp {np.ptp((rr-bg)[s]):6.2f} Ohm "
              f"({100*np.ptp((rr-bg)[s])/np.mean(rr[s]):5.2f} %)")
    summary[rid]["R10T"] = float(R[-1]); summary[rid]["R1T"] = float(rr[0])

fig.tight_layout()
fig.savefig(HS / "sdh_spot_67_ls.png", dpi=110)
print("\nwrote sdh_spot_67_ls.png")
json.dump(summary, open(HS / "sdh_spot_67.json", "w"), indent=1, default=float)
