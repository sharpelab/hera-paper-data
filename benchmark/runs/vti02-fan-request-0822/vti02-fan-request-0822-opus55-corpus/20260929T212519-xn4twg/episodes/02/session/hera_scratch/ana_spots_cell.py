"""Runs 6 (electron, n = +3.2e12) + 7 (hole, n = -1.2e12): sdh-spot-check read — raw R(B), onset, FFT vs model, B-window split."""
import sys, warnings
from scipy.signal import find_peaks
from hera.analysis import sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M
# run 6 is 50 mT-stepped below 1 T (Nyquist 2.5 T at 0.5 T) -> analysis floor 1.0 T; run 7 is 20 mT uniform -> floor 0.5 T
spots = {6: dict(n12=+3.2, b_lo=1.0), 7: dict(n12=-1.2, b_lo=0.5)}
fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for j, (rid, sp) in enumerate(spots.items()):
    r_ = run(rid); B = r_.col("magnet_field"); R = r_.col("sr1_X") / (r_.col("sr0_X") / -1e6)   # device card: sr1 gain 1, sr0 gain -1e6
    o = np.argsort(B); B, R = B[o], R[o]
    n_si = sp["n12"] * 1e16; FL = float(luttinger_frequency(n_si))
    abm = M.abab_mstar(n_si); ac = M.abca_mstar(n_si)
    print(f"=== run {rid}: n = {sp['n12']:+.1f}e12 (D = 0), F_L = {FL:.1f} T | model ABAB (F, m*) = "
          f"{[(round(float(F),1), round(float(m),3)) for F, m in abm]}, ABCA = ({float(ac[0]):.1f}, {float(ac[1]):.3f}) | R {R.min():.0f}..{R.max():.0f} Ohm (FS 5000)")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9, b_lo=sp["b_lo"])
    print(on.summary()); [print("  note:", str(x.message)[:160]) for x in w]
    axs[0, j].plot(B, R, lw=0.7); axs[0, j].axvline(on.onset_b, color="r", ls="--", lw=0.8, label=f"onset_b {on.onset_b:.2f} T")
    axs[0, j].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw — n = {sp['n12']:+.1f}e12, D = 0"); axs[0, j].legend(fontsize=8)
    wins = [(sp["b_lo"] if rid == 7 else 1.2, 10.0), (sp["b_lo"] if rid == 7 else 1.2, 3.0), (3.0, 10.0)]
    for br in wins:
        f, s = sdh_fft(R[:, None], B, b_range=br, bg_degree=5, nfft=16384, log=False); s = s[0] / s[0].max()
        pk, _ = find_peaks(s, prominence=0.08); top = sorted([p for p in pk if f[p] > 2], key=lambda p: -s[p])[:6]
        print(f"  FFT B {br}: dF = {1/(1/br[0]-1/br[1]):.2f} T; peaks (F, rel) {sorted((round(float(f[p]),1), round(float(s[p]),2)) for p in top)}")
        axs[1, j].plot(f, s, lw=0.8, label=f"B {br[0]:.1f}-{br[1]:.0f} T")
    for F, m in abm: axs[1, j].axvline(float(F), color="g", ls=":", lw=1.2)
    axs[1, j].axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f} T (= ABCA)")
    axs[1, j].set(xlim=(0, 2.2 * FL), xlabel="F (T)", ylabel="|FFT| (norm.)", title=f"run {rid} FFT (green dotted: ABAB model, scale 1)"); axs[1, j].legend(fontsize=7)
fig.tight_layout(); plt.show()
