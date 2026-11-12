"""Runs 6-7 raw view: SdH spot checks at D = 0 (`sdh-spot-check`).
Run 6: electron n = +3.2e12, B 0 -> 10 T (50 mT to 1 T, 10 mT above), sr1 50 uV.
Run 7: hole n = -1.2e12, B 10 -> 0.3 T ride-down, 20 mT, sr1 50 uV.
Gain-divided Rxx = (sr1_X/1) / (sr0_X/-1e6) from the TSV, no background removal."""
from hera.analysis import resolve_channels


def spot_trace(rid):
    r = run(rid)
    gains = {c.cid: c.gain for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / gains["sr0"]            # measured drain current, A
    R = (r.col("sr1_X") / gains["sr1"]) / I      # signed Rxx, ohm
    o = np.argsort(B)                            # run 7 descends; sort ascending
    return B[o], R[o], I[o], r


R_FS_50UV = 50e-6 / 9.9e-9  # 50 uV sensitivity at the measured ~9.9 nA bias = 5.05 kOhm

fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.8))
for a, (rid, lab) in zip(axs, ((6, "run 6 — electron, n = +3.2e12, D = 0"),
                               (7, "run 7 — hole, n = −1.2e12, D = 0"))):
    B, R, I, r = spot_trace(rid)
    print(summarize_run(r))
    a.plot(B, R, lw=0.6)
    a.set_xlabel("B (T)"); a.set_ylabel(r"$R_{xx}$ ($\Omega$)"); a.set_title(lab, fontsize=10)
    print(f"run {rid}: complete={not r.interrupted}; I_bias {np.median(np.abs(I))*1e9:.2f} nA; "
          f"R(B~0) {np.median(np.abs(R[:10])):.0f} Ohm; max|R| {np.abs(R).max():.0f} Ohm "
          f"= {np.abs(R).max()/R_FS_50UV*100:.0f}% of the 50 uV full scale (no clipping)\n")
fig.tight_layout()
