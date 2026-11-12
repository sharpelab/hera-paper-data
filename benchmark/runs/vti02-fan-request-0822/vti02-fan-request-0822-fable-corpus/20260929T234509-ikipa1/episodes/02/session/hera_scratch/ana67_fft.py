"""Runs 6-7 frequency read: sdh_onset (per-tone onsets, harmonic pairing, clip
guard via r_full_scale) + sdh_fft in 1/B over a cutoff ladder, against F_L and
the fs_count forward model (hera/models/tetralayer_fs_count/fs_count_b0.py,
u_D = 0; semi-quantitative -- trust partition/topology, not absolute F)."""
from hera.analysis import sdh_onset, SdhOnsetError

MODEL = {  # fs_count_b0: (F_L, ABAB pair, ABCA singleton) at the spot densities
    6: dict(F_L=33.09, abab=(7.31, 25.78), abab_m=(0.027, 0.061), abca=33.1),
    7: dict(F_L=12.41, abab=(6.54, 5.86), abab_m=(0.032, 0.074), abca=12.4),
}

fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.0))
for a, rid in zip(axs, (6, 7)):
    B, R, I, r = spot_trace(rid)
    mdl = MODEL[rid]
    print("=" * 72)
    on = sdh_onset(R, B, r_full_scale=R_FS_50UV)
    print(f"RUN {rid}:  F_L = {mdl['F_L']:.1f} T")
    print(on.summary())
    # FFT stability ladder: cutoff at onset and above (residual-background check)
    for co in (max(on.onset_b, 0.3), 0.5, 0.8):
        f, spec = sdh_fft(R[:, None], B, b_range=(co, float(B.max())), log=False)
        a.plot(f, spec[0] / np.nanmax(spec[0]), lw=0.8, label=f"cutoff {co:.2f} T")
    a.axvline(mdl["F_L"], color="k", ls=":", lw=1.2, label=f"F_L = {mdl['F_L']:.1f} T")
    for F, ls in zip(mdl["abab"], ("--", "-.")):
        a.axvline(F, color="tab:red", ls=ls, lw=0.9)
    a.set_xlim(0, mdl["F_L"] * 1.55); a.set_xlabel("F (T)"); a.set_ylabel("FFT amp (norm)")
    a.set_title(f"run {rid} SdH FFT — red: ABAB model pair, dotted: F_L", fontsize=9)
    a.legend(fontsize=7)
fig.tight_layout()

# Luttinger / partition arithmetic on the run-6 candidate pair (electron side)
f1, f2, FL = 7.1, 22.1, MODEL[6]["F_L"]
print("\nrun 6 candidate pair: 7.1 + 22.1 = "
      f"{f1+f2:.1f} T = {(f1+f2)/FL:.2f} x F_L; partition {f1/(f1+f2):.2f}/{f2/(f1+f2):.2f} "
      f"(ABAB model at n=+3.2e12: {7.31/33.09:.2f}/{25.78/33.09:.2f})")
print("run 7 candidate pair: 4.7 + 6.6 = "
      f"{4.7+6.6:.1f} T = {(4.7+6.6)/MODEL[7]['F_L']:.2f} x F_L (model pair 5.9/6.5 -- near-CNP balanced regime)")
