# Runs 6-7 - SdH content: per-tone onsets (sdh_onset) + FFT in 1/B (sdh_fft), two high-B windows.
from hera.analysis import resolve_channels, sdh_onset

FS_R = 50e-6 / 10e-9   # sr1 sensitivity / nominal I_bias = 5 kOhm full scale
spots = {6: "+3.2e12 (electron)", 7: "-1.2e12 (hole)"}
fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for j, i in enumerate((6, 7)):
    g = run(i)
    ch = {c.cid: c for c in resolve_channels(g.meta)}
    B = g.col("magnet_field")
    I = g.col("sr0_X") / ch["sr0"].gain
    R = (g.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B)
    B, R = B[o], R[o]
    ax[0, j].plot(B, R, lw=0.6)
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {i}: n = {spots[i]}, D = 0")
    print(f"===== run {i} (n = {spots[i]}) =====")
    print(sdh_onset(R, B, r_full_scale=FS_R).summary(), "\n")
    for b_lo, ls in ((1.5, "-"), (3.0, "--")):
        f, s = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()))
        ax[1, j].plot(f, s[0] / s[0].max(), ls, lw=0.8, label=f"FFT window B ({b_lo}, {B.max():.0f}) T")
    ax[1, j].set_xlim(0, 80); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("FFT amp (norm)")
    ax[1, j].legend(fontsize=8)
fig.tight_layout(); plt.show()

# Frequency bookkeeping, run 6: the two dominant incommensurate peaks vs the run-5 density calibration.
F1 = luttinger_frequency(1e16)   # T per 1e12 cm^-2, full 4-fold degeneracy
F_light, F_heavy = 7.0, 29.9     # dominant FFT peaks (resolution ~0.3-0.5 T)
print(f"run 6: F_light + F_heavy = {F_light + F_heavy:.1f} T -> n_implied = {(F_light + F_heavy) / F1:.2f}e12 cm^-2 "
      f"vs run-5 cal spot n = +3.20e12 ({100 * ((F_light + F_heavy) / F1 / 3.2 - 1):+.0f}% sum-rule excess)")
print(f"light-tone ladder: 2x = {2 * F_light:.1f}, 3x = {3 * F_light:.1f}, 4x = {4 * F_light:.1f} T; "
      f"combinations: F_heavy - F_light = {F_heavy - F_light:.1f}, F_heavy - 2 F_light = {F_heavy - 2 * F_light:.1f} T")
print(f"F_L(3.2e12, single 4-fold pocket) = {3.2 * F1:.1f} T")
