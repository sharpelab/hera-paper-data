"""Fan read (partial or complete): re-form R(n, B), raw pcolormesh, per-column SdH FFT in 1/B, peak tracks F(n),
overlay ABAB / ABCA model curves under a global density scale; Luttinger sum per column."""
import sys, json
from sharpelab_nb.gates import calc_nD
sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\tetralayer_fs_count")
import fs_count_b0 as fsm

rid = 8; scale = 0.886   # global density scale pinned by the run-6 Luttinger sum (and the run-7 ladder)
cal = json.load(open(Path(file_path).parent / "hera_scratch" / "cal_run5.json"))
g = fan_grids(str(Path(file_path) / str(rid))); rg = resistance_grids(g); R = rg.R["sr1"]; B = g.slow
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0]); Vbg = np.asarray(fs[1])
n12, D = calc_nD(Vtg, Vbg, cal["c_tg"], cal["c_bg"], cal["n_offset"], cal["D_offset"])
print(f"run {rid}: {g.nrows} rows (B {B.min():.2f}-{B.max():.2f} T) x {g.nfast} n-pts (n {n12.min():.2f}-{n12.max():.2f}e12, D {D.min():+.3f}..{D.max():+.3f}); R {np.nanmin(R):.0f}..{np.nanmax(R):.0f} Ohm")
fig, ax = plt.subplots(1, 3, figsize=(18, 5.5))
m = ax[0].pcolormesh(n12, B, R, shading="nearest", cmap="RdBu_r", vmin=-np.percentile(np.abs(R), 98), vmax=np.percentile(np.abs(R), 98))
fig.colorbar(m, ax=ax[0], label="R = X/I (Ohm)"); ax[0].set_xlabel("n (1e12)"); ax[0].set_ylabel("B (T)"); ax[0].set_title(f"run {rid} raw (signed, rho_xy admixture)")
# per-column FFT
if g.nrows >= 12:
    lo, hi = B.min(), 6.0   # SdH window; above ~7 T the QH regime distorts the background fit
    f, spec = sdh_fft(R, B, b_range=(lo, hi), bg_degree=3 if g.nrows < 30 else 5, log=False, nfft=2048)
    spec = spec / spec[:, f > 2].max(axis=1, keepdims=True)
    m2 = ax[1].pcolormesh(f, n12, spec, shading="nearest", cmap="magma", vmin=0, vmax=1)
    ax[1].set_xlim(0, 60); ax[1].set_xlabel("F (T)"); ax[1].set_ylabel("n (1e12)"); ax[1].set_title(f"per-column |FFT| [{lo:.1f},{hi:.1f}] T, dF={1/(1/lo-1/hi):.1f} T")
    # model overlays: ABAB (light, heavy), ABCA singleton, trilayer for adjacent-N, vs n_true = scale * n_cal
    nn = np.linspace(max(n12.min(), 1.0), n12.max(), 25)
    FL = luttinger_frequency(scale * nn * 1e16)
    ab = np.array([[F for F, k in fsm.abab_fs(scale * x * 1e16)[1]][:2] for x in nn])
    tri = np.array([[F for F, k in fsm.bernal_fs(scale * x * 1e16, "ABA", fsm.ABA_TRI)[1]][:2] for x in nn]) if hasattr(fsm, "bernal_fs") else None
    ax[1].plot(FL, nn, "w--", lw=1, label=f"F_L x{scale}"); ax[1].plot(ab[:, 0], nn, "c-", lw=1, label="ABAB light/heavy"); ax[1].plot(ab[:, 1], nn, "c-", lw=1)
    ax[1].plot(ab.sum(axis=1), nn, "c:", lw=1, label="ABAB sum"); ax[1].plot(2 * ab[:, 0], nn, "y:", lw=0.8, label="2 x light")
    if tri is not None: ax[1].plot(tri[:, 0], nn, "g-", lw=0.8, label="trilayer ML+BL"); ax[1].plot(tri[:, 1], nn, "g-", lw=0.8)
    ax[1].legend(fontsize=7, loc="lower right")
    # peak tracks per column + Luttinger check
    print("col  n_cal  n_true   peaks(T, norm)                      sum of top two fundamentals vs F_L")
    tracks = []
    for j in range(0, g.nfast, max(1, g.nfast // 15)):
        s = spec[j]; pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.25 and 3 < f[i] < 60]
        pk = sorted(pk, key=lambda p: -p[1])[:5]
        print(f"{j:3d}  {n12[j]:.2f}  {scale*n12[j]:.2f}   " + ", ".join(f"{a:.1f}({b:.2f})" for a, b in sorted(pk)) + f"   F_L={FL[np.argmin(abs(nn-n12[j]))]:.1f}")
        tracks.append((n12[j], pk))
    ax[2].plot(nn, FL, "k--", label=f"F_L x{scale}"); ax[2].plot(nn, ab[:, 0], "c-", label="ABAB"); ax[2].plot(nn, ab[:, 1], "c-"); ax[2].plot(nn, ab.sum(axis=1), "c:", label="ABAB sum"); ax[2].plot(nn, 2 * ab[:, 0], "y:", label="2x light")
    for j in range(g.nfast):
        s = spec[j]; pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.25 and 3 < f[i] < 60]
        for a, b in pk: ax[2].plot(n12[j], a, "o", ms=3 + 4 * b, color="r", alpha=0.5)
    ax[2].set_xlabel("n_cal (1e12)"); ax[2].set_ylabel("F (T)"); ax[2].set_ylim(0, 60); ax[2].legend(fontsize=7); ax[2].set_title("measured peaks (size = strength) vs model")
fig.tight_layout(); plt.show()

# Luttinger sum per column on the three strongest tracks (light < 10 T, heavy 14-26 T, top 16-32 T) and the difference tone
print("col  n_cal  light  heavy  sum(l+h)  top-track  F_L*scale   diff(h-l)  mid-track")
for j in range(0, g.nfast, 6):
    s_ = spec[j]
    def pk_in(a, b):
        m_ = (f >= a) & (f <= b)
        return f[m_][np.argmax(s_[m_])] if (m_.sum() > 0 and s_[m_].max() > 0.2) else np.nan
    fl_ = luttinger_frequency(scale * n12[j] * 1e16)
    light = pk_in(2.5, 10); heavy = pk_in(0.6 * fl_, 0.88 * fl_); top = pk_in(0.9 * fl_, 1.12 * fl_); mid = pk_in(10.5, 0.58 * fl_)
    print(f"{j:3d}  {n12[j]:.2f}   {light:5.1f}  {heavy:5.1f}   {light+heavy:6.1f}    {top:6.1f}     {fl_:5.1f}      {heavy-light:5.1f}     {mid:5.1f}")

# Lever-arm check from the QH regime: rho_xx minima vs n along a high-B row; their spacing = Δν·(e/h)·B in true n
from scipy.signal import find_peaks
for Brow in (8.0, 9.0, 10.0):
    i = int(np.argmin(np.abs(B - Brow))); row = R[i]
    mins, _ = find_peaks(-row, prominence=0.1 * np.ptp(row)); nm = n12[mins]
    if len(nm) >= 2:
        d = np.median(np.diff(np.sort(nm))); eB_h = 2.418e10 * B[i] * 1e-12  # e/h in 1e12 cm^-2 per T
        print(f"B = {B[i]:.2f} T: minima at n_cal = {np.round(np.sort(nm), 2)}; median spacing {d:.3f}e12 -> scale = Δν·eB/h/Δn_cal = "
              + ", ".join(f"Δν={k}: {k*eB_h/d:.3f}" for k in (1, 2, 4)))
