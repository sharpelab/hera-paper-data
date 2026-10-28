"""Runs 6 & 7 (sdh-spot-check, e- and h-side at D=0): raw R(B), onset, FFT tone content.
Feeds the landau-fan design (B_lo, dB, n-window, sensitivity)."""
import json, warnings
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError,
                           GateCalibration, luttinger_frequency)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
cal = json.load(open(HERE / "cal_run5.json"))
# cal_run5 c_tg/c_bg are SI F/m^2 (stack_capacitance); n_offset in 1e12 cm^-2, D_offset V/nm
GC = GateCalibration(cal["c_tg"], cal["c_bg"],
                     n_offset=cal["n_offset"] * 1e16, D_offset=cal["D_offset"] * 1e9)


def trace(rid):
    r = open_run(str(ROOT / "data" / str(rid)))
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col_at(cur.idx) / 1.0  # already gain-divided at read? no: stored value = param()/gain
    # hera.watch convention: stored column = X/gain already (fp gain division). Value is amps for sr0.
    V = None
    for c in chans:
        if c.cid == "sr1":
            V = r.col_at(c.idx)
    R = V / I
    mc = r.meta["measurement_config"]
    return r, B, R, I, mc


fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, rid in enumerate([6, 7]):
    r, B, R, I, mc = trace(rid)
    o = np.argsort(B)
    Bs, Rs = B[o], np.abs(R[o])
    print(f"\n===== run {rid} =====")
    print(f"  comments: {r.meta['comments']}")
    print(f"  pts {len(B)}  B {B.min():.3f}..{B.max():.3f} T  R {Rs.min():.1f}..{Rs.max():.1f} Ohm  I {np.median(I)*1e9:.2f} nA")
    sens = mc.get("sr1_sensitivity") or mc.get("sensitivities", {}).get("sr1")
    print(f"  mc keys: {sorted(mc.keys())}")
    print(f"  sr1 sens: {sens}")

    ax = axes[k, 0]
    ax.plot(Bs, Rs, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw Rxx vs B")

    # background-subtracted
    m = Bs > 0.5
    bg = np.polyval(np.polyfit(Bs[m], Rs[m], 5), Bs[m])
    ax = axes[k, 1]
    ax.plot(1.0 / Bs[m], Rs[m] - bg, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title(f"run {rid} detrended vs 1/B")

    # FFT over a few windows
    ax = axes[k, 2]
    for blo, bhi in [(1.0, 10.0), (2.0, 10.0), (4.0, 10.0), (6.0, 10.0)]:
        sel = (Bs >= blo) & (Bs <= bhi)
        if sel.sum() < 30:
            continue
        f, spec = sdh_fft(Rs[sel][:, None], Bs[sel], nfft=2048, bg_degree=5, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=0.8, label=f"{blo:.0f}-{bhi:.0f} T")
        top = f[np.argsort(s)[::-1][:400]]
        pk = []
        for ff in top:
            if all(abs(ff - p) > 1.5 for p in pk):
                pk.append(ff)
            if len(pk) >= 5:
                break
        print(f"  FFT {blo:.0f}-{bhi:.0f} T: top peaks (T) " + ", ".join(f"{p:.1f}" for p in sorted(pk)))
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.set_ylabel("norm |FFT|")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} SdH FFT")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            so = sdh_onset(Rs, Bs, b_lo=0.3, r_full_scale=50e-6 / np.median(np.abs(I)))
        print(so.summary())
        out[rid] = dict(onset_b=float(so.onset_b), onset_freq=float(so.onset_freq),
                        tones=[(float(t.freq), float(t.onset_b), float(t.contrast)) for t in so.tones])
    except SdhOnsetError as e:
        print(f"  sdh_onset FAILED: {e}")
        out[rid] = dict(error=str(e))

fig.tight_layout()
fig.savefig(HERE / "sdh67.png", dpi=110)
print("\nwrote", HERE / "sdh67.png")
json.dump(out, open(HERE / "sdh67.json", "w"), indent=1)
