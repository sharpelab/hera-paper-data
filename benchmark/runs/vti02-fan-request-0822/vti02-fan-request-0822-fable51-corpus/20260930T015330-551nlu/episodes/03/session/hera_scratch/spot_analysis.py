"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12):
raw R(B), sdh_onset, sdh_fft with window/bg stability, tones vs F_L and the model templates."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

OUT = "hera_scratch"
FS = 50e-6 / 10e-9   # sr1 50 uV / 10 nA -> 5 kOhm full scale


def load(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); return r, B[o], R[o], r.col("T_sample")[o]


res = {}
fig, axs = plt.subplots(2, 3, figsize=(17, 8))
for row, (rid, n12, lab) in enumerate([(6, 3.2, "electron n=+3.2e12"), (7, -1.2, "hole n=-1.2e12")]):
    r, B, R, T = load(rid)
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"\n===== run {rid} {lab}: F_L = {FL:.2f} T; R(B<0.2) = {np.median(R[B < 0.2]):.1f} Ohm, R max {R.max():.0f} at B={B[np.argmax(R)]:.2f}; T {T.min():.3f}-{T.max():.3f} K")
    ax = axs[row, 0]; ax.plot(B, R, lw=0.6); ax.set_xlabel("B (T)"); ax.set_ylabel("R_xx signed (Ohm)"); ax.set_title(f"run {rid} raw {lab}")
    # onset
    on = None
    for kw in (dict(b_lo=0.3), dict(b_lo=1.0), dict(b_lo=1.0, bg_degree=7)):
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                on = sdh_onset(np.abs(R), B, r_full_scale=FS, **kw)
                for wi in w: print("  warn:", str(wi.message)[:200])
            print(f"--- sdh_onset {kw}:\n{on.summary()}")
            break
        except SdhOnsetError as e:
            print(f"--- sdh_onset {kw} FAILED: {str(e)[:600]}")
    # FFT stability: windows x bg degrees
    ax2 = axs[row, 1]; ax3 = axs[row, 2]
    cuts = [1.5, 2.0, 3.0] if rid == 6 else [1.0, 1.5, 2.5]
    peaks = {}
    for cut in cuts:
        for deg in (3, 5, 7):
            fr, sp = sdh_fft(np.abs(R)[:, None], B, b_range=(cut, B.max()), bg_degree=deg, log=False, nfft=4096)
            s = sp[0]; m = fr > 2.0
            # top peaks
            from scipy.signal import find_peaks
            pk, pr = find_peaks(s[m], prominence=0.08 * s[m].max())
            top = sorted(zip(pr["prominences"], fr[m][pk]), reverse=True)[:6]
            peaks[(cut, deg)] = [(round(f, 2), round(p / s[m].max(), 2)) for p, f in top]
            if deg == 5:
                ax2.plot(fr, s / s[m].max(), lw=0.8, label=f"cut {cut} T")
    for k, v in peaks.items(): print(f"  FFT cut {k[0]} deg {k[1]}: peaks (F, rel) = {v}")
    ax2.axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L {FL:.1f}")
    ax2.set_xlim(0, 2.2 * FL); ax2.set_xlabel("F (T)"); ax2.set_ylabel("|FFT| (norm)"); ax2.legend(fontsize=7); ax2.set_title("FFT in 1/B (bg deg 5, log=False)")
    # B-window split (breakdown discrimination) at deg 5, cut mid
    cut = cuts[1]
    Bm = np.sqrt(cut * B.max()) if False else 2 / (1 / cut + 1 / B.max())   # split at equal 1/B halves
    for lo, hi, name in ((cut, Bm, "low-B half"), (Bm, B.max(), "high-B half")):
        fr, sp = sdh_fft(np.abs(R)[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        s = sp[0]; m = fr > 2
        ax3.plot(fr, s / s[m].max(), lw=0.8, label=f"{name} {lo:.2f}-{hi:.2f} T")
        pk, pr = find_peaks(s[m], prominence=0.1 * s[m].max())
        print(f"  split {name} {lo:.2f}-{hi:.2f}: peaks {sorted(zip(np.round(fr[m][pk],1), np.round(pr['prominences']/s[m].max(),2)), key=lambda t:-t[1])[:5]}")
    ax3.axvline(FL, color="k", ls="--", lw=0.8); ax3.set_xlim(0, 2.2 * FL); ax3.legend(fontsize=7); ax3.set_title("B-window split")
    # background-subtracted trace for eyeballing onset (deg 5 in B, above cut)
    m = B >= cuts[0]; cf = np.polyfit(B[m], np.abs(R)[m], 5); dR = np.abs(R)[m] - np.polyval(cf, B[m])
    np.save(f"{OUT}/dR_run{rid}.npy", np.c_[B[m], dR])
    res[rid] = dict(FL=FL, onset=None if on is None else on.onset_b, peaks={f"{k[0]}_{k[1]}": v for k, v in peaks.items()})
fig.tight_layout(); fig.savefig(f"{OUT}/spot_runs67.png", dpi=110)

# dR traces figure
fig, axs = plt.subplots(2, 1, figsize=(15, 7))
for ax, rid in zip(axs, (6, 7)):
    d = np.load(f"{OUT}/dR_run{rid}.npy"); ax.plot(1 / d[:, 0], d[:, 1], lw=0.6); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)"); ax.set_title(f"run {rid} background-subtracted (deg-5 in B)")
fig.tight_layout(); fig.savefig(f"{OUT}/spot_runs67_dR.png", dpi=110)
json.dump(res, open(f"{OUT}/spot_read.json", "w"), indent=1, default=str)
print("saved")
