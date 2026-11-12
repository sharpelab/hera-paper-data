"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D = 0, T_sample ~1.2 K.
Raw R(B) first, then sdh_onset (per-tone onsets) and sdh_fft in 1/B; compares tones to the Luttinger
frequency of the calibrated density (single-FS, 4-fold) and to a two-band split."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError

out = {}
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    print(f"===== run {rid} =====\n{summarize_run(r)}")
    chans = resolve_channels(r.meta); cur = current_channel(chans)
    v = [c for c in chans if not c.is_current][0]
    I = r.col(cur.col) / cur.gain; V = r.col(v.col) / v.gain
    R = V / I; B = r.col("magnet_field")
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    mc = r.meta["measurement_config"]
    sens = r.meta["instruments"].get("sr1", {}).get("sensitivity") if isinstance(r.meta.get("instruments"), dict) else None
    fs = 50e-6 / 10e-9
    print(f"I_drain {I.mean()*1e9:.3f} nA (range {I.min()*1e9:.3f}-{I.max()*1e9:.3f}); R range {R.min():.1f}..{R.max():.1f} Ohm; "
          f"R(B<0.2) = {R[B<0.2].mean() if (B<0.2).any() else R[:3].mean():.1f}; fs {fs:.0f} Ohm -> max fs frac {R.max()/fs:.2f}")
    F_L = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"Luttinger F (single FS, 4-fold) for |n| = {abs(n12)} e12: {F_L:.1f} T")
    # onset
    try:
        so = sdh_onset(R, B, b_lo=0.5, r_full_scale=fs)
        print(so.summary())
        out[rid] = dict(onset_b=float(so.onset_b), onset_freq=float(so.onset_freq),
                        tones=[(float(t.freq), float(t.contrast), float(t.onset_b), bool(t.marginal), t.harmonic_of) for t in so.tones])
    except SdhOnsetError as e:
        print("sdh_onset failed:", e); so = None
    # FFT over a couple of windows
    ax = axes[k]
    ax[0].plot(B, R, lw=0.8); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 — raw")
    ax[1].plot(1 / B[B > 0.8], R[B > 0.8], lw=0.8); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_title("raw vs 1/B")
    for lo, hi, c in [(1.5, 10.0, "k"), (3.0, 10.0, "C1"), (1.5, 5.0, "C2")]:
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=2048, bg_degree=5, log=False)
        sp = spec[0]; sel = (f > 1.0) & (f < 80)
        ax[2].plot(f[sel], sp[sel] / sp[sel].max(), c, lw=1, label=f"{lo}-{hi} T (dF={1/(1/lo-1/hi):.1f} T)")
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"  FFT {lo}-{hi} T top peaks (T): {np.round(np.sort(pk), 1)}")
    ax[2].axvline(F_L, color="r", ls="--", label=f"F_L(n) = {F_L:.1f} T"); ax[2].axvline(F_L / 2, color="r", ls=":", label="F_L/2")
    ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)"); ax[2].legend(fontsize=7); ax[2].set_title("SdH FFT in 1/B (poly-5 bg in B)")
    # filling factors at minima: nu = n h / (e B)
    h_e = 4.135667e-15
    nu = abs(n12) * 1e16 * h_e / B
    out[rid]["nu_at_10T"] = float(abs(n12) * 1e16 * h_e / 10)
    print(f"  nu at 10 T = {abs(n12)*1e16*h_e/10:.1f}; nu at 5 T = {abs(n12)*1e16*h_e/5:.1f}")
    # locate deep minima above 3 T
    from scipy.signal import find_peaks, savgol_filter
    m = B > 2.5
    Rs = savgol_filter(R[m], 9, 2)
    mins, _ = find_peaks(-Rs, prominence=0.15 * (Rs.max() - Rs.min()))
    print("  minima B (T) / nu:", [(round(float(B[m][i]), 2), round(float(nu[m][i]), 1)) for i in mins])
    out[rid]["minima"] = [(float(B[m][i]), float(nu[m][i])) for i in mins]
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_6_7.png", dpi=110)
json.dump(out, open("hera_scratch/sdh_spot_6_7.json", "w"), indent=1, default=str)
print("saved hera_scratch/sdh_spot_6_7.png")
