"""Runs 6-7 (sdh-spot-check, D = 0): raw traces, onset, 1/B FFT vs F_L and the model tones."""
import sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs
from hera.analysis import sdh_onset

H_4E = 4.1357e-15 / 4  # h/4e in T per m^-2

spots = {6: +3.2, 7: -1.2}  # run id -> n (1e12 cm^-2), both at D = 0 (run-5 cal)
fig, axes = plt.subplots(2, 3, figsize=(15, 7.5))

for i, (rid, n12) in enumerate(spots.items()):
    r = run(rid)
    B, x = r.col("magnet_field"), r.col("sr1_X")
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    i_bias = amp / r.meta["measurement_config"]["bias_resistor"]
    R = x / i_bias  # sr1 unity gain
    order = np.argsort(B); B, R = B[order], R[order]
    F_L = abs(n12) * 1e16 * H_4E
    on = sdh_onset(R, B, r_full_scale=50e-6 / i_bias)
    print(f"=== run {rid}: n = {n12:+.1f}e12, F_L = {F_L:.1f} T, I_bias = {i_bias*1e9:.1f} nA ===")
    print(on.summary()); print()

    ax = axes[i, 0]
    ax.plot(B, R, lw=0.6)
    ax.axvline(on.onset_b, color="r", ls="--", lw=0.8, label=f"onset {on.onset_b:.2f} T")
    ax.set(xlabel="B (T)", ylabel="Rxx (Ω)", title=f"run {rid} raw — n = {n12:+.1f}e12")
    ax.legend(fontsize=7)

    ax = axes[i, 1]
    m = B > 0.3
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax.plot(B[m], dR, lw=0.6)
    ax.set(xlabel="B (T)", ylabel="ΔRxx (Ω)", title="MR background removed (deg-5 in B)")

    ax = axes[i, 2]
    for cut in (on.onset_b, on.onset_b * 1.2, on.onset_b * 1.5):
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
        ax.plot(freqs, spec[0], lw=0.8, label=f"cut {cut:.2f} T")
    ax.axvline(F_L, color="k", ls=":", lw=1.2, label=f"F_L = {F_L:.1f} T")
    _, orb = abab_fs(n12 * 1e16)
    for F, _kf in orb:
        if F > 0.5:
            ax.axvline(F, color="tab:green", ls="--", lw=0.8)
    ax.set(xlabel="F (T)", ylabel="FFT amp", xlim=(0, F_L * 1.6),
           title="FFT in 1/B (green dashes: model ABAB pair)")
    ax.legend(fontsize=7)

fig.tight_layout(); plt.show()

# model context at the spot densities (scale = geometry prior)
for n12 in (+3.2, -1.2):
    _, orb = abab_fs(n12 * 1e16)
    F_L = abs(n12) * 1e16 * H_4E
    print(f"model @ n={n12:+.1f}e12: F_L={F_L:.1f} T; ABAB pair "
          + ", ".join(f"{F:.1f} T [{F/F_L:.2f}·F_L]" for F, _ in orb)
          + f"; ABCA singleton {F_L:.1f} T")
