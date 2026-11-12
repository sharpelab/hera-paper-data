"""SdH spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B),
background-subtracted trace vs 1/B, FFT, per-tone onset. Feeds the landau-fan design."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel, sdh_fft,
                           sdh_onset, SdhOnsetError, GateCalibration, luttinger_frequency)

CAL = json.load(open("hera_scratch/cal_run5.json"))
gc = GateCalibration(CAL["c_tg"], CAL["c_bg"], n_offset=CAL["n_offset"] * 1e16,
                     D_offset=CAL["D_offset"] * 1e9)

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for k, (rid, nspot, lbl) in enumerate([(6, +3.2, "electron"), (7, -1.2, "hole")]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col_at(cur.idx) / cur.gain
    v = [c for c in chans if not c.is_current and c.cid == "sr1"][0]
    R = (r.col_at(v.idx) / v.gain) / I
    T = r.col("T_sample")
    o = np.argsort(B)
    B, R, I = B[o], np.abs(R[o]), I[o]
    FL = luttinger_frequency(abs(nspot) * 1e16)
    print(f"\n=== run {rid} ({lbl}, n={nspot:+.2f}e12) ===")
    print(f"  {len(B)} pts, B {B.min():.3f}..{B.max():.3f} T; T {T.mean():.3f} K ({T.min():.3f}-{T.max():.3f})")
    print(f"  |I| med {np.median(np.abs(I))*1e9:.3f} nA; R {R.min():.1f}..{R.max():.1f} Ohm (R@Bmin {R[0]:.1f}, R@Bmax {R[-1]:.1f})")
    print(f"  F_Luttinger (full n, 4-fold) = {FL:.1f} T")
    fs_ohm = 50e-6 / np.median(np.abs(I))
    print(f"  full-scale R at sr1 50 uV = {fs_ohm:.0f} Ohm; max R / FS = {R.max()/fs_ohm:.2f}")

    # raw
    ax = axes[0, k]
    ax.plot(B, R, lw=0.8)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {lbl}, n={nspot:+.2f}e12, T={T.mean():.2f} K")

    # background-subtracted vs 1/B
    m = B > 0.5
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    dR = R[m] - bg
    ax = axes[1, k]
    ax.plot(1.0 / B[m], dR, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {rid} — deg-5 B-space background removed (B>0.5 T)")

    # FFT over a few windows
    ax = axes[2, k]
    for blo, bhi in [(1.0, 10.0), (2.0, 10.0), (4.0, 10.0), (6.0, 10.0)]:
        if B.max() < bhi - 0.5:
            bhi = B.max()
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=2048, bg_degree=5, log=False)
        s = sp[0]
        ax.plot(f, s / (s[f > 2].max() or 1), lw=0.9, label=f"{blo:.0f}-{bhi:.0f} T")
        pk = f[(f > 3) & (f < 200)][np.argsort(s[(f > 3) & (f < 200)])[-4:]][::-1]
        print(f"  FFT {blo:.0f}-{bhi:.0f} T: df={1/(1/blo-1/bhi):.1f} T; top peaks (T): {np.round(pk,1)}")
    ax.axvline(FL, color="k", ls=":", label=f"F_L={FL:.0f} T")
    ax.axvline(FL / 2, color="grey", ls=":", lw=0.8, label="F_L/2")
    ax.axvline(FL / 4, color="grey", ls="--", lw=0.8, label="F_L/4")
    ax.set_xlim(0, min(1.6 * FL, 120)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} SdH FFT in 1/B")

    try:
        so = sdh_onset(R, B, b_lo=0.4, r_full_scale=fs_ohm)
        print(so.summary())
        out[rid] = dict(onset_b=float(so.onset_b), onset_freq=float(so.onset_freq),
                        tones=[(float(t.freq), float(t.contrast), float(t.onset_b)) for t in so.tones])
    except SdhOnsetError as e:
        print(f"  sdh_onset FAILED: {e}")
        out[rid] = dict(error=str(e))

fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
json.dump(out, open("hera_scratch/spot_runs67.json", "w"), indent=1)
print("\nsaved hera_scratch/spot_runs67.png")
