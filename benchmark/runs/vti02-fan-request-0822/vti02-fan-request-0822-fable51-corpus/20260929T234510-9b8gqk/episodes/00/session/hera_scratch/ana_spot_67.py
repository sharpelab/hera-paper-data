"""Runs 6 + 7 — sdh-spot-check read (investigation Step 3): raw R(B) first, then bg-subtracted 1/B records,
per-tone onsets (hera.analysis.sdh_onset) and 1/B FFTs (sdh_fft) against F_L and the model's ABAB / ABCA tones."""
import sys
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

# model tones at the two spot densities (hera/models/tetralayer_fs_count/fs_count_b0.py, u_D = 0):
MODEL = {6: dict(n=+3.2, abab=(7.3, 25.8), abca=33.1, m_abab=(0.027, 0.061), m_abca=0.074),
         7: dict(n=-1.2, abab=(5.9, 6.5), abca=12.4, m_abab=(0.074, 0.032), m_abca=1.12)}
SENS, I_BIAS = 50e-6, 10e-9
WINDOWS = [(1.5, 5), (2.5, 5), (3.5, 5), (2.5, 3)]   # (B_lo cutoff, bg_degree) — FFT stability sweep

fig, axs = plt.subplots(3, 2, figsize=(14, 12))
spot = {}
for j, rid in enumerate((6, 7)):
    r = run(rid); print(summarize_run(r))
    B = r.col("magnet_field"); R = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)   # R = (V/gain_V)/(I_X/gain_I), device card
    o = np.argsort(B); B, R = B[o], R[o]
    T = r.col("T_sample"); n12 = MODEL[rid]["n"]; FL = luttinger_frequency(n12 * 1e16)
    print(f"run {rid}: n = {n12:+.1f}e12, B {B.min():.2f}-{B.max():.2f} T ({len(B)} pts), R {R.min():.0f}..{R.max():.0f} Ohm "
          f"(max {R.max()/(SENS/I_BIAS)*100:.0f} % of the 5 kOhm FS), T_sample {T.min():.3f}-{T.max():.3f} K, F_L = {FL:.1f} T")
    # (0) raw
    axs[0, j].plot(B, R, lw=0.6, color="k"); axs[0, j].set_title(f"run {rid} — raw Rxx(B), n = {n12:+.1f}e12, D = 0"); axs[0, j].set_xlabel("B (T)"); axs[0, j].set_ylabel("Rxx (Ohm)")
    # (1) onset, per tone
    try:
        on = sdh_onset(R, B, r_full_scale=SENS / I_BIAS); print(on.summary()); spot[rid] = on
    except SdhOnsetError as e:
        print(f"run {rid}: SdhOnsetError — {e}")
    # (2) bg-subtracted record vs 1/B (deg-5 in B, B > 1 T)
    m = B > 1.0; dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    axs[1, j].plot(1 / B[m], dR, lw=0.6); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dRxx (Ohm)"); axs[1, j].set_title("MR background removed (deg 5 in B, B > 1 T) vs 1/B")
    # (3) FFT stability sweep
    for (lo, deg), c in zip(WINDOWS, ("C0", "C1", "C2", "C3")):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg); s = S[0] / S[0].max()
        pk, _ = find_peaks(s, prominence=0.05); pk = sorted(pk, key=lambda k: -s[k])[:6]
        print(f"  FFT window B > {lo} T, bg deg {deg}: peaks " + ", ".join(f"{f[k]:.1f} T ({s[k]:.2f})" for k in pk))
        axs[2, j].plot(f, s, c, lw=0.9, label=f"B > {lo} T, deg {deg}")
    md = MODEL[rid]
    axs[2, j].axvline(FL, color="k", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    for F in md["abab"]: axs[2, j].axvline(F, color="tab:red", ls=":", lw=1)
    axs[2, j].axvline(md["abca"], color="tab:green", ls="-.", lw=1)
    axs[2, j].plot([], [], "tab:red", ls=":", label=f"model ABAB {md['abab'][0]} / {md['abab'][1]} T"); axs[2, j].plot([], [], "tab:green", ls="-.", label=f"model ABCA {md['abca']} T")
    axs[2, j].set_xlim(0, 2.1 * FL); axs[2, j].set_xlabel("F (T)"); axs[2, j].set_ylabel("|FFT| (norm.)"); axs[2, j].legend(fontsize=7); axs[2, j].set_title("1/B FFT — stability sweep vs window / detrender")
fig.tight_layout(); plt.show()
