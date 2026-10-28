"""First-pass read of the two SdH spot checks (runs 6 electron, 7 hole): raw R(B), sdh_onset, sdh_fft."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

here = Path(__file__).resolve().parent.parent
out = {}
for rid, n12 in [(6, 3.2), (7, -1.2)]:
    r = open_run(here / "data" / str(rid))
    print(f"\n######## run {rid}")
    print(summarize_run(r))
    print("cols:", r.cols)
    mc = r.meta.get("measurement_config", {})
    ib = None
    try:
        amp = None
        for k in ("instruments", "instrument"):
            if k in r.meta:
                ins = r.meta[k]
                sr1 = ins.get("sr1", {}) if isinstance(ins, dict) else {}
                amp = sr1.get("amplitude") or (sr1.get("parameters", {}) or {}).get("amplitude", {}).get("value")
        print("sr1 amplitude snapshot:", amp)
    except Exception as e:
        print("snapshot read failed", e)
    I_bias = 1.0 / mc.get("bias_resistor", 100e6)  # 1 V drive -> 10 nA
    B = r.col("magnet_field")
    X = r.col("sr1_X")
    R = X / I_bias
    T = r.col("T_sample") if "T_sample" in r.cols else None
    order = np.argsort(B)
    B, R = B[order], R[order]
    if T is not None:
        T = T[order]
        print(f"T_sample {np.nanmin(T):.3f}-{np.nanmax(T):.3f} K")
    print(f"B {B.min():.3f}-{B.max():.3f} T, {len(B)} pts; R {R.min():.1f}..{R.max():.1f} Ohm; R(B<0.1)={np.median(R[B<0.3]) if (B<0.3).any() else R[0]:.1f}")
    FL = luttinger_frequency(abs(n12) * 1e16) if luttinger_frequency.__code__.co_argcount else None
    print("F_L =", FL)
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / I_bias, b_lo=max(0.3, B.min()))
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), clip_high_b=float(on.clip_high_b) if on.clip_high_b is not None else None,
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=t.harmonic_of) for t in on.tones])
        b_lo_fft = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        out[rid] = dict(error=str(e))
        b_lo_fft = 2.0
    # FFT over a few windows for stability
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.2))
    ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx sr1 (Ohm)"); ax[0].set_title(f"run {rid} raw, n={n12:+.1f}e12")
    for lo, deg, c in [(b_lo_fft, 5, "C0"), (max(b_lo_fft, 2.0), 5, "C1"), (max(b_lo_fft, 3.0), 3, "C2"), (max(b_lo_fft,1.5), 7, "C3")]:
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, log=False, nfft=2048)
            sp = spec[0]
            ax[2].plot(f, sp / sp[f > 3].max(), c, lw=0.8, label=f"B>{lo:.2f}, deg {deg}")
            m = (f > 3) & (f < 80)
            from scipy.signal import find_peaks
            pk, pr = find_peaks(sp[m], prominence=0.08 * sp[m].max())
            print(f"FFT window B>{lo:.2f} T deg{deg}: peaks at F =", ", ".join(f"{f[m][p]:.1f}T({sp[m][p]/sp[m].max():.2f})" for p in pk[np.argsort(-pr['prominences'])][:8]))
        except Exception as e:
            print("fft failed", lo, deg, e)
    # background-subtracted trace vs 1/B
    sel = B >= b_lo_fft
    cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    ax[1].plot(1 / B[sel], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dR (Ohm)"); ax[1].set_title(f"bg-subtracted, B>{b_lo_fft:.2f}")
    if FL:
        ax[2].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L={FL:.1f} T")
    ax[2].set_xlim(0, 80); ax[2].set_xlabel("F (T)"); ax[2].legend(fontsize=7); ax[2].set_title("FFT in 1/B")
    fig.tight_layout(); fig.savefig(here / "hera_scratch" / f"spot_run{rid}.png", dpi=110)
json.dump(out, open(here / "hera_scratch" / "spot_read.json", "w"), indent=1)
print(json.dumps(out, indent=1))
