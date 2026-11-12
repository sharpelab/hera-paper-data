"""sdh-spot-check runs 6 (electron n=+3.2e12) & 7 (hole n=-1.2e12), D = 0: raw R(B), windowed
FFT in 1/B, per-tone onsets (hera.analysis.sdh_onset). Model overlays: tetralayer_fs_count."""
import sys
from scipy.signal import find_peaks

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
from hera.analysis import sdh_onset

I_BIAS = 1.0 / 100e6                     # 1 V drive / 100 MOhm
R_FS = 50e-6 / I_BIAS                    # sr1 sens 50 uV -> 5 kOhm full scale
cases = {                                # model pair from fs_count_b0.abab_fs (SI m^-2 input)
    6: dict(n=+3.2e16, brange=(1.0, 10.0), model=dict(light=7.31, heavy=25.78),
            label="run 6 — electron n=+3.2e12, B 0→10 T (10 mT ≥1 T; 50 mT below = aliased for F ≥ 4 T)"),
    7: dict(n=-1.2e16, brange=(0.72, 10.0), model=dict(light=1.15, heavy=11.25),
            label="run 7 — hole n=−1.2e12, B 10→0.3 T (20 mT)"),
}

fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for i, (rid, c) in enumerate(cases.items()):
    r = run(rid)
    assert not r.interrupted
    B, R = r.col("magnet_field"), r.col("sr1_X") / I_BIAS   # sr1 gain 1
    o = np.argsort(B)
    B, R = B[o], R[o]
    FL = float(luttinger_frequency(c["n"]))

    ax = axs[0, i]                                          # raw first
    ax.plot(B, R, lw=0.6, color="k")
    ax.set(xlabel="B (T)", ylabel=r"Rxx ($\Omega$)", title=c["label"], xlim=(0, 10.2))

    freqs, spec = sdh_fft(R[:, None], B, b_range=c["brange"], log=False)
    s = spec[0] / spec[0][freqs > 2].max()
    ax2 = axs[1, i]
    ax2.plot(freqs, s, lw=0.9, color="k")
    ax2.axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    ax2.axvline(c["model"]["light"], color="tab:blue", ls=":", lw=1, label=f"model ABAB light {c['model']['light']:.1f} T")
    ax2.axvline(c["model"]["heavy"], color="tab:green", ls=":", lw=1, label=f"model ABAB heavy {c['model']['heavy']:.1f} T")
    ax2.set(xlabel="F (T)", xlim=(0, 1.4 * FL), ylim=(0, 1.1), ylabel="FFT mag (norm)",
            title=f"run {rid} FFT, B ∈ {c['brange']} T; δF = {1/(1/c['brange'][0]-1/c['brange'][1]):.2f} T")
    ax2.legend(fontsize=8, loc="upper right")

    print(f"===== {c['label']} =====   F_L = {FL:.1f} T; R {R.min():.0f}..{R.max():.0f} Ohm (FS {R_FS:.0f})")
    ons = sdh_onset(R, B, r_full_scale=R_FS)
    print(f"sdh_onset: onset_b = {ons.onset_b:.2f} T (carrying tone censored: {ons.tones[0].censored})")
    for t in sorted(ons.tones, key=lambda t: -t.contrast)[:6]:
        print(f"  tone F = {t.freq:6.2f} T ({t.freq/FL:.3f} F_L)  contrast {t.contrast:6.1f}  onset {t.onset_b:.2f} T"
              f"{'  CENSORED' if t.censored else ''}{f'  flagged harmonic_of {t.harmonic_of:.2f}' if t.harmonic_of else ''}")
    pk, _ = find_peaks(s, height=0.08, distance=4)
    print("  windowed-FFT peaks:", ", ".join(f"{freqs[p]:.2f} T ({freqs[p]/FL:.2f} F_L)" for p in pk if freqs[p] > 1.5))

fig.tight_layout()
plt.show()
