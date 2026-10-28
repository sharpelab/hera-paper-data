"""sdh-spot-check read, runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), D = 0 (run-5 calibration).
Raw Rxx(B) first, then sdh_onset (per-tone onsets, harmonic flags) and sdh_fft in 1/B at three low-B cutoffs, against F_L and the
tetralayer forward model (hera/models/tetralayer_fs_count). Channel arithmetic: R = (sr1_X/1)/(sr0_X/-1e6)."""
import warnings
from hera.analysis import sdh_onset, sdh_fft, SdhOnsetError

SENS, IB = 50e-6, 10e-9; RFS = SENS / IB          # both spot checks: sr1 50 uV, 1 V / 100 MOhm
MODEL = {3.2: dict(abab=(7.31, 25.78), abca=33.08), -1.2: dict(abab=(5.86, 6.54), abca=12.41)}   # fs_count_b0 at u_D = 0, T

def spot(rid):
    r = run(rid); B = r.col("magnet_field"); R = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); return r, B[o], R[o], r.col("T_sample")[o]

fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r, B, R, T = spot(rid)
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"=== run {rid}: {r.tags[0][:60]}...; n = {n12:+.2f}e12 -> F_L = {FL:.2f} T; R {R.min():.0f}..{R.max():.0f} Ohm (FS {RFS:.0f}); T {T.min():.3f}-{T.max():.3f} K")
    print(f"    model: ABAB pair {MODEL[n12]['abab']} T (partition {MODEL[n12]['abab'][0]/FL:.2f}/{MODEL[n12]['abab'][1]/FL:.2f}), ABCA singleton {MODEL[n12]['abca']} T")
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw Rxx(B): n = {n12:+.1f}e12, D = 0, sr1 50 uV")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always"); on = sdh_onset(R, B, r_full_scale=RFS)
        for ww in w: print("    warn:", str(ww.message)[:160])
        print(on.summary())
    except SdhOnsetError as e:
        print("    SdhOnsetError:", e)
    cuts = [1.5, 2.5, 4.0] if rid == 6 else [1.5, 3.0, 5.0]
    m = B >= cuts[0]; p = np.polyfit(B[m], R[m], 5)
    axs[1, j].plot(1 / B[m], R[m] - np.polyval(p, B[m]), lw=0.7); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dRxx (Ohm)")
    axs[1, j].set_title(f"run {rid}: deg-5 background (in B) removed, B > {cuts[0]} T, vs 1/B")
    for cut in cuts:
        f, sp = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False, nfft=2048)
        axs[2, j].plot(f, sp[0] / sp[0].max(), lw=0.8, label=f"B > {cut} T (dF {1/(1/cut-1/B.max()):.1f} T)")
    for k in (1, 2, 3): axs[2, j].axvline(k * FL, color="k", ls="--" if k == 1 else ":", lw=0.8)
    for F in MODEL[n12]["abab"]: axs[2, j].axvline(F, color="C3", ls="-.", lw=0.8)
    axs[2, j].set_xlim(0, 3.2 * FL); axs[2, j].set_xlabel("F (T)"); axs[2, j].set_ylabel("|FFT| (norm)"); axs[2, j].legend(fontsize=7)
    axs[2, j].set_title(f"run {rid} FFT in 1/B — F_L = {FL:.1f} T dashed (2x, 3x dotted); model ABAB pair red dash-dot")
fig.tight_layout(); plt.show()
