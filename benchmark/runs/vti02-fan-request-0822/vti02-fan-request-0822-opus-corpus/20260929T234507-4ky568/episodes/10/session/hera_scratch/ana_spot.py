"""SdH spot-check read, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).

Raw R(B) first, then sdh_onset + sdh_fft in 1/B against F_L.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

CAL = json.load(open("hera_scratch/cal_run5.json"))
H, E = 6.62607015e-34, 1.602176634e-19


def trace(fid):
    r = open_run(f"data/{fid}")
    mc = r.meta["measurement_config"]
    B = r.col("magnet_field")
    I = r.col("sr0_X") / mc["sr0_gain"]          # drain current, A
    gain_v = 1.0                                  # sr1 unity (device card)
    R = (r.col("sr1_X") / gain_v) / I
    o = np.argsort(B)
    return r, B[o], R[o], I[o], mc


def report(fid, n_cm2, label):
    r, B, R, I, mc = trace(fid)
    n_si = abs(n_cm2) * 1e4                       # cm^-2 -> m^-2
    FL = luttinger_frequency(n_si)
    print(f"\n===== run {fid} — {label}: n = {n_cm2:+.2e} cm^-2, F_L = {FL:.2f} T")
    print(f"  B {B.min():.3f} .. {B.max():.3f} T, {len(B)} pts, "
          f"dB median {np.median(np.diff(B))*1e3:.1f} mT")
    print(f"  I_bias = {np.median(np.abs(I))*1e9:.3f} nA  (spread "
          f"{np.abs(I).min()*1e9:.3f}-{np.abs(I).max()*1e9:.3f} nA)")
    print(f"  |R|: min {np.abs(R).min():.1f}  max {np.abs(R).max():.1f}  "
          f"@B=0-edge {np.abs(R)[0]:.1f} Ohm")
    Tc = r.col("T_sample")
    print(f"  T_sample {Tc.min():.3f}-{Tc.max():.3f} K")
    for g in ("k_2400_tg_curr", "k_2400_bg_curr"):
        c = r.col(g)
        print(f"  {g}: med {np.median(c)*1e12:.0f} pA, min {c.min()*1e12:.0f}, max {c.max()*1e12:.0f}")

    # soft-clip check against full scale
    sens = None
    try:
        sens = r.meta["instruments"]["sr1"]["parameters"]["sensitivity"]["value"]
    except Exception:
        pass
    print(f"  sr1 sensitivity from snapshot: {sens}")

    Rabs = np.abs(R)
    # --- onset
    on = None
    try:
        on = sdh_onset(Rabs, B, b_lo=0.3)
        print(on.summary())
    except SdhOnsetError as e:
        print(f"  SdhOnsetError: {e}")

    # --- FFT at a few cutoffs (stability)
    fig, ax = plt.subplots(3, 1, figsize=(9, 11))
    ax[0].plot(B, Rabs, lw=0.7)
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("|Rxx| (Ohm)")
    ax[0].set_title(f"run {fid} raw — {label}, n={n_cm2:+.2e} cm^-2")

    cuts = [c for c in (0.5, 1.0, 1.5, 2.0, 3.0) if c < B.max() * 0.7]
    for c in cuts:
        fr, sp = sdh_fft(Rabs[:, None], B, b_range=(c, B.max()), bg_degree=5, log=False)
        s = sp[0]
        m = fr < 3 * FL + 10
        ax[1].plot(fr[m], s[m] / np.nanmax(s[m]), lw=0.9, label=f"cutoff {c} T")
        # peak list
        pk = []
        for i in range(2, len(fr) - 2):
            if fr[i] < 2.0 or fr[i] > 3 * FL + 10:
                continue
            if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.08 * np.nanmax(s[m]):
                pk.append((fr[i], s[i] / np.nanmax(s[m])))
        pk.sort(key=lambda t: -t[1])
        print(f"  FFT cutoff {c:.1f}-{B.max():.1f} T  dF={1/(1/c - 1/B.max()):.2f} T ; peaks "
              + ", ".join(f"{f:.1f}T({a:.2f}, {f/FL:.3f}FL)" for f, a in pk[:6]))
    ax[1].axvline(FL, color="k", ls="--", lw=1, label=f"F_L={FL:.1f} T")
    ax[1].set_xlabel("F (T)"); ax[1].set_ylabel("norm amp"); ax[1].legend(fontsize=7)

    # background-subtracted oscillations vs 1/B
    from numpy.polynomial import polynomial as P
    m = B > 0.4
    cf = np.polyfit(B[m], Rabs[m], 5)
    dR = Rabs[m] - np.polyval(cf, B[m])
    ax[2].plot(1 / B[m], dR, lw=0.7)
    ax[2].set_xlabel("1/B (1/T)"); ax[2].set_ylabel("dRxx (Ohm)")
    fig.tight_layout()
    fig.savefig(f"hera_scratch/spot_run{fid}.png", dpi=110)
    return on


if __name__ == "__main__":
    report(6, 3.20e12, "electron")
    report(7, -1.20e12, "hole")
