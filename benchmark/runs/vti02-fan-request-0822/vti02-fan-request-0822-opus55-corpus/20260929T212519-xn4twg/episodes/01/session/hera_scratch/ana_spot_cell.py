# Runs 6-7 — SdH spot checks (sdh-spot-check), D = 0, region-A calibration (run 5). Raw first, then onset + windowed FFT.
# R = (sr1_X / 1) / I_drain, I_drain = sr0_X / -1e6. Run 6 is cut at B >= 0.8 T: its 50 mT grid below 1 T
# Nyquist-samples a 7.3 T tone only above ~0.8 T (dB <= B^2 / 2F).
import sys
from scipy.signal import find_peaks
from hera.analysis import sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
import fs_count_b0 as FS

spots = {6: (+3.2, 0.8), 7: (-1.2, 0.3)}       # run: (n nominal 1e12 cm^-2, analysis B floor)
windows = {6: [(0.8, 10.0), (0.8, 3.0), (3.0, 10.0)], 7: [(0.71, 10.0), (0.71, 3.0), (3.0, 10.0)]}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, (n, bfloor)) in enumerate(spots.items()):
    r = run(rid)
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]; k = B >= bfloor; B, R, I = B[k], R[k], I[k]
    FL = luttinger_frequency(abs(n) * 1e16)
    ab = FS.abab_mstar(n * 1e16); ca_F, ca_m = FS.abca_mstar(n * 1e16)
    print(f"=== run {rid}: n = {n:+.1f}e12 (nominal), D = 0 | B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts | "
          f"I {np.median(I)*1e9:.2f} nA | R {R.min():.0f}..{R.max():.0f} Ohm | T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    print(f"    F_L = {FL:.1f} T (scale 1) | model ABAB (F, m*): " + ", ".join(f"{f:.1f} T/{m:.3f}" for f, m in ab) +
          f" | ABCA {ca_F:.1f} T/{ca_m:.3f}")
    on = sdh_onset(R, B, b_lo=bfloor, r_full_scale=50e-6 / np.median(np.abs(I)))
    print(on.summary())
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw, n = {n:+.1f}e12, D = 0 (sr1 50 uV FS = 5 kOhm)")
    m = (B >= on.onset_b); bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1, j].plot(1 / B[m], R[m] - bg, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm), deg-5 bg in B")
    ax[1, j].set_title(f"bg-subtracted from onset {on.onset_b:.2f} T")
    for lo, hi in windows[rid]:
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False); s = sp[0]; mm = f > 2
        pk, _ = find_peaks(s[mm], prominence=0.1 * s[mm].max())
        top = sorted(zip(s[mm][pk], f[mm][pk]), reverse=True)[:5]
        print(f"    FFT [{lo:.2f}, {hi:.1f}] T (dF {1/(1/lo-1/hi):.2f} T): " + ", ".join(f"{ff:.1f} T ({a/s[mm].max():.2f})" for a, ff in top))
        ax[2, j].plot(f, s / s[mm].max(), lw=0.9, label=f"[{lo:.2f}, {hi:.0f}] T")
    for f_, _m in ab: ax[2, j].axvline(f_, color="g", ls="--", lw=0.8)
    ax[2, j].axvline(FL, color="r", ls=":", lw=1.2); ax[2, j].axvline(0.9 * FL, color="r", ls="-", lw=0.5, alpha=0.5)
    ax[2, j].set_xlim(0, 2.2 * FL); ax[2, j].set_ylim(0, 1.1); ax[2, j].legend(fontsize=7)
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_title("windowed FFT; green = ABAB model, red dotted = F_L (s = 1), faint = 0.9 F_L")
fig.tight_layout(); plt.show()
