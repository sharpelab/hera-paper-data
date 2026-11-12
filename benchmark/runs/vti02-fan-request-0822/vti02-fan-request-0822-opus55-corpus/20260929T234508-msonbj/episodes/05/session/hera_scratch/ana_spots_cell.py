"""Runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12): sdh-spot-check read. Raw first, then onset + 1/B FFT vs F_L
and the FS-count model tones (hera/models/tetralayer_fs_count, u_D = 0). R = (sr1_X/gain)/I_bias, I_bias = 10 nA."""
import sys, warnings
from hera.analysis import resolve_channels, sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count")); import fs_count_b0 as M4
from scipy.signal import find_peaks
spots = [(6, +3.2, (1.0, 10.0), 50e-6), (7, -1.2, (1.0, 10.0), 50e-6)]
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, n, (blo, bhi), sens) in enumerate(spots):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = (r.col("sr1_X") / ch["sr1"].gain) / 10e-9
    o = np.argsort(B); B, R = B[o], R[o]
    FL = luttinger_frequency(abs(n) * 1e16)
    ab = [F for F, _ in M4.abab_fs(n * 1e16)[1]]; ca = M4.abca_fs(n * 1e16)[4]
    cb = [F for F, _ in M4.abcb_fs(n * 1e16)[1]] if n > 0 else []
    print(f"=== run {rid}: n = {n:+.1f}e12, D = 0; B {B.min():.2f}-{B.max():.2f} T ({len(B)} pts); R {R.min():.0f}..{R.max():.0f} Ohm; "
          f"T {np.nanmax(r.col('T_sample')):.3f} K max; F_L = {FL:.1f} T | model ABAB {[round(f,1) for f in ab]}, ABCA {ca:.1f}, ABCB(qual.) {[round(f,1) for f in cb]}")
    # raw
    ax[row, 0].plot(B, R, lw=0.7); ax[row, 0].set_xlabel("B (T)"); ax[row, 0].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[row, 0].set_title(f"run {rid} raw, n = {n:+.1f}e12, D = 0")
    # onset on the Nyquist-sampled record (run 6: 50 mT steps below 1 T alias a 7 T tone -> analyse >= 1 T only)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always"); on = sdh_onset(R, B, b_lo=blo, r_full_scale=sens / 10e-9)
    for x in w: print("  warn:", str(x.message)[:160])
    print(on.summary())
    for k, bcut in enumerate([blo, 2.0]):
        fr, sp = sdh_fft(R[:, None], B, b_range=(bcut, bhi), bg_degree=5, log=False); s0 = sp[0] / sp[0].max()
        a = ax[row, 1 + k]; a.plot(fr, s0, lw=1); a.set_xlim(0, 2.4 * FL); a.set_xlabel("F (T)"); a.set_title(f"run {rid} FFT, B in [{bcut}, {bhi}] T")
        a.axvline(FL, color="k", ls="--", lw=1, label="F_L")
        for f in ab: a.axvline(f, color="C1", ls=":", lw=1.2)
        a.axvline(ca, color="C2", ls="-.", lw=0.8)
        for f in cb: a.axvline(f, color="C4", ls=":", lw=0.8)
        a.plot([], [], "C1:", label="ABAB model"); a.plot([], [], "C2-.", label="ABCA model"); a.plot([], [], "C4:", label="ABCB (qual.)"); a.legend(fontsize=7)
        p, _ = find_peaks(s0, prominence=0.05); p = p[np.argsort(s0[p])[::-1]][:7]
        print(f"  FFT [{bcut},{bhi}] T: peaks F (rel amp, F/F_L): " + ", ".join(f"{fr[i]:.1f} ({s0[i]:.2f}, {fr[i]/FL:.2f})" for i in p))
fig.suptitle("sdh-spot-check runs 6 (e) / 7 (h) at D = 0 — raw, and 1/B FFT vs F_L + model tones (u_D = 0, scale 1)"); fig.tight_layout(); plt.show()
