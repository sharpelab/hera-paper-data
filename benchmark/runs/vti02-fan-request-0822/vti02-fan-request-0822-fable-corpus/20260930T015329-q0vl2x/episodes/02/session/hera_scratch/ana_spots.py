# Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
# Raw MR -> sdh_onset -> sdh_fft; tones vs F_L. Outputs: spot{6,7}_raw.png, spot{6,7}_fft.png
import json
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

OUT = "hera_scratch"
results = {}

for rid, n_e12, label in ((6, 3.2, "electron"), (7, -1.2, "hole")):
    r = open_run(f"data/{rid}")
    mc = r.meta["measurement_config"]
    # I_bias: sr1 oscillator amplitude / bias resistor
    amp = None
    for k, v in (r.meta.get("instruments") or {}).items():
        if "sr1" in k and isinstance(v, dict):
            amp = v.get("amplitude", amp)
    if amp is None:
        amp = 1.0  # fallback; cell design quoted 10 nA at 100 MOhm
        print(f"run {rid}: sr1 amplitude not in instruments snapshot -> assuming {amp} V")
    I_bias = amp / mc["bias_resistor"]
    B = r.col("magnet_field")
    order = np.argsort(B)
    B = B[order]
    R = (r.col("sr1_X") / 1.0)[order] / I_bias  # sr1 unity gain
    fs = 50e-6 / I_bias
    print(f"\n================ run {rid} ({label}, n = {n_e12:+.1f}e12) ================")
    print(f"I_bias = {I_bias*1e9:.2f} nA, full scale = {fs:.0f} Ohm; R range {R.min():.1f} - {R.max():.1f} Ohm")
    F_L = float(luttinger_frequency(abs(n_e12) * 1e16))
    print(f"F_L = {F_L:.2f} T")

    # raw MR
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {label} n={n_e12:+.1f}e12, D=0, T=1.2 K")
    fig.tight_layout(); fig.savefig(f"{OUT}/spot{rid}_raw.png", dpi=120); plt.close(fig)

    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=fs)
        print(on.summary())
        results[rid] = dict(onset_b=float(on.onset_b),
                            tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b),
                                        censored=bool(t.censored), marginal=bool(t.marginal),
                                        harmonic_of=t.harmonic_of)
                                   for t in on.tones])
        cutoff = on.onset_b
    except SdhOnsetError as e:
        print(f"run {rid}: SdhOnsetError: {e}")
        results[rid] = dict(error=str(e))
        cutoff = None

    # FFT above onset, stability over bg_degree and cutoff
    if cutoff is not None:
        fig, ax = plt.subplots(figsize=(9, 4))
        for co, deg, sty in ((cutoff, 5, "-"), (cutoff * 1.3, 5, "--"), (cutoff, 7, ":")):
            freqs, spec = sdh_fft(R[:, None], B, b_range=(co, B.max()), bg_degree=deg)
            ax.plot(freqs, spec[0] / spec[0].max(), sty, lw=1,
                    label=f"cutoff {co:.2f} T, deg {deg}")
        ax.axvline(F_L, color="k", lw=0.8, alpha=0.6)
        ax.text(F_L, 1.0, " F_L", va="top")
        ax.set_xlim(0, 1.6 * F_L)
        ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (norm)")
        ax.set_title(f"run {rid} SdH FFT — {label}; F_L = {F_L:.1f} T")
        ax.legend(fontsize=8)
        fig.tight_layout(); fig.savefig(f"{OUT}/spot{rid}_fft.png", dpi=120); plt.close(fig)
        results[rid]["F_L"] = F_L

with open(f"{OUT}/spot_results.json", "w") as f:
    json.dump(results, f, indent=1)
print("\nsaved:", json.dumps(results, indent=1))
