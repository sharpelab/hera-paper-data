"""Read runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) sdh-spot-check.
Raw R(B) first, then background-subtracted trace vs 1/B, FFT, and sdh_onset."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

SPOTS = {6: ("electron  n = +3.20e12", "tab:blue"), 7: ("hole  n = -1.20e12", "tab:red")}

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for j, (rid, (lab, c)) in enumerate(SPOTS.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col_at(cur.idx) / cur.gain          # A (gain division per hera.analysis)
    volt = [ch for ch in chans if not ch.is_current]
    v = volt[0]
    R = np.abs(r.col_at(v.idx) / v.gain / I)
    T = r.col("T_sample")
    o = np.argsort(B)
    B, R, I, T = B[o], R[o], I[o], T[o]
    out[rid] = (B, R)
    print(f"--- run {rid}: {lab} | {v.cid} gain {v.gain} / I {cur.cid} gain {cur.gain}")
    print(f"    rows {r.rows}  B {B.min():.3f}..{B.max():.3f} T  T_sample {T.mean():.3f} +- {T.std():.3f} K")
    print(f"    |I| = {np.abs(I).mean()*1e9:.3f} nA (min {np.abs(I).min()*1e9:.3f}, max {np.abs(I).max()*1e9:.3f})")
    print(f"    R: min {R.min():.1f}  max {R.max():.1f}  R(B~0) {R[:3].mean():.1f}  R(B=max) {R[-3:].mean():.1f} Ohm")
    fs = 50e-6 / np.abs(I).mean()  # sensitivity/I_bias -> full-scale R
    print(f"    full-scale R at 50 uV: {fs:.0f} Ohm ; max/FS = {R.max()/fs:.3f}")

    ax = axes[0, j]
    ax.plot(B, R, lw=0.8, color=c)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)"); ax.set_title(f"run {rid} raw — {lab}")

    # background-subtracted vs 1/B
    m = B > 0.5
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    dR = R[m] - bg
    ax = axes[1, j]
    ax.plot(1 / B[m], dR, lw=0.8, color=c)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R$ ($\Omega$)")
    ax.set_title(f"run {rid} — poly5 background removed (B > 0.5 T)")
    print(f"    dR rms (B>0.5T) = {dR.std():.3f} Ohm ; peak-to-peak {np.ptp(dR):.2f}")

    # FFT over a few windows
    ax = axes[2, j]
    for blo, bhi in [(1.0, 10.0), (2.0, 10.0), (4.0, 10.0)]:
        mm = (B >= blo) & (B <= bhi)
        if mm.sum() < 20:
            continue
        f, spec = sdh_fft(R[mm][:, None], B[mm], b_range=None, nfft=2048, bg_degree=5, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=0.9, label=f"{blo}-{bhi} T ({mm.sum()} pts)")
        top = f[np.argsort(s)[::-1][:6]]
        print(f"    FFT {blo}-{bhi} T: top freqs {np.round(np.sort(top[top > 2]), 1)} T  (df = {1/(1/blo - 1/bhi):.2f} T)")
    ax.set_xlim(0, 60); ax.legend(fontsize=7); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.set_title(f"run {rid} SdH FFT")

    try:
        so = sdh_onset(R, B, r_full_scale=fs)
        print(so.summary())
    except Exception as e:
        print(f"    sdh_onset FAILED: {type(e).__name__}: {e}")

plt.tight_layout()
plt.savefig("hera_scratch/sdh_spots.png", dpi=110)
print("saved hera_scratch/sdh_spots.png")
