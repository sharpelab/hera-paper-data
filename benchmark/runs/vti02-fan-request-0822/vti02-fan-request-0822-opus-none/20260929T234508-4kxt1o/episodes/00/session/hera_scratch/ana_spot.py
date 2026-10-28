"""Runs 6 & 7 — sdh-spot-check read (electron n=+3.2e12, hole n=-1.2e12, both D=0).
Raw first, then background-subtracted 1/B view, sdh_onset, and FFT."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, summarize_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency,
                           GateCalibration)

CAL = GateCalibration(c_tg=2.796e-03, c_bg=2.161e-03,
                      n_offset=-0.0894e16, D_offset=-0.013e9)

def load(rid):
    r = open_run(f"data/{rid}")
    print(f"===== run {rid} =====")
    print(summarize_run(r))
    print("interrupted:", r.interrupted, "| rows:", r.rows, "| cols:", r.cols)
    print("comments:", r.recipe, r.tags)
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    print("channels:", [(c.cid, c.gain, c.label, c.is_current) for c in chans])
    B = r.col("field") if "field" in r.cols else r.col_at(1)
    I = r.col_at(cur.idx) / cur.gain
    v = [c for c in chans if not c.is_current][0]
    R = (r.col_at(v.idx) / v.gain) / I
    T = r.col("T_sample") if "T_sample" in r.cols else None
    sens = r.meta.get("measurement_config", {}).get("sr1_sens")
    print(f"B {B.min():.3f}..{B.max():.3f} T  |I| med {np.median(np.abs(I))*1e9:.3f} nA  "
          f"R {np.abs(R).min():.1f}..{np.abs(R).max():.1f} Ohm  sr1_sens {sens}")
    if T is not None:
        print(f"T_sample {T.min():.3f}..{T.max():.3f} K (med {np.median(T):.3f})")
    return r, B, np.abs(R), I

for rid, nspot in ((6, 3.2), (7, -1.2)):
    r, B, R, I = load(rid)
    FL = luttinger_frequency(nspot * 1e16)
    print(f"Luttinger full-density F_L(n={nspot:+.2f}e12) = {FL:.1f} T")

    # background-subtracted trace for the eye
    m = B > 0.9
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    dR = R[m] - bg
    print(f"dR rms (B>0.9 T) = {dR.std():.2f} Ohm, peak-to-peak {np.ptp(dR):.2f} Ohm, R_bg scale {bg.mean():.0f} Ohm")

    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / np.median(np.abs(I)))
        print(on.summary())
    except SdhOnsetError as e:
        print("sdh_onset FAILED:", e)
        on = None

    f, spec = sdh_fft(R[:, None], B, b_range=(1.0 if rid == 6 else 1.0, B.max()), nfft=2048)
    sp = spec[0]
    keep = (f > 2) & (f < 120)
    fk, spk = f[keep], sp[keep]
    order = np.argsort(spk)[::-1]
    print("top FFT peaks (T):", [(round(float(fk[i]), 2), round(float(spk[i] / spk.max()), 3)) for i in order[:12]])

    fig, ax = plt.subplots(1, 3, figsize=(16, 4.2))
    ax[0].plot(B, R, lw=0.8); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("R_xx (Ohm)")
    ax[0].set_title(f"run {rid} raw  n={nspot:+.1f}e12, D=0")
    ax[1].plot(1 / B[m], dR, lw=0.8); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dR (Ohm)")
    ax[1].set_title("background-subtracted (deg-5 in B, B>0.9 T)")
    ax[2].plot(fk, spk, lw=0.9); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT|")
    ax[2].axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f} T")
    ax[2].axvline(FL / 2, color="orange", ls=":", label=f"F_L/2={FL/2:.1f} T")
    ax[2].axvline(FL / 4, color="g", ls=":", label=f"F_L/4={FL/4:.1f} T")
    ax[2].legend(fontsize=8); ax[2].set_title("SdH FFT in 1/B")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
    print()
