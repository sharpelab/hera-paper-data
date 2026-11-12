"""SdH spot checks (runs 6 electron / 7 hole): raw R(B), onset, FFT tones.
Read: how many Fermi surfaces, onset field, signal size -> sizes the Landau fan."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError,
                           GateCalibration, luttinger_frequency)

HERE = Path(__file__).resolve().parent.parent
CAL = GateCalibration(c_tg=2.796e-03, c_bg=2.161e-03,
                      n_offset=-0.0894e16, D_offset=-0.013e9)

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, (rid, Vtg, Vbg, lbl) in enumerate([(6, +0.9836, +1.1661, "electron"),
                                          (7, -0.2770, -0.4650, "hole")]):
    r = open_run(str(HERE / "data" / str(rid)))
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col_at(cur.idx) / 1.0          # sr0 already gain-divided at fp time? check below
    V = r.col("sr1_X")
    # gains: sr0_gain -1e6 (transimpedance), sr1 gain 1
    mcg = r.meta["measurement_config"]
    I = r.col("sr0_X") / mcg["sr0_gain"]
    Rxx = np.abs(V / 1.0 / I)
    o = np.argsort(B); B, Rxx, I = B[o], Rxx[o], I[o]
    n = CAL.density(Vtg, Vbg)
    FL = luttinger_frequency(n)
    print(f"=== run {rid} ({lbl}): n = {n*1e-16:+.3f}e12 cm^-2, F_L(full density) = {FL:.2f} T")
    print(f"    |I| = {np.median(np.abs(I))*1e9:.3f} nA, R range {Rxx.min():.1f} - {Rxx.max():.1f} Ohm, "
          f"R(B=min) {Rxx[0]:.1f}, R(B=max) {Rxx[-1]:.1f}")
    T = r.col("T_sample"); print(f"    T_sample {T.mean():.3f} +- {T.std():.3f} K")
    itg = np.abs(r.col("k_2400_tg_curr")); ibg = np.abs(r.col("k_2400_bg_curr"))
    print(f"    leakage max |I_tg| {itg.max()*1e12:.0f} pA, |I_bg| {ibg.max()*1e12:.0f} pA")

    ax = axes[k, 0]; ax.plot(B, Rxx, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} raw — {lbl}, n={n*1e-16:+.2f}e12")

    # onset
    try:
        so = sdh_onset(Rxx, B, r_full_scale=50e-6 / np.median(np.abs(I)))
        print(so.summary())
        out[rid] = so
    except SdhOnsetError as e:
        print(f"    sdh_onset FAILED: {e}")

    # background-subtracted vs 1/B
    m = B > 0.9
    bg = np.polyval(np.polyfit(B[m], Rxx[m], 5), B[m])
    ax = axes[k, 1]; ax.plot(1/B[m], Rxx[m]-bg, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} detrended (deg5, B>0.9 T)")

    # FFT over a few windows
    ax = axes[k, 2]
    for blo, bhi in [(1.5, 10.0), (3.0, 10.0), (5.0, 10.0)]:
        if B.max() < bhi - 0.5: bhi = B.max()
        f, spec = sdh_fft(Rxx[:, None], B, b_range=(blo, bhi), nfft=4096, bg_degree=5, log=False)
        s = spec[0]
        ax.plot(f, s/s.max(), lw=0.9, label=f"{blo}-{bhi} T")
        pk = f[(f > 3) & (f < 120)][np.argsort(s[(f > 3) & (f < 120)])[-6:]][::-1]
        print(f"    FFT {blo}-{bhi} T: top peaks (T) = {np.round(pk,1)}")
    ax.axvline(FL, color="k", ls="--", lw=1, label=f"$F_L$={FL:.1f} T")
    ax.axvline(FL/2, color="gray", ls=":", lw=1, label=f"$F_L$/2={FL/2:.1f} T")
    ax.set_xlim(0, min(120, 3*FL)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} SdH FFT")

plt.tight_layout(); plt.savefig(HERE / "hera_scratch" / "spot_sdh.png", dpi=110)
print("wrote hera_scratch/spot_sdh.png")
