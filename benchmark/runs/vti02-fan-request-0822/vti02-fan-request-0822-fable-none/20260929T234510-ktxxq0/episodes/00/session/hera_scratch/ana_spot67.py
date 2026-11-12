# Runs 6 & 7 — SdH spot checks: FFT in 1/B + per-tone onsets.
# Run 6: electron, n = +3.2e12, B 0->10 T (10 mT above 1 T).
# Run 7: hole, n = -1.2e12, B 10->0.3 T (20 mT).
import numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

OUT = "hera_scratch"

def load(rid):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col(cur.col) / cur.gain
    v = [c for c in chans if c.cid == "sr1"][0]
    R = (r.col(v.col) / v.gain) / I
    B = r.col("magnet_field")
    sens = r.meta["measurement_config"].get("sr1_sensitivity", None)
    return r, B, R, np.median(np.abs(I)), sens

fig, axs = plt.subplots(2, 2, figsize=(13, 8))
results = {}
for row, (rid, brng, tag) in enumerate([(6, (1.5, 10.0), "e: n=+3.2e12"),
                                        (7, (1.5, 10.0), "h: n=-1.2e12")]):
    r, B, R, Imed, sens = load(rid)
    order = np.argsort(B)
    B, R = B[order], R[order]
    ax = axs[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw Rxx — {tag} (I~{Imed*1e9:.2f} nA)")
    # FFT
    freqs, spec = sdh_fft(R[:, None], B, b_range=brng, nfft=4096, bg_degree=5, log=False)
    sp = spec[0]
    ax2 = axs[row, 1]
    ax2.plot(freqs, sp / sp.max(), lw=0.8)
    ax2.set_xlim(0, 80); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT mag (norm)")
    ax2.set_title(f"run {rid} SdH FFT, B in [{brng[0]}, {brng[1]}] T")
    # top peaks
    from scipy.signal import find_peaks
    pk, props = find_peaks(sp, height=0.05 * sp.max(), distance=5)
    top = sorted(zip(freqs[pk], sp[pk]), key=lambda t: -t[1])[:8]
    print(f"run {rid} FFT peaks (F, rel amp): " + ", ".join(f"({f:.1f} T, {a/sp.max():.2f})" for f, a in top))
    for f, a in top:
        ax2.axvline(f, color="0.7", lw=0.4)
    results[rid] = dict(peaks=[(float(f), float(a / sp.max())) for f, a in top])
    # onsets
    try:
        so = sdh_onset(R, B, b_lo=0.3, r_full_scale=(50e-6 / 1.0) / Imed)
        print(f"run {rid} onset summary:\n{so.summary()}")
        results[rid]["onset_b"] = float(so.onset_b)
        results[rid]["tones"] = [(float(t.freq), float(t.onset_b), bool(t.marginal), t.harmonic_of) for t in so.tones]
    except SdhOnsetError as e:
        print(f"run {rid} sdh_onset: {e}")
        results[rid]["onset_error"] = str(e)

fig.tight_layout()
fig.savefig(f"{OUT}/spot67_fft.png", dpi=120)
print("saved", f"{OUT}/spot67_fft.png")

# expectations at run-5 calibration
h_over_e = 4.135667e-15
for n12, lab in [(3.2, "e-spot"), (-1.2, "h-spot")]:
    n = abs(n12) * 1e16
    print(f"{lab}: F_full(deg4) = {h_over_e*n/4:.1f} T; deg-2 (spin-split/valley-polarized) = {h_over_e*n/2:.1f} T")
with open(f"{OUT}/spot67_results.json", "w") as f:
    json.dump(results, f, indent=1)
