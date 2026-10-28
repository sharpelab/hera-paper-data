# SdH spot-check analysis: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12)
# Onset via sdh_onset, tones via sdh_fft; compare vs F_L and model F(n).
import numpy as np, json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02"
out = {}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))

for row, (rid, nlab, n_cm2) in enumerate([(6, "electron n=+3.2e12", +3.2e12), (7, "hole n=-1.2e12", -1.2e12)]):
    run = open_run(f"{BASE}/data/{rid}")
    B = run.col("magnet_field")
    R = run.col("sr1_X") / 1.0 / 10e-9  # unity gain, I_bias 10 nA
    order = np.argsort(B)
    B, R = B[order], R[order]
    F_L = float(luttinger_frequency(abs(n_cm2) * 1e4))  # cm^-2 -> m^-2

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.5)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw — {nlab}")

    # onset
    try:
        onset = sdh_onset(R, B, b_lo=0.3)
        out[rid] = {"onset_b": float(onset.onset_b),
                    "tones": [{"f": float(t.freq), "onset": float(t.onset_b),
                               "marginal": bool(getattr(t, "marginal", False)),
                               "censored": bool(getattr(t, "censored", False))}
                              for t in onset.tones]}
        print(f"run {rid}: onset_b = {onset.onset_b:.3f} T")
        for t in onset.tones:
            print(f"   tone f={t.freq:7.2f} T  onset={t.onset_b:5.2f} T  marginal={getattr(t,'marginal',None)} censored={getattr(t,'censored',None)}  f/F_L={t.freq/F_L:.3f}")
    except SdhOnsetError as e:
        out[rid] = {"onset_error": str(e)}
        print(f"run {rid}: SdhOnsetError: {e}")

    # FFT, full record above 1 T and split windows
    for col, (blo, bhi, lab) in enumerate([(1.0, float(B.max()), "full"), (None, None, "split")]):
        ax = axes[row, col + 1]
        if lab == "full":
            fr, amp = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=4096, log=False)
            a = np.asarray(amp).reshape(-1, len(fr))[0]
            ax.plot(fr, a, lw=0.8)
            ax.axvline(F_L, color="k", ls="--", label=f"F_L={F_L:.1f} T")
            ax.set_xlim(0, 1.6 * F_L)
            ax.set_title(f"run {rid} FFT {blo:.1f}-{bhi:.1f} T")
            ax.legend(fontsize=7)
            out[rid]["F_L"] = F_L
            # store spectrum peaks
            out[rid]["fft_freqs"] = fr[np.argsort(a)[::-1][:12]].tolist()
        else:
            Bmax = float(B.max())
            for (b1, b2), c in [((1.0, 0.5 * (1.0 + Bmax)), "C0"), ((0.5 * (1.0 + Bmax), Bmax), "C1")]:
                fr, amp = sdh_fft(R[:, None], B, b_range=(b1, b2), nfft=4096, log=False)
                a = np.asarray(amp).reshape(-1, len(fr))[0]
                ax.plot(fr, a / max(a.max(), 1e-12), lw=0.8, color=c, label=f"{b1:.1f}-{b2:.1f} T")
            ax.axvline(F_L, color="k", ls="--")
            ax.set_xlim(0, 1.6 * F_L)
            ax.set_title(f"run {rid} B-window split (norm)")
            ax.legend(fontsize=7)
        ax.set_xlabel("F (T)")

fig.tight_layout()
fig.savefig(f"{BASE}/hera_scratch/spot_fft.png", dpi=110)
json.dump(out, open(f"{BASE}/hera_scratch/spot_fft.json", "w"), indent=1)
print(json.dumps(out, indent=1))
