"""sdh-spot-check step 6 read for runs 6 (electron +3.2e12) and 7 (hole -1.2e12): onset (sdh_onset), background-subtracted
dRxx(1/B), FFT stability sweep (bg degree x window) and B-window split, peak set vs F_L; model F(n) table (fs_count_b0) for the
spot densities and the fan window."""
import warnings, importlib.util
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, SdhOnsetError
import hera
warnings.simplefilter("ignore")
FL = lambda n: abs(n) * 1e16 * cst.h / (4 * cst.e)   # n in 1e12 cm^-2 -> T

def trace(rid):
    r = run(rid); B = r.col("magnet_field"); X = r.col("sr1_X")
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]; I = amp / r.meta["measurement_config"]["bias_resistor"]
    o = np.argsort(B); return B[o], (X / I)[o], I

peaks = {}
for rid, n, blo in ((6, 3.2, 1.0), (7, -1.2, 0.3)):
    B, R, I = trace(rid)
    print(f"\n===== run {rid}: n = {n:+.2f}e12, F_L = {FL(n):.1f} T; I_bias {I*1e9:.1f} nA; R {R.min():.0f}..{R.max():.0f} Ohm (|R|max = {abs(R).max()/(50e-6/I):.2f} FS)")
    for bl in sorted({blo, 1.0}):
        try:
            on = sdh_onset(R[B >= bl], B[B >= bl], r_full_scale=50e-6 / I)
            print(f"-- sdh_onset, record B >= {bl} T: onset_b = {on.onset_b:.2f} T (tone {on.onset_freq:.1f} T)")
            for t in on.tones:
                fl = [f for f, v in (("censored", t.censored), ("revived", t.revived), ("marginal", t.marginal), ("near-residual", t.near_residual)) if v]
                print(f"     {t.freq:5.1f} T  onset {t.onset_b:.2f} T  snr_max {t.snr.max():5.1f}  harmonic_of {t.harmonic_of if t.harmonic_of is None else round(t.harmonic_of,1)}  {fl}")
        except SdhOnsetError as e:
            print("   SdhOnsetError:", str(e)[:200])
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.2))
    sel = B >= max(blo, 1.0); cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    ax[0].plot(1 / B[sel], dR, lw=0.7); ax[0].set_xlabel("1/B (1/T)"); ax[0].set_ylabel("dRxx (Ohm), deg-5 bg in B"); ax[0].set_title(f"run {rid}: dRxx vs 1/B, B >= {max(blo,1.0)} T")
    for bg, ls in ((3, ":"), (5, "-"), (7, "--")):
        for (lo, hi), col in (((1.0, 10.0), "C0"), ((1.5, 10.0), "C1"), ((2.5, 10.0), "C2"), ((1.0, 5.0), "C3")):
            if lo < blo: continue
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=bg, log=False, nfft=4096)
            ax[1].plot(f, sp[0] / sp[0][f > 2].max(), ls, color=col, lw=0.8, label=f"bg{bg} [{lo},{hi}]" if bg == 5 else None)
    ax[1].set_xlim(0, 70); ax[1].axvline(FL(n), color="k", ls="--", lw=1); ax[1].text(FL(n), 1.0, " F_L", va="top")
    ax[1].set_xlabel("F (T)"); ax[1].set_ylabel("|FFT| (norm to max above 2 T)"); ax[1].legend(fontsize=7); ax[1].set_title("stability: bg degree x window")
    # B-window split (Verify: F_L-tone origin) + reference peak table
    rows = []
    for (lo, hi), col in (((1.5, 10.0), "k"), ((1.5, 4.0), "C0"), ((4.0, 10.0), "C3")):
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5 if hi - lo > 5 else 4, log=False, nfft=4096); s = sp[0]
        pk, _ = find_peaks(s, prominence=0.05 * s[f > 2].max()); pk = sorted([p for p in pk if f[p] > 1.5], key=lambda p: -s[p])[:8]
        ax[2].plot(f, s / s[pk[0]] if pk else s, color=col, lw=0.9, label=f"[{lo},{hi}] T, dF {1/(1/lo-1/hi):.1f} T")
        tbl = ", ".join(f"{f[p]:.1f} ({s[p]/s[pk[0]]:.2f}, {f[p]/FL(n):.2f} F_L)" for p in sorted(pk, key=lambda p: f[p]))
        print(f"-- FFT peaks [{lo},{hi}] T (F, rel amp, F/F_L): {tbl}")
        rows.append(((lo, hi), [(f[p], s[p] / s[pk[0]]) for p in sorted(pk, key=lambda p: f[p])]))
    ax[2].set_xlim(0, 70); ax[2].axvline(FL(n), color="k", ls="--", lw=1); ax[2].set_xlabel("F (T)"); ax[2].legend(fontsize=7); ax[2].set_title(f"B-window split vs F_L = {FL(n):.1f} T")
    fig.tight_layout(); plt.show(); peaks[rid] = rows

# Model F(n) (fs_count_b0: n in SI m^-2) at the spot densities and across the electron-side fan window
p = Path(hera.__file__).parent / "models" / "tetralayer_fs_count" / "fs_count_b0.py"
spec = importlib.util.spec_from_file_location("fs_count_b0", p); fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
print("\nmodel F(n): n(e12)  F_L | ABAB orbits F [m*/me] (fraction of F_L) | ABCA F, topology, m*")
for n in (-1.2, 1.0, 1.5, 2.0, 2.5, 3.0, 3.2, 3.24):
    EF, orbs = fs.abab_fs(n * 1e16); ms = fs.abab_mstar(n * 1e16)
    _, topo, ncomp, nfreq, Ft = fs.abca_fs(n * 1e16); _, m2 = fs.abca_mstar(n * 1e16)
    print(f"  {n:+5.2f}  {FL(n):5.1f} | " + ", ".join(f"{F:5.1f} [{m:.3f}] ({F/FL(n):.2f})" for (F, k), (_, m) in zip(orbs, ms)) + f" | {Ft:5.1f} T {topo} m* {m2:.3f}")
