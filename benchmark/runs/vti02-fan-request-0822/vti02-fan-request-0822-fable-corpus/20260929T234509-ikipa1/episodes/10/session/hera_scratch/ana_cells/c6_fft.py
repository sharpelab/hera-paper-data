# Run 6 — onset + 1/B FFT vs the FS-count model (fs_count_b0), electron side n = +3.2e12.
import sys
from hera.analysis import sdh_onset

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fsm

n6 = 3.2e16                                  # m^-2 (run-5 cal; scale = geometry prior)
FL6 = luttinger_frequency(n6)                # 33.1 T
_, orbs = fsm.abab_fs(n6)                    # ABAB Onsager pair at the geometry-prior scale
F_abab = [F for F, _ in orbs]
print(f"F_L(g=4) = {FL6:.1f} T | model ABAB pair = {F_abab[0]:.2f} + {F_abab[1]:.2f} T | ABCA singleton = F_L")

on6 = sdh_onset(R6, B6, r_full_scale=50e-6 / I6)
print(on6.summary())
print("NB: sub-1 T leg is 50 mT background-only — cannot Nyquist a 7.5 T tone below ~0.9 T, so the")
print("    'censored @ 0.30 T' carrying tone and the censored low tones (3.0/4.2/5.1/9.5 T) ride an")
print("    aliased leg. Onset is UNMEASURED; run 8 (low-field extension) pins it.")

fig, ax = plt.subplots(figsize=(10, 3.6))
for cut in (1.0, 1.3, 1.6):
    freqs, spec = sdh_fft(R6[:, None], B6, b_range=(cut, B6.max()), bg_degree=5)
    ax.plot(freqs, spec[0] / spec[0].max(), lw=0.8, label=f"cut {cut:.1f} T")
ax.axvline(FL6, color="k", ls="--", label=f"F_L = {FL6:.1f} T")
for F in F_abab:
    ax.axvline(F, color="tab:red", ls=":", label=f"ABAB model {F:.1f} T")
for k in range(1, 5):
    ax.axvline(k * 7.45, color="0.6", lw=0.5)
ax.set(xlim=(0, 70), xlabel="F (T)", ylabel="FFT (norm)",
       title="run 6 FFT in 1/B (B >= cut): comb 7.5/14.9/22.4/29.8 (grey: k x 7.45)")
ax.legend(fontsize=7, ncol=2)
plt.show()
