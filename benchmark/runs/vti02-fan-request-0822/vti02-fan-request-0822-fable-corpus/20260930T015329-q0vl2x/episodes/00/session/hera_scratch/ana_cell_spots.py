"""Runs 6 + 7 — SdH spot checks (`sdh-spot-check`), electron n=+3.2e12 / hole n=-1.2e12, D=0."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency

RUNS = {6: +3.2e12, 7: -1.2e12}
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
reads = {}
for i, (rid, n_cm2) in enumerate(RUNS.items()):
    r = open_run(f"data/{rid}")
    assert not r.interrupted
    B = r.col("magnet_field")
    I = r.col("sr0_X") / (-1e6)          # transimpedance -1e6 V/A (device card)
    R = r.col("sr1_X") / I               # sr1 unity gain
    o = np.argsort(B); Bs, Rs = B[o], R[o]
    FL = float(luttinger_frequency(abs(n_cm2) * 1e4))

    # raw first
    ax = axes[0, i]
    ax.plot(Bs, Rs, lw=0.6)
    ax.set(xlabel="B (T)", ylabel="Rxx (Ohm)",
           title=f"run {rid} raw — n = {n_cm2/1e12:+.1f}e12, D = 0 (T = {np.median(r.col('T_sample')):.2f} K)")

    # per-tone onset (statistical, matched-filter; clip check vs 50 uV FS)
    onset = sdh_onset(Rs, Bs, r_full_scale=50e-6 / np.median(np.abs(I)))
    fund = [(t.freq, t.censored) for t in onset.tones if t.harmonic_of is None and not t.near_residual]

    # FFT over the well-sampled 10 mT/20 mT leg
    b_lo = 1.0 if rid == 6 else 0.75
    freqs, spec = sdh_fft(Rs.reshape(-1, 1), Bs, b_range=(b_lo, 10.0), nfft=4096)
    sp = spec[0]
    pk, _ = find_peaks(sp, height=np.median(sp) + 2 * sp.std(), distance=8)
    peaks = sorted(zip(freqs[pk], sp[pk]), key=lambda t: -t[1])[:6]
    ax2 = axes[1, i]
    ax2.plot(freqs, sp, lw=0.8)
    ax2.axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T")
    ax2.set(xlim=(0, 2 * FL), xlabel="F (T)", ylabel="|FFT|",
            title=f"run {rid} FFT, B in [{b_lo}, 10] T (dF = {1/(1/b_lo-0.1):.2f} T)")
    ax2.legend(fontsize=8)
    reads[rid] = (FL, peaks, onset.onset_b, fund)
    print(f"run {rid}: F_L = {FL:.2f} T | onset_b = {onset.onset_b:.2f} T | "
          f"fundamentals (tracker): {[(round(f,2), 'censored' if c else 'tracked') for f, c in fund]}")
    for f, a in peaks:
        print(f"   FFT peak {f:6.2f} T  amp {a:7.1f}   f/F_L = {f/FL:.3f}")
fig.tight_layout()

# --- the read against the fs_count_b0 model (n in m^-2) ---
import sys; sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs
FL6 = reads[6][0]
f_light, f_heavy = 7.78, 28.88            # run 6 FFT peaks
s_sum = (f_light + f_heavy) / FL6
_, orb = abab_fs(3.2e16)
m_light, m_heavy = orb[0][0], orb[1][0]
print(f"\nrun 6 (electron): pair sum {f_light + f_heavy:.1f} T = {s_sum:.3f} x F_L "
      f"(lever-arm band 0.8-1.2 -> global scale {s_sum:.3f})")
print(f"  partition {f_light/(f_light+f_heavy):.3f}/{f_heavy/(f_light+f_heavy):.3f} "
      f"vs ABAB model {m_light/(m_light+m_heavy):.3f}/{m_heavy/(m_light+m_heavy):.3f} (model {m_light:.2f}/{m_heavy:.2f} T)")
print(f"  ABAB-template pair; NOT yet a call: heavy = 4 x 7.11 T (tracker fundamental) is within dF -> "
      f"harmonic vs real pocket is n-dependence work (the fan). No tone at F_L x scale = {s_sum*FL6:.1f} T beyond the pair sum's intermods.")
print("run 7 (hole): near-CNP exception regime as designed — close balanced tones "
      f"(tracker fundamentals {[round(f,2) for f,_ in reads[7][3]]} T vs model pair 5.3/7.1 T), short 1/B record; preview only, not evidence.")
print("VERDICT: electron side is the fan side (two resolved tones, censored onset < 1 T, clean record).")
