"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), both D = 0 (run-5 cal).
Raw R(B) first, then SdH: minima positions in 1/B, per-trace FFT (hera.analysis.sdh_fft), onset (sdh_onset),
Onsager density n_SdH = 4 F e/h vs the nominal density -> absolute lever-arm check of the geometry-prior c_tg."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError

def load(rid):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("T_sample")[o]

out = {}
fig, ax = plt.subplots(3, 2, figsize=(14, 12))
for k, (rid, n_nom) in enumerate([(6, 3.2), (7, -1.2)]):
    r, B, R, I, T = load(rid)
    Ra = np.abs(R)
    sign = np.sign(np.median(R))
    print(f"\n=== run {rid}: {r.tags[0][:60]} ... rows {r.rows}, B {B.min():.3f}-{B.max():.3f} T, T {T.mean():.3f}+-{T.std():.3f} K, "
          f"I_drain {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, R sign {sign:+.0f}, |R| {Ra.min():.1f}..{Ra.max():.0f} Ohm, R(Bmin) {Ra[0]:.1f}")
    ax[0, k].plot(B, Ra, "-", lw=0.8); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("|Rxx| (Ohm)")
    ax[0, k].set_title(f"run {rid}: raw |Rxx|(B), n_nom = {n_nom:+.1f}e12, D = 0")
    # minima (Rxx -> QH minima) above 1.5 T, on a lightly smoothed trace
    m = B > 1.2
    Rs = savgol_filter(Ra[m], 7, 2)
    mins, _ = find_peaks(-Rs, prominence=8, distance=5)
    Bm = B[m][mins]; invB = 1 / Bm
    print(f"Rxx minima (B>1.2 T, prom>8 Ohm): " + ", ".join(f"{b:.2f}" for b in Bm))
    if len(Bm) > 2:
        d = np.diff(np.sort(invB))
        print(f"  1/B spacings: " + ", ".join(f"{x:.4f}" for x in d) + f"  -> median {np.median(d):.4f} T^-1 => F = {1/np.median(d):.1f} T")
    ax[0, k].plot(Bm, Ra[m][mins], "rv", ms=5)
    # Rxx vs 1/B with nominal filling-factor ticks
    nhe = abs(n_nom) * 1e16 * cst.h / cst.e   # Tesla: nu = nhe / B
    ax[1, k].plot(1 / B[m], Ra[m], "-", lw=0.8); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("|Rxx| (Ohm)")
    for nu in range(1, 40):
        x = nu / nhe
        if x < (1 / B[m]).max():
            ax[1, k].axvline(x, color="gray", lw=0.4, ls=":")
            if nu % 4 == 0: ax[1, k].text(x, Ra[m].max() * 0.95, str(nu), fontsize=6, ha="center")
    ax[1, k].set_title(f"|Rxx| vs 1/B; dotted = integer nu for n_nom (nh/e = {nhe:.1f} T)")
    # FFT in 1/B over the oscillatory window
    res = {}
    for lo, hi in [(1.5, 10.0), (2.0, 6.0), (3.0, 10.0)]:
        try:
            f, spec = sdh_fft(Ra[:, None], B, b_range=(lo, hi), nfft=2048, bg_degree=4, log=False)
            spec = spec[0]; sel = f > 2
            pk, _ = find_peaks(spec[sel], prominence=0.1 * spec[sel].max())
            top = sorted(zip(spec[sel][pk], f[sel][pk]), reverse=True)[:6]
            print(f"  FFT [{lo},{hi}] T: peaks (F [T], rel amp): " + ", ".join(f"{ff:.1f} ({a/top[0][0]:.2f})" for a, ff in top))
            res[(lo, hi)] = (f, spec, top)
        except Exception as e:
            print(f"  FFT [{lo},{hi}] failed: {e}")
    if res:
        (lo, hi), (f, spec, top) = list(res.items())[0]
        ax[2, k].plot(f, spec / spec[f > 2].max(), lw=0.9)
        ax[2, k].set_xlim(0, 80); ax[2, k].set_xlabel("F (T)"); ax[2, k].set_ylabel("FFT amp (norm)")
        F_L = nhe / 4
        for lab, F in [("nh/4e", F_L), ("nh/e", nhe)]:
            ax[2, k].axvline(F, color="r", ls="--", lw=0.8); ax[2, k].text(F, 0.9, lab, color="r", fontsize=7)
        ax[2, k].set_title(f"SdH FFT, B in [{lo},{hi}] T (deg-4 bg); nominal F_L = {F_L:.1f} T, nh/e = {nhe:.1f} T")
        for a, ff in top:
            n_4 = 4 * ff * cst.e / cst.h * 1e-16
            print(f"    F = {ff:5.1f} T -> n(4-fold) = {n_4:.2f}e12 ({n_4/abs(n_nom)*100:.0f}% of nominal), n(full nh/e) = {n_4/4:.2f}e12")
    # onset
    try:
        on = sdh_onset(Ra, B, b_lo=1.0, r_full_scale=5e3)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), onset_freq=float(on.onset_freq),
                        tones=[(float(t.freq), float(t.contrast), float(t.onset_b)) for t in on.tones])
    except SdhOnsetError as e:
        print(f"  onset: {e}")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_runs67.png", dpi=110)
json.dump(out, open("hera_scratch/sdh_spot_runs67.json", "w"), indent=1, default=str)
print("saved hera_scratch/sdh_spot_runs67.png")
