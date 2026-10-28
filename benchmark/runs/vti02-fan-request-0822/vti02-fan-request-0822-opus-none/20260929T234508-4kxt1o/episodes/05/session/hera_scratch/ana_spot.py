"""SdH spot checks runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12): raw R(B),
background, FFT in 1/B, per-tone onset. Sets the landau-fan design (B_lo, B_hi,
spacing, sensitivity, dwell)."""
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError,
                           GateCalibration, luttinger_frequency)

DD = Path("/home/hera/measurements/zack/20260822-vti-02/data")
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run 5, n in 1e12 cm^-2


def load(i):
    r = open_run(DD / str(i))
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    I = r.col_at(cur.idx) / cur.gain
    B = r.col("magnet_field")
    V = {c.cid: r.col_at(c.idx) / c.gain for c in ch if not c.is_current}
    R = {k: v / I for k, v in V.items()}
    return r, B, I, R


fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for j, (rid, label, nspot) in enumerate([(6, "electron n=+3.2e12", +3.2), (7, "hole n=-1.2e12", -1.2)]):
    r, B, I, R = load(rid)
    Rxx = np.abs(R["sr1"])
    o = np.argsort(B)
    B, Rxx, I = B[o], Rxx[o], I[o]
    fs_R = 50e-6 / np.median(np.abs(I))     # sr1 sensitivity 50 uV / I_bias -> full-scale ohms
    print(f"\n===== run {rid}: {label}")
    print(f"  I_bias median {np.median(np.abs(I))*1e9:.3f} nA (spread {np.std(np.abs(I))*1e9:.3f}); "
          f"R full scale {fs_R:.0f} Ohm; R {Rxx.min():.1f} .. {Rxx.max():.1f} Ohm "
          f"({100*Rxx.max()/fs_R:.1f} % FS)")
    print(f"  T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; "
          f"|I_tg|max {np.abs(r.col('k_2400_tg_curr')).max():.2e} A, |I_bg|max {np.abs(r.col('k_2400_bg_curr')).max():.2e} A")
    # Luttinger full-density frequency for this spot
    nSI = nspot * 1e16
    print(f"  F_L(full density) = {luttinger_frequency(abs(nSI)):.2f} T; "
          f"quarter (4-fold split) {luttinger_frequency(abs(nSI))/4:.2f} T")

    ax = axes[0, j]
    ax.plot(B, Rxx, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw — {label}")

    # background-subtracted trace (poly in B) over the high-field window
    for blo in (1.0, 2.0, 3.0):
        m = B >= blo
        cf = np.polyfit(B[m], Rxx[m], 5)
        d = Rxx[m] - np.polyval(cf, B[m])
        print(f"  detrend B>={blo}: residual rms {np.std(d):.3f} Ohm, p-p {d.max()-d.min():.3f} Ohm, "
              f"rel {100*np.std(d)/np.mean(Rxx[m]):.2f} %")
    m = B >= 1.0
    cf = np.polyfit(B[m], Rxx[m], 5)
    d = Rxx[m] - np.polyval(cf, B[m])
    ax = axes[1, j]
    ax.plot(1 / B[m], d, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title(f"run {rid} detrended (B>1 T, poly5)")

    # FFT over several windows
    ax = axes[2, j]
    for blo, bhi in [(1.0, 10.0), (2.0, 10.0), (4.0, 10.0), (1.0, 5.0)]:
        if B.max() < bhi - 0.5:
            bhi = B.max()
        f, spec = sdh_fft(Rxx[:, None], B, b_range=(blo, bhi), nfft=2048, bg_degree=5, log=False)
        s = spec[0]
        sel = f > 1.0
        pk = f[sel][np.argmax(s[sel])]
        ax.plot(f, s / s[sel].max(), lw=0.9, label=f"{blo}-{bhi} T (peak {pk:.1f} T)")
        print(f"  FFT {blo}-{bhi} T: peak at F = {pk:.2f} T; resolution dF = {1/(1/blo - 1/bhi):.2f} T")
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.set_ylabel("norm. amp"); ax.legend(fontsize=7)
    ax.set_title(f"run {rid} SdH FFT")

    # per-tone onset
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            on = sdh_onset(Rxx, B, r_full_scale=fs_R)
        print("  --- sdh_onset ---")
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print(f"  sdh_onset FAILED: {e}")
        out[rid] = None

fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_runs67.png", dpi=110)
print("\nsaved spot_runs67.png")
