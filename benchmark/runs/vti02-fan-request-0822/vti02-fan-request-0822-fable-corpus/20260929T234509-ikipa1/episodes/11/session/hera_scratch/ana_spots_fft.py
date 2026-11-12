# Runs 6-7: onset (sdh_onset) + 1/B FFT vs F_L and the fs_count model tones
import sys
from hera.analysis import sdh_onset, SdhOnsetError
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fscm

SENS = 50e-6  # sr1 sensitivity both runs (metadata comments)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
reads = {}
for a, rid, n_cm2 in ((ax[0], 6, +3.2e12), (ax[1], 7, -1.2e12)):
    r = run(rid)
    B = r.col("magnet_field")
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    I = amp / r.meta["measurement_config"]["bias_resistor"]
    R = r.col("sr1_X") / I
    o = np.argsort(B); B, R = B[o], R[o]
    u, iu = np.unique(np.round(B, 5), return_index=True); B, R = B[iu], R[iu]
    F_L = luttinger_frequency(n_cm2 * 1e4)  # m^-2
    on = sdh_onset(R, B, r_full_scale=SENS / I)
    print(f"--- run {rid} (n = {n_cm2/1e12:+.1f}e12, F_L = {F_L:.1f} T) ---")
    print(on.summary())
    freqs, spec = sdh_fft(R[:, None], B, b_range=(on.onset_b, B.max()), bg_degree=5)
    sp = spec[0] / np.nanmax(spec[0])
    a.plot(freqs, sp, lw=0.8)
    a.axvline(F_L, color="k", ls=":", lw=1, label=f"F_L = {F_L:.1f} T")
    mtones = fscm.abab_mstar(n_cm2 * 1e4)
    for F, m in mtones:
        a.axvline(F, color="tab:red", ls="--", lw=0.8)
    a.set(xlim=(0, 1.3 * F_L), xlabel="F (T)", ylabel="FFT amp (norm)",
          title=f"run {rid}: FFT above onset {on.onset_b:.2f} T; red dashed = model ABAB pair")
    a.legend(fontsize=8)
    reads[rid] = (F_L, on, [(F, m) for F, m in mtones])
fig.tight_layout()
