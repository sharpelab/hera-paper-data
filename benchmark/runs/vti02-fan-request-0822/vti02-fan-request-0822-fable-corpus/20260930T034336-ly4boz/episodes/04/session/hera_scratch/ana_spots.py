# SdH spot-check analysis: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0
# onset via hera.analysis.sdh_onset, tones via sdh_fft; design numbers for the fan.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, summarize_run

I_BIAS = 10e-9
SENS = 50e-6
R_FS = SENS / I_BIAS  # 5 kOhm

for fid, label, n12 in ((6, "electron n=+3.2e12", 3.2), (7, "hole n=-1.2e12", -1.2)):
    run = open_run(f"data/{fid}")
    print(f"===== run {fid} — {label} =====")
    print(summarize_run(run))
    B = run.col("magnet_field")
    R = run.col("sr1_X") / I_BIAS
    order = np.argsort(B)
    B, R = B[order], R[order]
    F_L = 2.0672 * abs(n12) * 10  # h/4e * n ; (h/4e)=1.0336e-14 T m^2 -> per 1e12 cm^-2: 10.336 T... compute properly below
    # proper: F_L = (h/(4e)) * n ; n in m^-2
    h = 6.62607015e-34; e = 1.602176634e-19
    F_L = h / (4 * e) * abs(n12) * 1e16
    print(f"F_L = {F_L:.2f} T")
    try:
        on = sdh_onset(R, B, r_full_scale=R_FS)
        print(on.summary())
        onset = on.onset_b
    except Exception as ex:
        print(f"sdh_onset: {type(ex).__name__}: {ex}")
        onset = None
    # FFT with a couple of cutoffs/degrees for stability
    for cutoff in ([onset, onset * 1.25] if onset else [1.5, 2.0]):
        for deg in (3, 5, 7):
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()), bg_degree=deg)
            sp = spec[0]
            # top peaks
            pk = []
            for i in range(2, len(sp) - 2):
                if sp[i] > sp[i-1] and sp[i] > sp[i+1] and sp[i] > 0.1 * sp.max() and freqs[i] > 1.0:
                    pk.append((freqs[i], sp[i]))
            pk.sort(key=lambda t: -t[1])
            print(f"  cutoff {cutoff:.2f} T, deg {deg}: peaks " +
                  ", ".join(f"{f:.2f} T ({a/sp.max():.2f})" for f, a in pk[:6]))
    # figures: raw, background-subtracted vs 1/B, FFT
    fig, ax = plt.subplots(3, 1, figsize=(9, 10))
    ax[0].plot(B, R, lw=0.6)
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {fid} raw — {label}")
    if onset:
        msk = B >= onset
        p = np.polyfit(B[msk], R[msk], 5)
        dR = R[msk] - np.polyval(p, B[msk])
        ax[1].plot(1 / B[msk], dR, lw=0.6)
        ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)")
        freqs, spec = sdh_fft(R[:, None], B, b_range=(onset, B.max()), bg_degree=5)
        ax[2].plot(freqs, spec[0] / spec[0].max(), lw=0.8)
        ax[2].axvline(F_L, color="r", ls="--", label=f"F_L={F_L:.1f} T")
        ax[2].axvline(0.72 * F_L, color="g", ls=":", label="0.72 F_L")
        ax[2].axvline(0.28 * F_L, color="g", ls=":", label="0.28 F_L")
        ax[2].set_xlim(0, 1.6 * F_L); ax[2].set_xlabel("F (T)"); ax[2].legend()
    fig.tight_layout()
    fig.savefig(f"hera_scratch/spot_run{fid}.png", dpi=110)
    print()
