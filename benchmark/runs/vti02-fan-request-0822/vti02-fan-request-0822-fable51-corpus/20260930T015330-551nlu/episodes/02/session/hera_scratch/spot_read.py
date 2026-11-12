"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT."""
import sys, warnings, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

DATA = Path("/home/hera/measurements/zack/20260822-vti-02/data")
OUT = Path("/home/hera/measurements/zack/20260822-vti-02/hera_scratch")
I_BIAS = 10e-9; SENS = 50e-6; RFS = SENS / I_BIAS

res = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    run = open_run(DATA / str(rid))
    print("=" * 70); print(summarize_run(run))
    B = run.col("magnet_field"); X = run.col("sr1_X"); I = run.col("sr0_X") / -1e6
    R = X / np.abs(I)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"run {rid}: n = {n12:+.2f}e12, F_L = {FL:.1f} T; R(B) range {R.min():.1f}..{R.max():.1f} Ohm; {len(B)} pts, dB med {np.median(np.diff(B))*1e3:.1f} mT")
    print(f"  Nyquist check on F_L: need dB <= {1/(2*FL)*1**2*1e3:.1f} mT at 1 T, {1/(2*FL)*2**2*1e3:.1f} mT at 2 T, {1/(2*FL)*4**2*1e3:.1f} mT at 4 T")
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx sr1 (Ohm)"); ax.set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0")
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=RFS, b_lo=0.3)
            for ww in w: print("  WARN:", ww.message)
        print(on.summary())
        onset = on.onset_b
        res[rid] = {"onset_b": float(onset), "tones": [(float(t.freq), float(t.onset_b), bool(t.censored), bool(t.marginal)) for t in on.tones]}
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); onset = None; res[rid] = {"onset_b": None, "err": str(e)}
    # background-subtracted trace vs 1/B, several windows
    ax = axs[1, j]
    for lo in ([1.5, 2.5, 4.0] if rid == 6 else [1.0, 2.0, 3.0]):
        m = B >= lo
        cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
        ax.plot(1 / B[m], dR + (lo * 15 if rid == 6 else lo * 30), lw=0.6, label=f"B>={lo} T (deg 5)")
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm, offset)"); ax.legend(fontsize=7); ax.set_title("bg-subtracted in B, plotted vs 1/B")
    # FFT for several low cuts
    ax = axs[2, j]
    Bmax = B.max()
    cuts = [1.5, 2.0, 3.0, 4.0] if rid == 6 else [1.0, 1.5, 2.0, 3.0]
    for lo in cuts:
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, Bmax), bg_degree=5, log=False, nfft=4096)
        sp = sp[0]; sel = (f > 1) & (f < 80)
        ax.plot(f[sel], sp[sel] / sp[sel].max(), lw=0.8, label=f"[{lo},{Bmax:.0f}] T, dF={1/(1/lo-1/Bmax):.1f} T")
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"  FFT window [{lo},{Bmax:.1f}] T: dF = {1/(1/lo-1/Bmax):.2f} T; top-6 bins (T): {np.round(np.sort(pk),1)}")
    for x, lab in [(FL, "F_L")]:
        ax.axvline(x, color="k", ls=":", lw=1); ax.text(x, 0.95, lab, fontsize=8)
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.legend(fontsize=7); ax.set_title(f"FFT in 1/B; F_L = {FL:.1f} T")
fig.tight_layout(); fig.savefig(OUT / "spot_read.png", dpi=110)
json.dump(res, open(OUT / "spot_read.json", "w"), indent=1)
print(json.dumps(res, indent=1))
