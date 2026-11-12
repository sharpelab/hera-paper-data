"""First-pass read of the SdH spot checks (runs 6 e-side, 7 h-side): columns, R(B), onset, FFT."""
import numpy as np, json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
for rid in (6, 7):
    run = open_run(f"data/{rid}")
    print("="*80); print(summarize_run(run)); print("cols:", run.cols)
    mc = run.meta.get("measurement_config", {})
    print("meas_config keys:", list(mc.keys()))
    B = run.col("magnet_field")
    xs = [c for c in run.cols if c.startswith("sr1") and c.endswith("X")][0]
    X = run.col(xs)
    ib = None
    try:
        from hera.analysis import current_channel
        print("current_channel:", current_channel(run))
    except Exception as e: print("current_channel err", e)
    # I_bias: drive amplitude / bias resistor — try metadata instruments
    inst = run.meta.get("instruments", {})
    amp = None
    for k, v in inst.items():
        if "sr1" in k and isinstance(v, dict):
            for kk in ("amplitude", "sr1_amplitude"):
                if kk in v: amp = v[kk]
    print("sr1 amplitude from instruments:", amp, "| bias_resistor:", mc.get("bias_resistor"))
    Ib = (amp or 1.0) / mc.get("bias_resistor", 100e6)
    R = X / Ib
    order = np.argsort(B); B, R = B[order], R[order]
    print(f"B {B.min():.3f}..{B.max():.3f} ({len(B)} pts); R {R.min():.1f}..{R.max():.1f} Ohm; R(B<0.2) med {np.median(R[B<0.2]) if (B<0.2).any() else np.nan:.1f}")
    T = run.col("T_sample") if "T_sample" in run.cols else None
    if T is not None: print(f"T_sample {np.nanmin(T):.3f}..{np.nanmax(T):.3f} K")
    sens = None
    for k, v in inst.items():
        if "sr1" in k and isinstance(v, dict) and "sensitivity" in v: sens = v["sensitivity"]
    print("sr1 sensitivity:", sens)
    try:
        on = sdh_onset(R, B, r_full_scale=(sens / Ib) if sens else None)
        print(on.summary())
        cut = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); cut = None
    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    ax[0,0].plot(B, R, lw=0.7); ax[0,0].set_xlabel("B (T)"); ax[0,0].set_ylabel("Rxx (Ohm)"); ax[0,0].set_title(f"run {rid} raw R(B)")
    for j, (lo, deg) in enumerate([((cut or 1.5), 5), (max((cut or 1.5), 3.0), 5), ((cut or 1.5), 3)]):
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg)
            spec = spec[0]
            ax[1,0].plot(f, spec / spec[f > 2].max() if (f>2).any() else spec, lw=0.8, label=f"cut {lo:.2f} T, deg {deg}")
            pk = f[(f > 2)][np.argsort(spec[f > 2])[::-1][:6]]
            print(f"FFT (cut {lo:.2f}, deg {deg}): top peaks (T): {np.round(np.sort(pk),2)}")
        except Exception as e: print("fft err", lo, deg, e)
    ax[1,0].set_xlim(0, 60); ax[1,0].set_xlabel("F (T)"); ax[1,0].legend(fontsize=7)
    # background-subtracted trace in 1/B
    m = B > (cut or 1.5)
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    ax[0,1].plot(1/B[m], dR, lw=0.7); ax[0,1].set_xlabel("1/B (1/T)"); ax[0,1].set_ylabel("dR (Ohm)"); ax[0,1].set_title("bg-subtracted (deg 5)")
    ax[1,1].plot(B[m], dR, lw=0.7); ax[1,1].set_xlabel("B (T)"); ax[1,1].set_ylabel("dR (Ohm)")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_firstpass_run{rid}.png", dpi=110)
    n = 3.2e12 if rid == 6 else -1.2e12
    try: print("F_L:", luttinger_frequency(abs(n) * 1e4))
    except Exception as e: print("F_L err", e)
