"""Runs 6/7 sdh-spot-check: raw R(B), onset, FFT in 1/B, vs the Luttinger expectation.
Standalone (not notebook-namespace) so it can run under `menv python`."""
import json
import warnings
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import (
    open_run,
    summarize_run,
    resolve_channels,
    current_channel,
    sdh_fft,
    sdh_onset,
    SdhOnsetError,
    GateCalibration,
    luttinger_frequency,
)

D = Path(__file__).resolve().parent.parent / "data"
cal_j = json.load(open(Path(__file__).resolve().parent / "cal_run5.json"))
cal = GateCalibration(
    c_tg=cal_j["c_tg"],
    c_bg=cal_j["c_bg"],
    n_offset=cal_j["n_offset"] * 1e16,   # 1e12 cm^-2 -> m^-2
    D_offset=cal_j["D_offset"] * 1e9,    # V/nm -> V/m
)


def trace(rid):
    r = open_run(D / str(rid))
    B = r.col("magnet_field")
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    I = r.col_at(cur.idx) / cur.gain
    volt = [c for c in chs if not c.is_current]
    R = {c.cid: (r.col_at(c.idx) / c.gain) / I for c in volt}
    return r, B, I, R


fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for k, (rid, spot) in enumerate([(6, "+3.20e12 (e)"), (7, "-1.20e12 (h)")]):
    r, B, I, R = trace(rid)
    Rxx = np.abs(R["sr1"])
    T = r.col("T_sample")
    mc = r.meta["measurement_config"]
    print(f"===== run {rid}  {spot} =====")
    print(summarize_run(r))
    print(f"  I_bias: med {np.median(I)*1e9:.3f} nA  ({I.min()*1e9:.3f}..{I.max()*1e9:.3f})")
    print(f"  Rxx: {Rxx.min():.1f} .. {Rxx.max():.1f} Ohm   (B=0..end)")
    print(f"  T_sample: {T.mean():.3f} K  ({T.min():.3f}..{T.max():.3f})")
    for g in ("k_2400_tg_curr", "k_2400_bg_curr"):
        c = r.col(g)
        print(f"  {g}: med {np.median(c)*1e12:.0f} pA  ({c.min()*1e12:.0f}..{c.max()*1e12:.0f})")
    # field tracking
    sp = np.asarray(r.setpoints, float)
    print(f"  |B_read - B_set| max {np.abs(B - sp[: len(B)]).max()*1e3:.1f} mT")

    # ---- sort ascending in B for all spectral work
    o = np.argsort(B)
    Bs, Rs = B[o], Rxx[o]

    ax = axes[0, k]
    ax.plot(B, Rxx, lw=0.6)
    ax.set_xlabel("B (T)")
    ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} raw — n = {spot}")

    # ---- background-subtracted, high-B
    ax = axes[1, k]
    for blo, bhi, c in [(1.5, 10.0, "C0"), (4.0, 10.0, "C3")]:
        m = (Bs >= blo) & (Bs <= bhi)
        if m.sum() < 20:
            continue
        cf = np.polyfit(Bs[m], Rs[m], 5)
        ax.plot(Bs[m], Rs[m] - np.polyval(cf, Bs[m]), lw=0.7, color=c, label=f"{blo}-{bhi} T, deg5")
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlabel("B (T)")
    ax.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax.legend(fontsize=7)
    ax.set_title(f"run {rid} background-subtracted")

    # ---- FFT in 1/B over a few windows
    ax = axes[2, k]
    for blo, bhi in [(1.0, 10.0), (2.0, 10.0), (4.0, 10.0), (6.0, 10.0)]:
        m = (Bs >= blo) & (Bs <= bhi)
        if m.sum() < 32:
            continue
        f, spec = sdh_fft(Rs[m][:, None], Bs[m], bg_degree=5, log=False, nfft=2048)
        s = spec[0]
        keep = (f > 0) & (f < 80)
        sn = s[keep] / max(s[keep].max(), 1e-30)
        ax.plot(f[keep], sn, lw=0.8, label=f"{blo}-{bhi} T")
        pk = f[keep][np.argmax(sn)]
        # crude peak list
        top = np.argsort(sn)[::-1][:60]
        peaks = []
        for i in sorted(top):
            if 0 < i < len(sn) - 1 and sn[i] > sn[i - 1] and sn[i] > sn[i + 1] and sn[i] > 0.15:
                peaks.append((f[keep][i], sn[i]))
        print(f"  FFT {blo}-{bhi} T: dominant {pk:.2f} T; peaks>0.15: "
              + ", ".join(f"{a:.2f}T({b:.2f})" for a, b in peaks))
    Vtg = float(mc["comments"].split("(Vtg, Vbg) = (")[1].split(",")[0])
    Vbg = float(mc["comments"].split("(Vtg, Vbg) = (")[1].split(", ")[1].split(")")[0])
    n = cal.density(Vtg, Vbg)
    FL = float(luttinger_frequency(n))
    ax.axvline(FL, color="k", ls="--", lw=1, label=f"$F_L$={FL:.1f} T")
    ax.axvline(FL / 2, color="grey", ls=":", lw=1, label=f"$F_L/2$={FL/2:.1f} T")
    ax.set_xlabel("F (T)")
    ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7)
    ax.set_title(f"run {rid} SdH FFT — n={n*1e-16:+.2f}e12, $F_L$={FL:.1f} T")
    print(f"  n(cal) = {n*1e-16:+.3f}e12 cm^-2 ; F_L = {FL:.2f} T")

    # ---- onset
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            r_fs = None
            on = sdh_onset(Rs, Bs, r_full_scale=r_fs)
        print(on.summary())
        out[rid] = dict(onset_b=on.onset_b, onset_freq=on.onset_freq,
                        tones=[(t.freq, t.contrast, t.onset_b) for t in on.tones], FL=FL, n=n * 1e-16)
    except SdhOnsetError as e:
        print(f"  sdh_onset FAILED: {e}")
        out[rid] = dict(error=str(e), FL=FL, n=n * 1e-16)

fig.tight_layout()
fig.savefig(Path(__file__).resolve().parent / "sdh_spot_67.png", dpi=110)
print("\nwrote sdh_spot_67.png")
print(json.dumps(out, indent=1, default=float))
