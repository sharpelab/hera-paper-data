"""Runs 6-7 (sdh-spot-check): raw R(B), onset, FFT in 1/B. Establishes the fan's B window."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, GateCalibration, luttinger_frequency)

D = Path(__file__).resolve().parent.parent
cal = json.load(open(D / "hera_scratch" / "cal_run5.json"))
gc = GateCalibration(c_tg=cal["c_tg"], c_bg=cal["c_bg"],
                     n_offset=cal["n_offset"] * 1e16, D_offset=cal["D_offset"] * 1e9)

fig, ax = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for j, rid in enumerate([6, 7]):
    r = open_run(str(D / "data" / str(rid)))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    cur = current_channel(list(ch.values()))
    B = r.col("magnet_field")
    I = r.col(cur.col) / cur.gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    SPOT = {6: (+0.9836, +1.1661), 7: (-0.2770, -0.4650)}  # from the run comment (gates not fp'd on 1D field sweeps)
    Vtg, Vbg = SPOT[rid]
    n, Dfield = gc.n_D(Vtg, Vbg)
    F_full = luttinger_frequency(n)
    T = r.col("T_sample")
    print(f"\n=== run {rid}: {r.rows} pts, B {B.min():.3f}..{B.max():.3f} T, interrupted={r.interrupted}")
    print(f"    (Vtg,Vbg)=({Vtg:+.4f},{Vbg:+.4f}) -> n={n*1e-16:+.3f}e12 cm^-2, D={Dfield*1e-9:+.4f} V/nm")
    print(f"    R {R.min():.1f}..{R.max():.1f} Ohm; T_sample {T.mean():.3f} K ({T.min():.3f}-{T.max():.3f})")
    print(f"    full-density Onsager F = {F_full:.2f} T (g=4)")

    # raw
    a = ax[j, 0]
    a.plot(B, R, "-", lw=0.6)
    a.set_xlabel("B (T)"); a.set_ylabel("Rxx (Ohm)"); a.set_title(f"run {rid} raw  n={n*1e-16:+.2f}e12")

    # onset
    fs = r.meta["measurement_config"]
    try:
        o = sdh_onset(R, B, r_full_scale=None)
        print(o.summary())
        out[rid] = dict(onset_b=float(o.onset_b), tones=[(float(t.freq), float(t.contrast), float(t.onset_b)) for t in o.tones])
    except Exception as e:
        print(f"    sdh_onset FAILED: {type(e).__name__}: {e}")
        out[rid] = dict(error=str(e))

    # FFT over the high-B window
    for b_lo, c in [(1.5, "C0"), (3.0, "C1"), (5.0, "C2")]:
        m = B > b_lo
        if m.sum() < 30:
            continue
        f, sp = sdh_fft(R[m][:, None], B[m], b_range=None, nfft=4096, bg_degree=5, log=False)
        s = sp[0]
        ax[j, 1].plot(f, s / s[(f > 2)].max(), c, lw=0.8, label=f"B>{b_lo} T")
        pk = f[(f > 2)][np.argmax(s[(f > 2)])]
        print(f"    FFT B>{b_lo} T: peak at F = {pk:.2f} T  (dF_res = {1/(1/b_lo - 1/B.max()):.2f} T)")
    ax[j, 1].axvline(abs(F_full), color="k", ls="--", lw=1, label=f"F_full={abs(F_full):.1f} T")
    ax[j, 1].set_xlim(0, max(60, abs(F_full) * 2)); ax[j, 1].set_xlabel("F (T)"); a.set_ylabel("|FFT|")
    ax[j, 1].legend(fontsize=7); ax[j, 1].set_title(f"run {rid} SdH FFT (1/B)")

    # R vs 1/B, background-subtracted, to eyeball periodicity
    m = B > 1.0
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[j, 2].plot(1 / B[m], R[m] - bg, "-", lw=0.7)
    ax[j, 2].set_xlabel("1/B (1/T)"); ax[j, 2].set_ylabel("dRxx (Ohm)"); ax[j, 2].set_title(f"run {rid} detrended vs 1/B")

fig.tight_layout()
fig.savefig(D / "hera_scratch" / "spot_runs67.png", dpi=110)
print("\nwrote spot_runs67.png")
json.dump(out, open(D / "hera_scratch" / "spot_onset.json", "w"), indent=1)
