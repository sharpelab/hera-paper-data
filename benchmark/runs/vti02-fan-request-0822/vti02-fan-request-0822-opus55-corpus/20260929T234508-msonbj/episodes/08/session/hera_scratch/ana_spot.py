"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT vs model F(n)."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fs

D = Path(__file__).resolve().parents[1] / "data"
spots = {6: +3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n) in enumerate(spots.items()):
    r = open_run(D / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = V / I
    Rabs = np.abs(R)
    o = np.argsort(B); B, R, Rabs, I = B[o], R[o], Rabs[o], I[o]
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    FL = float(luttinger_frequency(abs(n) * 1e16))
    print(f"\n=== run {rid}: n = {n:+.1f}e12, F_L = {FL:.2f} T; {len(B)} pts, B {B.min():.3f}-{B.max():.3f} T; "
          f"I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.1f}..{R.max():.1f} Ohm; "
          f"T {T.min():.3f}-{T.max():.3f} K; I_tg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA, I_bg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA; "
          f"sr1 |X| max {np.abs(V).max()*1e6:.2f} uV of 50 uV FS")
    print(f"R at B=0.3,1,3,6,9: " + ", ".join(f"{np.interp(b, B, R):.0f}" for b in (0.3, 1, 3, 6, 9)))
    # model
    try:
        Ef, orbs = fs.abab_fs(n * 1e16); ms = fs.abab_mstar(n * 1e16)
        print("  ABAB model:", [(round(f, 2), round(m, 3)) for (f, _), (_, m) in zip(orbs, ms)])
    except Exception as e:
        print("  ABAB model err", e)
    try:
        print("  ABCA model F, m*:", [round(x, 3) for x in fs.abca_mstar(n * 1e16)])
    except Exception as e:
        print("  ABCA model err", e)
    rfs = 50e-6 / 10e-9
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(on.summary())
        b_on = on.onset_b
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); on = None; b_on = None
    a = ax[0, j]; a.plot(B, R, "-", lw=0.7); a.set_xlabel("B (T)"); a.set_ylabel("Rxx (Ohm)")
    a.set_title(f"run {rid} raw, n = {n:+.1f}e12, D = 0")
    if b_on: a.axvline(b_on, color="r", ls="--", lw=0.8)
    # background-subtracted in B (poly deg 5 over window) for view
    lo = b_on if b_on else 1.5
    m = B >= lo
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm)")
    ax[1, j].set_title(f"bg-sub (poly5 in B, B>{lo:.2f} T) vs 1/B")
    for cut in sorted({round(lo, 2), 2.0, 3.0, 4.0}):
        if cut >= B.max() - 1: continue
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False)
            ax[2, j].plot(f, sp[0] / sp[0][f > 2].max(), lw=0.8, label=f"{cut:.2f}-{B.max():.1f} T")
            s = sp[0]; k = (f > 2) & (f < 3 * FL)
            idx = np.argsort(s[k])[::-1]
            ff = f[k]; ss = s[k]
            # local maxima
            from scipy.signal import find_peaks
            pk, _ = find_peaks(ss, prominence=0.08 * ss.max())
            pk = pk[np.argsort(ss[pk])[::-1]][:6]
            print(f"  FFT {cut:.2f}-{B.max():.1f} T: dF={1/(1/cut-1/B.max()):.2f} T; peaks " +
                  ", ".join(f"{ff[p]:.1f}T({ss[p]/ss.max():.2f})" for p in pk))
        except Exception as e:
            print("  fft err", cut, e)
    ax[2, j].axvline(FL, color="k", ls=":", label="F_L")
    try:
        for (fo, _) in orbs: ax[2, j].axvline(fo, color="C3", ls="--", lw=0.7)
    except Exception: pass
    ax[2, j].set_xlim(0, 2.5 * FL); ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel("F (T)")
    ax[2, j].set_title("FFT (norm) — dotted F_L, red dashed ABAB model")
fig.tight_layout(); fig.savefig(Path(__file__).with_name("spot_runs67.png"), dpi=90)
