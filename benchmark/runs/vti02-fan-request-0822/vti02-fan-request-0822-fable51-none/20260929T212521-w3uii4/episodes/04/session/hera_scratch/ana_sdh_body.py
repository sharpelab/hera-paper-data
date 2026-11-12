"""Runs 6 + 7 — `sdh-spot-check` at D = 0 (region-A cal, run 5). Raw Rxx(B) first, then the SdH content: deg-5 B-space
background removed and plotted vs 1/B, FFT spectra (hera.analysis.sdh_fft) for three low-B cut-offs, and the per-tone
onset read (sdh_onset). F_L marked at the raw-cal density and at 0.89x (see the take below)."""
import warnings
from scipy.signal import find_peaks
from hera.analysis import resolve_channels, current_channel, sdh_onset

spots = {6: ("electron", +3.2), 7: ("hole", -1.2)}
fig, axes = plt.subplots(2, 3, figsize=(17, 8.5))
for k, (rid, (side, n_raw)) in enumerate(spots.items()):
    r = run(rid)
    chs = resolve_channels(r.meta); cur = current_channel(chs); vch = [c for c in chs if c.cid == "sr1"][0]
    B = r.col("magnet_field"); I = r.col(cur.col) / cur.gain; R = (r.col(vch.col) / vch.gain) / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    F_L_raw = float(luttinger_frequency(abs(n_raw) * 1e16))
    # raw
    ax = axes[k, 0]; ax.plot(B, R, lw=0.8, color="C0"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx = (sr1_X/gain) / I_drain (Ohm)")
    ax.set_title(f"run {rid} raw — {side}, n_raw = {n_raw:+.1f}e12, D = 0; I = {np.nanmean(I)*1e9:.2f} nA, T = {r.meta['measurement_config'].get('sample_temperature:', float('nan')):.2f} K", fontsize=9)
    # SdH vs 1/B (B >= 1 T)
    m = B >= 1.0
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[k, 1]; ax.plot(1 / B[m], dR, lw=0.8, color="C0"); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg in B removed")
    ax.set_title(f"run {rid} — SdH vs 1/B, B >= 1 T", fontsize=9)
    # spectra
    ax = axes[k, 2]
    for lo, c in ((1.0, "C0"), (1.5, "C1"), (2.5, "C2")):
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False)
        sp = spec[0]; sp = sp / sp[f > 2].max()
        ax.plot(f, sp, c, lw=0.9, label=f"B in [{lo}, {B.max():.0f}] T")
        if lo == 1.5:
            pk, _ = find_peaks(sp, height=0.12, distance=3)
            pk = [p for p in pk if f[p] > 2]
            print(f"run {rid} FFT peaks (B 1.5-10 T, norm.): " + ", ".join(f"{f[p]:.1f} T ({sp[p]:.2f})" for p in pk))
            for p in pk: ax.annotate(f"{f[p]:.1f}", (f[p], sp[p]), fontsize=7, textcoords="offset points", xytext=(0, 3), ha="center")
    ax.axvline(F_L_raw, color="k", ls="--", lw=1, label=f"F_L(n_raw) = {F_L_raw:.1f} T")
    ax.axvline(0.89 * F_L_raw, color="r", ls=":", lw=1, label=f"0.89 F_L = {0.89*F_L_raw:.1f} T")
    ax.set_xlim(0, 45); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm. to max above 2 T)"); ax.set_title(f"run {rid} — SdH spectrum", fontsize=9); ax.legend(fontsize=7)
    # onset read
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
            print(f"run {rid} ({side}): sdh_onset -> onset {on.onset_b:.2f} T carried by {on.onset_freq:.1f} T"
                  f"{' (censored: persists to record edge)' if any(t.censored and t.freq == on.onset_freq for t in on.tones) else ''}; noise sigma {on.noise_sigma:.1f} Ohm")
            for t in on.tones:
                print(f"   tone {t.freq:5.1f} T  contrast {t.contrast:6.1f}  onset {t.onset_b:.2f} T" + (f"  flagged ~{t.freq/t.harmonic_of:.1f}x of {t.harmonic_of:.1f}" if t.harmonic_of else "") + ("  near-residual" if t.near_residual else ""))
            if on.untracked: print("   untracked:", on.untracked)
        except ValueError as e:
            print(f"run {rid}: sdh_onset failed: {e}")
    print(f"   Rxx range {R.min():.0f}..{R.max():.0f} Ohm (fs {R.max()/5e3:.2f} of the 5 kOhm scale); Rxx(10 T) = {R[-1]:.0f} Ohm; "
          f"drain current {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA\n")
fig.tight_layout(); plt.show()
