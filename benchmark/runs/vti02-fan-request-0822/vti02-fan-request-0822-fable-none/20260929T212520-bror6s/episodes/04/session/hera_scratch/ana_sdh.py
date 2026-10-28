# Runs 6 + 7 - SdH spot checks (raw first, then FFT/onset). R = (sr1_X/gain)/I_drain.
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError

MODEL = {6: dict(FL=33.1, abab=(7.5, 25.6), label="electron n=+3.2e12"),
         7: dict(FL=12.4, abab=(5.3, 7.1), label="hole n=-1.2e12")}

fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for k, rid in enumerate((6, 7)):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain               # measured drain current, A
    R = (r.col("sr1_X") / ch["sr1"].gain) / I         # Rxx B_1-B_2, Ohm
    srt = np.argsort(B); B, R = B[srt], R[srt]        # run 7 swept descending
    print(f"=== run {rid} ({MODEL[rid]['label']}): {len(B)} pts, B {B[0]:.2f}->{B[-1]:.2f} T, "
          f"R {R.min():.1f}..{R.max():.1f} Ohm, interrupted={r.interrupted}")

    ax[k, 0].plot(B, R, lw=0.6)
    ax[k, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw - {MODEL[rid]['label']}")

    try:
        o = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)   # 50 uV sens at 10 nA
        print(o.summary())
        onset = o.onset_b
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}"); onset = 3.0

    for blo in sorted({max(onset, 1.5), 3.0, 4.5}):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), log=False)
        s = sp[0] / sp[0].max()
        ax[k, 1].plot(f, s, lw=0.8, label=f"B in [{blo:.1f}, {B.max():.0f}] T")
        top = sorted(zip(s, f), reverse=True)[:5]
        print(f"  FFT b_lo={blo:.1f}: top freqs " + ", ".join(f"{ff:.1f} T ({ss:.2f})" for ss, ff in top))
    m = MODEL[rid]
    ax[k, 1].axvline(m["FL"], color="k", ls="--", lw=0.8, alpha=0.6)
    for x in m["abab"]:
        ax[k, 1].axvline(x, color="r", ls="--", lw=0.8, alpha=0.6)
    ax[k, 1].set(xlim=(0, 60), xlabel="F (T)", ylabel="FFT (norm)",
                 title=f"run {rid} SdH FFT (black dash F_L, red dash ABAB two-band model)")
    ax[k, 1].legend(fontsize=7)
fig.tight_layout()
