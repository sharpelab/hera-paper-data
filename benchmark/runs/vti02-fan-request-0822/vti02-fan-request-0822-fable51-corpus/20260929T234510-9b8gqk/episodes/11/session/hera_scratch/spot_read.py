"""Spot-check read for runs 6 (e, n=+3.2) and 7 (h, n=-1.2): R from measured I, sdh_onset, windowed FFTs with peak lists."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

MODEL = {6: dict(n=3.2, abab=(7.3, 25.8), abca=33.1), 7: dict(n=-1.2, abab=(5.3, 7.1), abca=12.4)}
def load(rid):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.metadata)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B); return B[o], R[o], I[o], r
def peaks(f, s, fmin=2.0, nmax=8):
    m = f >= fmin; ff, ss = f[m], s[m]
    pk, pr = find_peaks(ss, prominence=0.05 * ss.max())
    order = np.argsort(ss[pk])[::-1][:nmax]
    return [(ff[pk[i]], ss[pk[i]] / ss.max()) for i in order]

for rid, wins in ((6, [(1.0, 10.0), (0.7, 10.0), (1.0, 3.0), (3.0, 10.0), (1.0, 5.0), (5.0, 10.0)]),
                  (7, [(0.75, 10.0), (0.75, 3.0), (3.0, 10.0), (0.75, 5.0), (5.0, 10.0)])):
    B, R, I, r = load(rid); FL = MODEL[rid]
    print("=" * 90); print(f"run {rid}: n={FL['n']:+.2f}e12  F_L={luttinger_frequency(abs(FL['n'])*1e16):.2f} T  model ABAB {FL['abab']}  ABCA {FL['abca']}")
    print(f"  I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.0f}..{R.max():.0f} Ohm; R(B<0.5) med {np.median(R[B<0.5]):.1f}; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    nu = lambda b: abs(FL['n']) * 1e16 * 4.1357e-15 / b
    print(f"  filling factor nu at 2/4/6/8/10 T: " + ", ".join(f"{b}T:{nu(b):.1f}" for b in (2, 4, 6, 8, 10)))
    try:
        on = sdh_onset(R, B, r_full_scale=5e3); print(on.summary())
    except SdhOnsetError as e: print("  SdhOnsetError:", e)
    fig, ax = plt.subplots(2, 3, figsize=(16, 8)); ax = ax.ravel()
    ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {rid} raw Rxx(B), n = {FL['n']:+.2f}e12, D = 0")
    lo, hi = wins[0]; m = (B >= lo) & (B <= hi); p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    ax[1].plot(1 / B[m], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)"); ax[1].set_title(f"bg-subtracted (deg 5, {lo}-{hi} T) vs 1/B")
    for k, (lo, hi) in enumerate(wins):
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=2048); sp = sp[0]
        dF = 1 / (1 / lo - 1 / hi)
        pl = peaks(f, sp)
        print(f"  FFT window {lo:>4}-{hi:>4} T (dF {dF:.2f} T): " + ", ".join(f"{fr:.1f}T({a:.2f})" for fr, a in pl))
        a = ax[2 + min(k, 3)] if k < 4 else ax[5]
        a.plot(f, sp / sp[f > 2].max(), lw=0.8, label=f"{lo}-{hi} T, dF {dF:.1f}")
    for a in ax[2:]:
        a.set_xlim(0, 60); a.set_xlabel("F (T)"); a.axvline(luttinger_frequency(abs(FL['n'])*1e16), color="k", ls=":", lw=1, label="F_L")
        for x in FL['abab']: a.axvline(x, color="r", ls="--", lw=0.8)
        a.legend(fontsize=7)
    ax[2].set_title("FFT (red dashed: model ABAB pair; dotted: F_L = ABCA)")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_read_run{rid}.png", dpi=110); print(f"  saved hera_scratch/spot_read_run{rid}.png")
