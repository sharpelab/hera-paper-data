# Runs 6-7 — sdh-spot-check at D = 0 (region-A cal, run 5). Raw first, then FFT in 1/B (log R, B-space bg5).
import warnings
from scipy.signal import find_peaks
from hera.analysis import resolve_channels, sdh_onset

def rxx_vs_B(rid):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1)                                   # planned setpoint column
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
    o = np.argsort(B)
    return r, B[o], R[o]

h_over_4e = cst.h / (4 * cst.e)
fig, ax = plt.subplots(2, 2, figsize=(12, 7.5))
for k, (rid, n12) in enumerate([(6, +3.2), (7, -1.2)]):
    r, B, R = rxx_vs_B(rid)
    FL = abs(n12) * 1e16 * h_over_4e
    print(f"run {rid}: n = {n12:+.1f}e12 (run-5 cal), {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"R {R.min():.1f}-{R.max():.1f} Ohm, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, "
          f"I_tg {r.col('k_2400_tg_curr').min()*1e12:+.0f}..{r.col('k_2400_tg_curr').max()*1e12:+.0f} pA; F_L(prior scale) = {FL:.1f} T")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, k].set_title(f"run {rid} raw — n = {n12:+.1f}e12, D = 0")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 1e-8)
    print(on.summary())
    for br, c in [((1.5, 10.0), "C0"), ((2.0, 10.0), "C1")]:
        f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=4096, bg_degree=5); sp = sp[0]
        m = (f > 2) & (f < 70); ff, ss = f[m], sp[m]
        p, _ = find_peaks(ss, prominence=0.1 * ss.max())
        print(f"  FFT {br} T: peaks " + ", ".join(f"{ff[i]:.1f} T ({ss[i]/ss.max():.2f})" for i in p[np.argsort(-ss[p])][:6]))
        ax[1, k].plot(ff, ss / ss.max(), c, lw=0.8, label=f"B {br[0]}-{br[1]} T")
    ax[1, k].axvline(FL, color="k", ls=":", lw=1, label=f"F_L prior {FL:.1f} T")
    ax[1, k].set_xlabel("F (T)"); ax[1, k].set_ylabel("norm. |FFT|"); ax[1, k].legend(fontsize=8)
fig.suptitle("vti-02 SdH spot checks, D = 0: run 6 (e, +3.2e12, 0->10 T) and run 7 (h, -1.2e12, 10->0.3 T)")
fig.tight_layout(); plt.show()
