# Runs 6-7: per-tone onsets (sdh_onset matched filter) + SdH FFT in 1/B, read against the FS-count model.
import sys
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fsm
from hera.analysis import sdh_onset

I_BIAS = 10e-9
FS_OHM = 50e-6 / I_BIAS
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.6))
for a, (i, side, n12, blo) in zip(ax, ((6, "electron", +3.2, 1.2), (7, "hole", -1.2, 0.75))):
    r = run(i)
    B, R = r.col("magnet_field"), r.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    on = sdh_onset(R, B, r_full_scale=FS_OHM)
    print(f"--- run {i} ({side}, n = {n12:+.1f}e12): F_L = {FL:.1f} T, onset_b = {on.onset_b:.2f} T"
          f"{' (censored: carrying tone persists to the record low edge)' if any(t.censored for t in on.tones) else ''} ---")
    for t in on.tones:
        if not t.marginal:
            print(f"  tone F = {t.freq:6.2f} T  (F/F_L = {t.freq/FL:.3f}, onset {t.onset_b:.2f} T"
                  + (", censored" if t.censored else "")
                  + (f", ratio-tagged harmonic_of {t.harmonic_of:.2f}" if t.harmonic_of else "") + ")")
    f, spec = sdh_fft(R[:, None], B, b_range=(blo, 10.0), nfft=4096, log=False)
    sp = spec[0] / spec[0].max()
    a.plot(f, sp, lw=0.9, label=f"FFT, {blo}-10 T")
    a.axvline(FL, color="k", ls=":", label=f"F_L = {FL:.1f} T (scale 1)")
    _, orbs = fsm.abab_fs(n12 * 1e16)
    for F, kF in orbs:
        a.axvline(F, color="tab:red", ls="--", lw=0.8)
    a.plot([], [], color="tab:red", ls="--", lw=0.8, label="ABAB model pair (scale 1)")
    a.set(xlim=(0, 1.9 * FL), xlabel="F (T)", ylabel="FFT amp (norm)",
          title=f"run {i} — {side} (dF = {1/(1/blo - 0.1):.1f} T)")
    a.legend(fontsize=8)
fig.suptitle("sdh-spot-check FFTs vs tetralayer FS-count model — vti-02, D = 0")
fig.tight_layout(); plt.show()

# Luttinger / template arithmetic on the matched-filter frequencies:
print()
for side, fl_, light, heavy, extra in (("electron n=+3.2e12", 33.09, 7.11, 22.08, 29.47),
                                       ("hole    n=-1.2e12", 12.41, 4.72, 6.59, 12.34)):
    tot = light + heavy
    print(f"{side}: pair {light:.2f} + {heavy:.2f} = {tot:.2f} T -> global scale {tot/fl_:.2f} vs F_L; "
          f"partition {light/tot:.2f}/{heavy/tot:.2f}; extra tone {extra:.2f} T = {extra/tot:.2f} x pair-sum "
          f"(breakdown/sum-tone candidate at scaled F_L)")
n_eff = 3.2 * 0.88
_, orbs = fsm.abab_fs(n_eff * 1e16)
Fs = [F for F, _ in orbs]
print(f"model check at n_eff = {n_eff:.1f}e12 (scale 0.88): ABAB pair {Fs[0]:.1f}/{Fs[1]:.1f} T "
      f"(partition {Fs[0]/sum(Fs):.2f}/{Fs[1]/sum(Fs):.2f}) vs measured 7.11/22.08 (0.24/0.76)")
