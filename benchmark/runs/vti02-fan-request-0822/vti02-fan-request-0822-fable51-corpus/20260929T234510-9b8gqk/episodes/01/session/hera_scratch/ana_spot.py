"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D = 0.
Raw R(B) first, then sdh_onset + sdh_fft vs F_L. Scratch — promote to ana when clean."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

DATA = Path("/home/hera/measurements/zack/20260822-vti-02/data")
OUT = Path("/home/hera/measurements/zack/20260822-vti-02/hera_scratch")
SENS = 50e-6; IB = 10e-9; RFS = SENS / IB

def load(rid):
    r = open_run(DATA / str(rid))
    B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); return r, B[o], R[o], r.col("T_sample")[o], I[o]

res = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r, B, R, T, I = load(rid)
    print("=" * 70); print(summarize_run(r))
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.2f}e12 -> F_L = {FL:.2f} T; R range {R.min():.1f}..{R.max():.1f} Ohm (FS {RFS:.0f}); "
          f"T {T.min():.3f}-{T.max():.3f} K; I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R(B~0.3) = {R[np.argmin(abs(B-0.3))]:.1f}")
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw Rxx(B), n={n12:+.1f}e12, D=0")
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=RFS)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        res[rid] = dict(onset_b=float(on.onset_b), clip_high_b=(None if on.clip_high_b is None else float(on.clip_high_b)),
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=(None if t.harmonic_of is None else float(t.harmonic_of))) for t in on.tones])
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); res[rid] = dict(error=str(e)); onset_b = None
    # background-subtracted trace + FFT at a few cutoffs
    ax = axs[1, j]
    for cut in ([1.5, 2.5, 4.0] if rid == 6 else [1.5, 3.0, 5.0]):
        m = B >= cut
        if m.sum() < 30: continue
        p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
        if cut == ([1.5, 2.5, 4.0] if rid == 6 else [1.5, 3.0, 5.0])[0]:
            ax.plot(1 / B[m], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg removed"); ax.set_title(f"run {rid} dRxx vs 1/B (B>{cut})")
        f, sp = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False, nfft=2048)
        axs[2, j].plot(f, sp[0] / sp[0].max(), lw=0.8, label=f"B > {cut} T")
    for k in (1, 2, 3):
        axs[2, j].axvline(k * FL, color="k", ls=":" if k > 1 else "--", lw=0.8)
    axs[2, j].set_xlim(0, 3.2 * FL); axs[2, j].set_xlabel("F (T)"); axs[2, j].set_ylabel("|FFT| (norm)"); axs[2, j].legend(fontsize=7)
    axs[2, j].set_title(f"run {rid} FFT in 1/B; F_L = {FL:.1f} T (dashed), 2F_L, 3F_L dotted")
    res[rid]["F_L"] = FL; res[rid]["n12"] = n12
fig.tight_layout(); fig.savefig(OUT / "spot_checks_6_7.png", dpi=110)
json.dump(res, open(OUT / "spot_checks_6_7.json", "w"), indent=1)
print(json.dumps(res, indent=1))
