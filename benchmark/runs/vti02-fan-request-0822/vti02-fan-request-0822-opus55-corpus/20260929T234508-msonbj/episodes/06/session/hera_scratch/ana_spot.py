"""Spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw R(B), onset, FFT vs F_L, model table."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

SENS = 50e-6
out = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = np.abs(V / I)
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    Ibias = np.median(np.abs(I))
    print(f"\n=== run {rid}  n={n:+.2f}e12  B {B.min():.2f}-{B.max():.2f} T  pts {len(B)}")
    print(f"I_drain med {Ibias*1e9:.2f} nA; R(B~0) {R[:3].mean():.1f} Ohm; R max {R.max():.1f} at {B[R.argmax()]:.2f} T; "
          f"sr1 |X| max {np.abs(V).max()*1e6:.2f} uV of {SENS*1e6:.0f} uV FS ({100*np.abs(V).max()/SENS:.1f}%)")
    print(f"T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; I_tg {r.col('k_2400_tg_curr').min()*1e12:+.0f}..{r.col('k_2400_tg_curr').max()*1e12:+.0f} pA; "
          f"I_bg {r.col('k_2400_bg_curr').min()*1e12:+.0f}..{r.col('k_2400_bg_curr').max()*1e12:+.0f} pA")
    nSI = n*1e16; FL = float(luttinger_frequency(abs(nSI)))
    print(f"F_L = {FL:.2f} T")
    # model table
    try:
        Ef, orbs = M.abab_fs(nSI)
        print("ABAB orbits:", [(round(f, 2)) for f, k in orbs], "masses:", [(round(f, 2), round(m, 3)) for f, m in M.abab_mstar(nSI)])
    except Exception as e:
        print("abab err", e)
    try:
        res = M.abca_fs(nSI); print("ABCA:", res[1:], "mstar:", M.abca_mstar(nSI))
    except Exception as e:
        print("abca err", e)
    # uniform-B segment only for onset/FFT (run 6: 10 mT above 1 T)
    sel = B >= (1.0 if rid == 6 else 0.3)
    Bs, Rs = B[sel], R[sel]
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=SENS / Ibias, b_lo=Bs.min())
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None
    ax[row, 0].plot(B, R, lw=0.8); ax[row, 0].set_xlabel("B (T)"); ax[row, 0].set_ylabel("|Rxx| (Ohm)")
    ax[row, 0].set_title(f"run {rid} raw, n={n:+.1f}e12, D=0")
    # background-subtracted in B
    for lo in ([2.0, 3.0, 4.0] if rid == 6 else [2.0, 3.0, 4.0]):
        m = Bs >= lo
        cf = np.polyfit(Bs[m], Rs[m], 5); dR = Rs[m] - np.polyval(cf, Bs[m])
        if lo == 3.0:
            ax[row, 1].plot(1 / Bs[m], dR, lw=0.7); ax[row, 1].set_xlabel("1/B (1/T)"); ax[row, 1].set_ylabel("dR (Ohm), poly5 in B")
            ax[row, 1].set_title(f"run {rid} bg-sub (B>={lo})")
        f, S = sdh_fft(Rs[m][:, None], Bs[m], b_range=(lo, Bs.max()), bg_degree=5, log=False)
        S = S[0]
        ax[row, 2].plot(f, S / S.max(), lw=0.8, label=f"B>={lo}")
        k = (f > 3)
        idx = np.argsort(S[k])[::-1]
        # local maxima
        from scipy.signal import find_peaks
        pk, _ = find_peaks(S, prominence=0.05 * S.max())
        pk = [p for p in pk if f[p] > 3]
        pk = sorted(pk, key=lambda p: -S[p])[:6]
        print(f"  FFT B>={lo}: peaks " + ", ".join(f"{f[p]:.1f} T ({S[p]/S.max():.2f})" for p in pk) + f"; dF = {1/(1/lo-1/Bs.max()):.2f} T")
    ax[row, 2].axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f}")
    ax[row, 2].set_xlim(0, 2.2 * FL); ax[row, 2].set_xlabel("F (T)"); ax[row, 2].legend(fontsize=7)
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
