"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12):
raw R(B), sdh_onset per tone, sdh_fft vs F_L and the model templates."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

D = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parent
runs = {6: dict(n=3.2, side="electron"), 7: dict(n=-1.2, side="hole")}
I_BIAS = 10e-9; SENS = 50e-6
res = {}
fig, axs = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, info) in enumerate(runs.items()):
    r = open_run(D / str(rid))
    print(f"===== run {rid} =====\n{summarize_run(r)}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    print(f"T_sample {T.min():.3f}-{T.max():.3f} K; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.1f}..{R.max():.1f} Ohm; "
          f"R(B<0.5) med {np.median(R[B < 0.5]):.1f}; |V|max/FS = {np.abs(V).max()/SENS:.2f}")
    FL = float(luttinger_frequency(abs(info["n"]) * 1e16))
    print(f"F_L = {FL:.2f} T")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(np.abs(R), B, r_full_scale=SENS / I_BIAS, b_lo=0.3)
            print(on.summary())
            res[rid] = dict(onset_b=on.onset_b, onset_freq=on.onset_freq, clip_high_b=on.clip_high_b,
                            tones=[dict(freq=t.freq, onset_b=t.onset_b, censored=t.censored, marginal=t.marginal,
                                        harmonic_of=t.harmonic_of, n_periods=t.n_periods, delta_f=t.delta_f(B.max()) if callable(t.delta_f) else None,
                                        contrast=t.contrast) for t in on.tones],
                            untracked=on.untracked)
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); on = None; res[rid] = dict(error=str(e))
        for ww in w: print("  warn:", ww.message)
    # raw
    ax = axs[row, 0]; ax.plot(B, R, lw=0.8, color="#1f4e79"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm), signed")
    ax.set_title(f"run {rid} {info['side']} n={info['n']:+.1f}e12 D=0 — raw sr1/sr0")
    # bg-subtracted vs 1/B
    for cut, ax in ((on.onset_b if on else 1.5, axs[row, 1]),):
        m = B >= cut
        p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
        ax.plot(1 / B[m], dR, lw=0.8, color="#1f4e79"); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg in B")
        ax.set_title(f"bg-subtracted, B >= {cut:.2f} T")
    # FFT for a few cutoffs
    ax = axs[row, 2]
    cuts = sorted({round(c, 2) for c in ([on.onset_b] if on else []) + [1.5, 2.0, 3.0]})
    for c, col in zip(cuts, ["#1f4e79", "#c0504d", "#4f9d69", "#7f6000"]):
        m = B >= c
        if m.sum() < 30: continue
        f, sp = sdh_fft(R[m][:, None], B[m], b_range=(c, B.max()), bg_degree=5, log=False, nfft=4096)
        sp = sp[0]; sel = (f > 1) & (f < 3 * FL)
        ax.plot(f[sel], sp[sel] / sp[sel].max(), lw=1, color=col, label=f"cut {c:.2f} T")
        pk = f[sel][np.argsort(sp[sel])[::-1][:12]]
        print(f"  FFT cut {c:.2f}: top freqs (T) {np.round(np.sort(pk), 1)}")
    ax.axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f} T")
    if info["n"] > 0:
        for fr, lab in ((0.276 * FL, "ABAB light"), (0.724 * FL, "ABAB heavy")): ax.axvline(fr, color="gray", ls=":", lw=1)
    ax.set_xlim(0, 2 * FL); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.legend(fontsize=7); ax.set_title("FFT in 1/B (linear R)")
fig.tight_layout(); fig.savefig(OUT / "spot_runs67.png", dpi=110)
json.dump(res, open(OUT / "spot_runs67.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
