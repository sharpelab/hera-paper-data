"""SdH spot checks: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Raw R(B), onset per tone, FFT in 1/B with real peak-finding. Feeds the landau-fan design."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, luttinger_frequency)


def trace(rid):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    volt = [c for c in chans if not c.is_current][0]
    B = r.col("magnet_field")
    I = r.col_at(cur.idx) / cur.gain          # A (gain from measurement_config)
    R = (r.col_at(volt.idx) / volt.gain) / I  # Ohm
    o = np.argsort(B)
    return r, B[o], R[o], I[o], volt.cid, r.col("T_sample")[o]


def peaks(f, s, fmax):
    m = (f > 2.0) & (f < fmax)
    fm, sm = f[m], s[m]
    idx, props = find_peaks(sm, prominence=0.08 * sm.max())
    order = np.argsort(props["prominences"])[::-1]
    return [(round(float(fm[idx[i]]), 2), round(float(sm[idx[i]] / sm.max()), 2))
            for i in order[:6]]


fig, axes = plt.subplots(3, 2, figsize=(13, 10))
summary = {}
for k, (rid, lab, nspot) in enumerate([(6, "e-side n=+3.2e12", +3.2e16),
                                       (7, "h-side n=-1.2e12", -1.2e16)]):
    r, B, R, I, cid, T = trace(rid)
    FL = float(luttinger_frequency(nspot))
    print(f"\n===== run {rid} — {lab} =====")
    print(f"  rows {len(B)}  B {B.min():.3f}..{B.max():.3f} T  R {R.min():.1f}..{R.max():.1f} Ohm"
          f"  T {T.mean():.3f} K  I {I.mean()*1e9:.2f} nA")
    print(f"  full-density Onsager F_L = {FL:.2f} T (g=4);  F/F_L for a band carrying fraction x is x*F_L")

    # noise floor: residual after a local (Savitzky-like) smooth over the flat 3-5 T stretch
    m = (B > 3) & (B < 5)
    resid = R[m] - np.convolve(R[m], np.ones(5) / 5, mode="same")
    sigma = float(np.std(resid[3:-3]))
    print(f"  point-to-point noise sigma ~ {sigma:.3f} Ohm  (at sr1 fs 5 kOhm = 50 uV/10 nA)"
          f"  -> {sigma*4:.2f} Ohm if fs raised 4x to 20 kOhm")
    print(f"  R at 10 T = {R[-1]:.0f} Ohm; R max over record {np.abs(R).max():.0f} Ohm")

    ax = axes[0, k]; ax.plot(B, R, lw=.6); ax.set_title(f"run {rid} raw — {lab}")
    ax.set_xlabel("B (T)"); ax.set_ylabel(f"R {cid} (Ohm)"); ax.grid(alpha=.3)

    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(so.summary())
        summary[rid] = dict(onset_b=float(so.onset_b), onset_freq=float(so.onset_freq),
                            tones=[(round(float(t.freq), 2), round(float(t.onset_b), 2),
                                    round(float(t.contrast), 4), t.harmonic_of is not None)
                                   for t in so.tones])
    except Exception as e:
        print(f"  sdh_onset FAILED: {type(e).__name__}: {e}")

    for b_lo, c in [(0.6, "C3"), (1.0, "C0"), (2.0, "C1"), (4.0, "C2")]:
        if B.min() > b_lo:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()), nfft=8192,
                          bg_degree=5, log=False)
        s = spec[0]
        df = 1.0 / (1.0 / b_lo - 1.0 / B.max())
        axes[1, k].plot(f, s / s.max(), c, lw=.8, label=f"B>{b_lo} T (df={df:.2f})")
        print(f"  FFT B in [{b_lo}, {B.max():.0f}] T, resolution df = {df:.2f} T: "
              f"peaks (F T, rel amp) = {peaks(f, s, 2.2*max(FL, 8))}")
    axes[1, k].axvline(FL, color="k", ls="--", lw=1, label=f"F_L={FL:.1f} T")
    axes[1, k].set_xlim(0, 2.2 * max(FL, 8)); axes[1, k].legend(fontsize=7)
    axes[1, k].set_xlabel("F (T)"); axes[1, k].set_title(f"run {rid} SdH FFT in 1/B")

    m = B > 0.5
    axes[2, k].plot(1 / B[m], R[m], lw=.6)
    axes[2, k].set_xlabel("1/B (1/T)"); axes[2, k].set_ylabel("R (Ohm)")
    axes[2, k].set_title(f"run {rid} R vs 1/B"); axes[2, k].grid(alpha=.3)

plt.tight_layout(); plt.savefig("hera_scratch/sdh_spots.png", dpi=110)
json.dump(summary, open("hera_scratch/sdh_spots.json", "w"), indent=1)
print("\nwrote hera_scratch/sdh_spots.png")
