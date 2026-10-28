"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), both D = 0 (run-5 cal).
Raw R(B) first, then SdH: minima in 1/B, per-trace FFT (sdh_fft), onset (sdh_onset), Onsager density vs nominal."""
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError

def load_spot(rid):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("T_sample")[o]

fig, ax = plt.subplots(3, 2, figsize=(14, 12))
for k, (rid, n_nom) in enumerate([(6, 3.2), (7, -1.2)]):
    r, B, R, I, T = load_spot(rid)
    Ra = np.abs(R)
    print(f"\n=== run {rid}: rows {r.rows}, B {B.min():.3f}-{B.max():.3f} T, T {T.mean():.3f}+-{T.std():.3f} K, "
          f"I_drain {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, |R| {Ra.min():.1f}..{Ra.max():.0f} Ohm, interrupted={r.interrupted}")
    ax[0, k].plot(B, Ra, "-", lw=0.8); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("|Rxx| (Ohm)")
    ax[0, k].set_title(f"run {rid}: raw |Rxx|(B), n_nom = {n_nom:+.1f}e12, D = 0")
    m = B > 1.2
    Rs = savgol_filter(Ra[m], 7, 2)
    mins, _ = find_peaks(-Rs, prominence=8, distance=5)
    Bm = B[m][mins]
    print("Rxx minima (B>1.2 T, prom>8 Ohm): " + ", ".join(f"{b:.2f}" for b in Bm))
    ax[0, k].plot(Bm, Ra[m][mins], "rv", ms=5)
    nhe = abs(n_nom) * 1e16 * cst.h / cst.e
    ax[1, k].plot(1 / B[m], Ra[m], "-", lw=0.8); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("|Rxx| (Ohm)")
    for nu in range(1, 40):
        x = nu / nhe
        if x < (1 / B[m]).max():
            ax[1, k].axvline(x, color="gray", lw=0.4, ls=":")
            if nu % 4 == 0: ax[1, k].text(x, Ra[m].max() * 0.95, str(nu), fontsize=6, ha="center")
    ax[1, k].set_title(f"|Rxx| vs 1/B; dotted = integer nu for n_nom (nh/e = {nhe:.1f} T)")
    f, spec = sdh_fft(Ra[:, None], B, b_range=(1.5, 10.0), nfft=2048, bg_degree=4, log=False)
    spec = spec[0]; sel = f > 2
    pk, _ = find_peaks(spec[sel], prominence=0.1 * spec[sel].max())
    top = sorted(zip(spec[sel][pk], f[sel][pk]), reverse=True)[:6]
    print("FFT [1.5,10] T peaks: " + ", ".join(f"{ff:.1f} T ({a/top[0][0]:.2f}) -> n4 {4*ff*cst.e/cst.h*1e-16:.2f}e12" for a, ff in top))
    ax[2, k].plot(f, spec / spec[sel].max(), lw=0.9); ax[2, k].set_xlim(0, 80); ax[2, k].set_xlabel("F (T)"); ax[2, k].set_ylabel("FFT amp (norm)")
    for lab, F in [("nh/4e", nhe / 4), ("nh/e", nhe)]:
        ax[2, k].axvline(F, color="r", ls="--", lw=0.8); ax[2, k].text(F, 0.9, lab, color="r", fontsize=7)
    ax[2, k].set_title(f"SdH FFT, B in [1.5, 10] T (deg-4 bg); nominal F_L = {nhe/4:.1f} T")
    try:
        on = sdh_onset(Ra, B, b_lo=1.0, r_full_scale=5e3); print(on.summary())
    except SdhOnsetError as e:
        print(f"onset: {e}")
fig.tight_layout(); plt.show()
