# === Runs 6 & 7 — onset + 1/B FFT, tones vs F_L and the fs_count model ===
from hera.analysis import sdh_onset, sdh_fft, luttinger_frequency

# fs_count_b0 model table (ABAB SWMcC / ABCA continuum; semi-quantitative — trust
# topology + partition, not absolute F):
#   n = +3.2e12: ABAB pair 7.31 / 25.78 T (m* 0.027 / 0.061 me), ABCA singleton 33.1 T
#   n = -1.2e12: ABAB pair ~5.3 / 7.1 T (near-CNP semimetal), ABCA 12.4 T (m* ~1 me, LK-dead at T_e~8K)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, (rid, n12) in zip(ax, [(6, 3.2), (7, -1.2)]):
    B, R, Imed = spot_trace(rid)
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    on = sdh_onset(R, B, r_full_scale=50e-6 / Imed)   # sr1 sens 50 uV both runs
    print(f"--- run {rid} (n = {n12:+.1f}e12, F_L = {FL:.1f} T) ---")
    print(on.summary())
    for cut in (max(on.onset_b, 0.6), 1.5):
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
        a.plot(f, spec[0], lw=0.8, label=f"cut {cut:.2f} T")
    a.axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L = {FL:.1f} T")
    a.set(xlabel="F (T)", xlim=(0, 1.5 * FL), title=f"run {rid} — FFT in 1/B")
    a.legend(fontsize=7)
fig.tight_layout()

# Luttinger / template arithmetic on the run-6 tone set:
f1, f2, f3 = 7.1, 22.2, 29.5
print(f"\nrun 6 pair reading: f1 + f2 = {f1+f2:.1f} T vs f3 = {f3} (sum tone, d = {f3-(f1+f2):+.1f} T ~ dF)")
print(f"  global scale (f1+f2)/F_L = {(f1+f2)/33.09:.3f}; partition {f1/(f1+f2):.3f} / {f2/(f1+f2):.3f} (model ABAB 0.221 / 0.779)")
print(f"harmonic-comb rival: 3*f1 = {3*f1:.1f} vs 22.2 (d = {22.2-3*f1:+.1f} = 2.9*dF); 4*f1 = {4*f1:.1f} vs 29.5 (d = {29.5-4*f1:+.1f})")
print(f"run 7 pair reading: 4.7 + 6.6 = {4.7+6.6:.1f} T vs F_L 12.4 -> scale {11.3/12.41:.3f} (electron side gave 0.885)")
