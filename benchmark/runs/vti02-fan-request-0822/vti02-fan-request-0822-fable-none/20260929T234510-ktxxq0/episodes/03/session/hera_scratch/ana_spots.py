"""Scratch: analyze SdH spot checks runs 6 (electron, n=+3.2e12, B 0->10) and 7 (hole, n=-1.2e12, B 10->0.3)."""
import numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, summarize_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, GateCalibration, luttinger_frequency)

base = Path("/home/hera/measurements/zack/20260822-vti-02/data")
cal = json.load(open("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/cal_run5.json"))

for rid, nspot in ((6, 3.2e12 * 1e4), (7, -1.2e12 * 1e4)):  # n in m^-2
    r = open_run(base / str(rid))
    print(f"===== run {rid} =====")
    print(summarize_run(r))
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    B = r.col("magnet_field") if "magnet_field" in r.cols else r.col_at(1)
    print("cols:", r.cols)
    I = r.col(cur.col) / cur.gain
    v = [c for c in chans if c.cid == "sr1"][0]
    R = (r.col(v.col) / v.gain) / I
    T = r.col("T_sample") if "T_sample" in r.cols else None
    print(f"I_bias med {np.median(np.abs(I))*1e9:.2f} nA; R(B~min) {np.abs(R[np.argmin(np.abs(B))]):.1f} Ohm; "
          f"R range {np.abs(R).min():.1f}-{np.abs(R).max():.1f}; T {T.mean():.3f}+-{T.std():.3f} K" if T is not None else "")
    F_full = luttinger_frequency(nspot)
    print(f"Luttinger single-FS frequency at |n|: {F_full:.1f} T")
    # sensitivity / full scale
    sens = 50e-6; ibias_nom = np.median(np.abs(I))
    rfs = sens / ibias_nom
    srt = np.argsort(np.abs(B)); Bs, Rs = np.abs(B)[srt], np.abs(R)[srt]
    # dedupe/monotonic
    try:
        o = sdh_onset(Rs, Bs, b_hi=10.0, b_lo=0.3, r_full_scale=rfs)
        print(o.summary())
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e)
    # FFT over a couple of windows
    for blo, bhi in ((1.5, 10.0), (3.0, 10.0)):
        m = (Bs >= blo) & (Bs <= bhi)
        try:
            f, s = sdh_fft(Rs[m][:, None], Bs[m], b_range=None, nfft=2048, bg_degree=5, log=False)
            sp = s[0]; sp[f < 2] = 0
            pk = f[np.argmax(sp)]
            top = f[np.argsort(sp)[::-1][:6]]
            print(f"FFT window {blo}-{bhi} T: peak {pk:.1f} T; top bins {np.round(np.sort(top),1)}")
        except Exception as e:
            print("sdh_fft:", type(e).__name__, e)
    fig, ax = plt.subplots(2, 1, figsize=(10, 7))
    ax[0].plot(np.abs(B), np.abs(R), lw=0.6)
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("|Rxx| (Ohm)"); ax[0].set_title(f"run {rid} raw")
    m = (Bs >= 1.5)
    f, s = sdh_fft(Rs[m][:, None], Bs[m], nfft=2048, bg_degree=5, log=False)
    ax[1].plot(f, s[0], lw=0.8); ax[1].set_xlim(0, 120); ax[1].set_xlabel("F (T)"); ax[1].set_ylabel("FFT mag")
    ax[1].axvline(F_full, color="r", ls="--", label=f"single-FS F(|n|)={F_full:.1f} T"); ax[1].legend()
    fig.tight_layout(); fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{rid}.png", dpi=110)
    print()
