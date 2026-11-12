"""Runs 6 & 7 — SdH spot checks. Onset, tone set, F_L comparison; design inputs for the fan."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency, resolve_channels

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

def load(rid):
    g = open_run(f"data/{rid}")
    cols = list(g.cols)
    d = np.asarray(g.data)
    print(f"--- run {rid}: cols={cols} shape={d.shape}")
    mc = g.meta.get("measurement_config", g.meta.get("measurement_configs", {}))
    return g, cols, d, mc

for rid, n_spot in ((6, 3.2), (7, -1.2)):
    g, cols, d, mc = load(rid)
    print("   measurement_config keys:", list(mc)[:25])
    i_B = cols.index("magnet_field")
    B = d[:, i_B]
    # sr1 = Rxx, gain 1 (device card); I_bias = drive/100 MOhm
    i_sr1 = cols.index("sr1_X")
    p1 = g.meta["instruments"]["sr1"]["snapshot"]["parameters"]
    drive, sens = p1["amplitude"]["value"], p1["sensitivity"]["value"]
    print(f"   drive {drive} V, sr1 sens {sens} V, tau {p1['time_constant']['value']} s")
    Ib = float(drive) / float(mc["bias_resistor"])
    R = d[:, i_sr1] / 1.0 / Ib
    order = np.argsort(B)
    B, R = B[order], R[order]
    print(f"   I_bias = {Ib:.3e} A | B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts")
    print(f"   R: min {R.min():.1f}, max {R.max():.1f}, R(B~0) {R[0]:.1f} Ohm")
    FL = float(luttinger_frequency(abs(n_spot) * 1e16))  # 1e12 cm^-2 -> m^-2
    print(f"   F_L(|n|={abs(n_spot)}e12) = {FL:.2f} T")
    try:
        on = sdh_onset(R, B, r_full_scale=sens / Ib)
        print(f"   ONSET: {on.onset_b:.3f} T @ f={on.onset_freq:.2f} T | noise {on.noise_sigma:.3g} | clip_high_b {on.clip_high_b}")
        for t in on.tones:
            print(f"     tone f={t.freq:8.2f} T  onset={t.onset_b:5.2f} T  snr={float(np.max(t.snr)):7.1f} "
                  f"nper={float(np.max(t.n_periods)):5.1f} marg={t.marginal} cens={t.censored} harm_of={t.harmonic_of} f/F_L={t.freq/FL:.3f}")
    except Exception as e:
        print("   ONSET FAILED:", type(e).__name__, e)
    # FFT over a few B windows
    for blo, bhi in ((1.0, 10.0), (2.0, 10.0), (3.0, 10.0), (2.0, 6.0), (6.0, 10.0)):
        m = (B >= blo) & (B <= bhi)
        if m.sum() < 30:
            continue
        f, spec = sdh_fft(R[m][None, :].T.reshape(-1, 1).T.T, B[m]) if False else sdh_fft(R[m].reshape(-1, 1), B[m], nfft=4096)
        s = spec[0]
        keep = (f > 1.0) & (f < 3 * FL)
        fk, sk = f[keep], s[keep]
        pk = []
        for i in range(1, len(sk) - 1):
            if sk[i] > sk[i - 1] and sk[i] > sk[i + 1]:
                pk.append((sk[i], fk[i]))
        pk.sort(reverse=True)
        top = ", ".join(f"{fr:.1f}T({amp - np.median(sk):.2f})" for amp, fr in pk[:6])
        print(f"   FFT B[{blo},{bhi}]: N={m.sum():4d}  peaks: {top}   | F_L={FL:.1f}, .72FL={0.72*FL:.1f}, .28FL={0.28*FL:.1f}")
    # raw plot
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("R_xx (Ohm)"); ax[0].set_title(f"run {rid} raw, n={n_spot}e12")
    m = B > 1.0
    Rb = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1].plot(1 / B[m], Rb, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dR (Ohm)"); ax[1].set_title("bg-subtracted vs 1/B")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110); plt.close(fig)
    print()
