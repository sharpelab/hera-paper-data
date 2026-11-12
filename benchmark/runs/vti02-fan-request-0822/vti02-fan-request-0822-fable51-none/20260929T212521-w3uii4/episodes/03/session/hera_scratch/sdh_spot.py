"""SdH spot-check read: runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12). Raw R(B), background-subtracted, FFT in 1/B, onset/tones."""
import numpy as np, json, sys, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
from scipy.constants import e, h

out = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    print(f"===== run {rid} =====\n{summarize_run(r)}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = r.col("sr1_X") / I; Rabs = np.abs(R); T = r.col("T_sample")
    o = np.argsort(B); B, R, Rabs, T = B[o], R[o], Rabs[o], T[o]
    print(f"T_sample {T.mean():.3f} K (range {T.min():.3f}-{T.max():.3f}); I {I.mean()*1e9:.3f} nA; R(B~0.3) {Rabs[np.argmin(abs(B-0.3))]:.1f} Ohm, R max {Rabs.max():.0f} at {B[np.argmax(Rabs)]:.2f} T")
    F_L = luttinger_frequency(abs(n12) * 1e16)
    print(f"F_L(n={n12:+.2f}e12, 4-fold) = {F_L:.1f} T ; F_L/2 = {F_L/2:.1f}; per Landau level filling nu=4: B(nu=4)= {F_L/1:.2f}/? ")
    # R minima positions (LL positions): local minima of smoothed Rabs above 2 T
    from scipy.signal import find_peaks, savgol_filter
    m = B > 1.5
    sm = savgol_filter(Rabs[m], 9, 2)
    mins, _ = find_peaks(-sm, prominence=0.15*(sm.max()-sm.min()))
    Bmin = B[m][mins]; print("R minima (T):", np.round(Bmin, 2), " -> 1/B:", np.round(1/Bmin, 3), " diff(1/B):", np.round(np.diff(1/Bmin[::-1]), 4))
    for nu_guess in [4, 8, 12, 16, 20]:
        pass
    # if minima at nu = F_L/B*? : implied frequency from spacing in 1/B
    if len(Bmin) >= 2:
        d = np.diff(np.sort(1/Bmin)); print(f"  median spacing 1/B = {np.median(d):.4f} T^-1 -> freq {1/np.median(d):.1f} T ; F_L/freq = {F_L/(1/np.median(d)):.2f}")
        print("  filling factor guesses at minima (F_L*4/B = nu if 4-fold full density):", np.round(F_L*4/Bmin, 1))
    # FFT
    for b_lo, b_hi in [(1.5, 10.0), (2.0, 10.0), (1.0, 5.0)]:
        try:
            fr, sp = sdh_fft(Rabs[:, None], B, b_range=(b_lo, b_hi), nfft=2048, bg_degree=5, log=False)
            sp = sp[0]; pk, _ = find_peaks(sp, prominence=0.1*sp.max())
            top = sorted(pk, key=lambda p: -sp[p])[:6]
            print(f"  FFT [{b_lo},{b_hi}] T peaks (T): " + ", ".join(f"{fr[p]:.1f}({sp[p]/sp.max():.2f})" for p in top))
        except Exception as ex: print("  fft err", ex)
    try:
        on = sdh_onset(Rabs, B, b_lo=0.5, r_full_scale=50e-6/10e-9)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), tones=[(float(t.freq), float(t.onset_b), float(t.contrast)) for t in on.tones])
    except SdhOnsetError as ex: print("  onset err:", ex)
    ax = axs[0, k]; ax.plot(B, Rabs, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("|Rxx| (Ohm)"); ax.set_title(f"run {rid}: n={n12:+.1f}e12, D=0, raw")
    for bm in Bmin: ax.axvline(bm, color="r", lw=0.4, alpha=0.5)
    ax = axs[1, k]; mm = B > 1.0; ax.plot(1/B[mm], Rabs[mm], lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("|Rxx|"); ax.set_title("vs 1/B")
    ax = axs[2, k]
    for b_lo in (1.5, 3.0):
        fr, sp = sdh_fft(Rabs[:, None], B, b_range=(b_lo, 10.0), nfft=2048, bg_degree=5, log=False); ax.plot(fr, sp[0]/sp[0].max(), lw=0.8, label=f"B {b_lo}-10 T")
    ax.axvline(F_L, color="k", ls="--", lw=0.8, label=f"F_L={F_L:.1f}"); ax.axvline(F_L/2, color="gray", ls=":", lw=0.8, label="F_L/2")
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.legend(fontsize=7); ax.set_title("SdH FFT (bg deg 5)")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_67.png", dpi=110)
json.dump(out, open("hera_scratch/sdh_spot_67.json", "w"), indent=1)
