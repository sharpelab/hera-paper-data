# Runs 6-7 — SdH spot checks (`sdh-spot-check`), D = 0 (run-5 cal). Raw MR first, then onset + FFT vs F_L and the model.
import sys
from scipy.signal import find_peaks
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
import fs_count_b0 as fsm

spots = {6: (+3.2, 1.0), 7: (-1.2, 0.3)}   # rid: (n [1e12 cm^-2], b_lo = low edge of the Nyquist-adequate record)
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, (n, blo)) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n) * 1e16))
    _, orbs = fsm.abab_fs(n * 1e16); Fab = [f for f, _ in orbs]
    print(f"=== run {rid}: n = {n:+.1f}e12, D = 0; F_L = {FL:.1f} T; model ABAB {', '.join(f'{f:.1f}' for f in Fab)} T, ABCA {FL:.1f} T; "
          f"B {B.min():.2f}-{B.max():.2f} T, R {R.min():.0f}..{R.max():.0f} Ohm, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw — n = {n:+.1f}e12, D = 0"); ax[0, j].axvline(blo, color="grey", ls=":", lw=0.8)
    try:
        on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6 / 10e-9); print(on.summary())
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None
    m = B >= max(blo, 1.0); cf = np.polyfit(B[m], R[m], 5)
    ax[1, j].plot(1 / B[m], R[m] - np.polyval(cf, B[m]), lw=0.6)
    ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("ΔRxx (Ohm)"); ax[1, j].set_title(f"poly-5-in-B background removed, B ≥ {max(blo, 1.0):.1f} T")
    for w in ((max(blo, 1.0), 8.0), (max(blo, 1.0), 10.0), (2.0, 10.0)):
        f, sp = sdh_fft(R[:, None], B, b_range=w, bg_degree=5, log=False, nfft=4096)
        s = sp[0]; k = (f > 2.5) & (f < 1.4 * FL); ff, ss = f[k], s[k]
        pk, _ = find_peaks(ss, prominence=0.1 * ss.max()); pk = sorted(pk[np.argsort(ss[pk])[::-1]][:6])
        print(f"  FFT {w[0]:.1f}-{w[1]:.0f} T (δF {1/(1/w[0]-1/w[1]):.2f} T): peaks " + ", ".join(f"{ff[p]:.1f} ({ss[p]/ss.max():.2f})" for p in pk))
        ax[2, j].plot(ff, ss / ss.max(), lw=0.8, label=f"{w[0]:.1f}-{w[1]:.0f} T")
    ax[2, j].axvline(FL, color="k", ls=":", label="F_L (ABCA)")
    for fa in Fab: ax[2, j].axvline(fa, color="C3", ls="--", lw=0.8)
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("|FFT| (norm)"); ax[2, j].legend(fontsize=7)
    ax[2, j].set_title("FFT in 1/B — dotted F_L, red dashed ABAB model (scale 1)")
fig.suptitle("vti-02 SdH spot checks at D = 0: run 6 electron n = +3.2e12, run 7 hole n = -1.2e12 (T ≈ 1.2-1.3 K)")
fig.tight_layout(); plt.show()
