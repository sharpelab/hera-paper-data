# Runs 6-7 — sdh-spot-check (electron n=+3.2e12, hole n=-1.2e12; D = 0, run-5 cal). Raw first, then onset + FFT vs model.
import sys, warnings
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError
from scipy.signal import find_peaks
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
import fs_count_b0 as FSM

SPOT = {6: +3.2, 7: -1.2}                       # 1e12 cm^-2, D = 0
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, rid in enumerate((6, 7)):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B); B, R = B[o], R[o]
    n = SPOT[rid]; FL = float(luttinger_frequency(n * 1e16))
    abab = [F for F, _ in FSM.abab_fs(n * 1e16)[1]]; Fa, ma = FSM.abca_mstar(n * 1e16)
    print(f"run {rid}: n = {n:+.1f}e12, F_L = {FL:.2f} T | model ABAB {', '.join(f'{F:.2f}' for F in abab)} T | ABCA {Fa:.2f} T (m* {ma:.3f}) | "
          f"R {R.min():.0f}..{R.max():.0f} Ohm, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, I_tg max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw — n = {n:+.1f}e12, D = 0")
    # run 6 below 1 T is 50 mT-stepped: undersampled for a 7 T tone below ~0.86 T -> onset on the 10 mT segment only
    m = B >= (0.995 if rid == 6 else 0.29)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R[m], B[m], b_lo=float(B[m].min()), r_full_scale=50e-6 / np.median(np.abs(I)))
    print(on.summary())
    for ww in w: print("  warn:", str(ww.message)[:160])
    ax[0, j].axvline(on.onset_b, color="r", ls="--", lw=0.8, label=f"onset_b {on.onset_b:.2f} T"); ax[0, j].legend()
    for lo in (on.onset_b, 1.3 * on.onset_b):
        fq, sp = sdh_fft(R[m][:, None], B[m], b_range=(lo, B.max()), bg_degree=5, nfft=4096)
        s = sp[0]; k = fq > 2; s = s / s[k].max()
        pk, _ = find_peaks(np.where(k, s, 0), prominence=0.08)
        print(f"  FFT [{lo:.2f}, {B.max():.1f}] T peaks: " + ", ".join(f"{fq[p]:.1f}({s[p]:.2f})" for p in pk[:8]))
        ax[1, j].plot(fq[k], s[k], lw=0.8, label=f"window [{lo:.2f}, {B.max():.0f}] T")
    ax[1, j].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f} T")
    for F in abab:
        if F > 1: ax[1, j].axvline(F, color="b", ls=":", lw=1.2)
    ax[1, j].plot([], [], "b:", label="ABAB model"); ax[1, j].set_xlim(0, 2.2 * FL)
    ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm.)"); ax[1, j].legend(fontsize=7)
fig.suptitle("vti-02 SdH spot checks (runs 6, 7): raw Rxx(B) and 1/B FFT (bg deg 5 in B) vs F_L and the ABAB model")
fig.tight_layout(); plt.show()
