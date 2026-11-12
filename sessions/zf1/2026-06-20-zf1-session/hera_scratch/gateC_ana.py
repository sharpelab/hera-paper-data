import numpy as np
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print(summarize_run(run))
print("interrupted:", run.interrupted)
print("cols:", run.cols)

# --- drive / bias truth from metadata ---
mc = run.meta.get("measurement_config", {})
print("\n=== bias config ===")
for k in ("bias_voltage_1", "bias_resistor", "lockin_freq_1", "sr1_gain", "comment"):
    print(f"  {k}: {mc.get(k)}")
bias_v = mc.get("bias_voltage_1")
bias_r = mc.get("bias_resistor")
if bias_v and bias_r:
    print(f"  => I_bias = {bias_v/bias_r*1e9:.4f} nA")

# --- leakage ---
print("\n=== gate leakage ===")
for c in ("k_tg_curr", "k_bg_curr"):
    if c in run.cols:
        v = np.abs(run.col(c))
        print(f"  |{c}| max = {v.max():.3e} A   med = {np.median(v):.3e} A")

# --- current channel: alive? pinned at I_bias? ---
print("\n=== current channel sr830_1 (5-4) ===")
i = run.col("sr830_1_X") / mc.get("sr1_gain", -1e6)
print(f"  I med {np.median(i)*1e12:.2f} pA  min {i.min()*1e12:.2f}  max {i.max()*1e12:.2f}")

# --- voltage channels -> R = (X/gain)/I_bias ---
vbg = run.col_at(run.col_indices("k_bg_volt")[-1])  # readback (last occurrence)
Ibias = bias_v / bias_r
print("\n=== voltage channels R = (X/100)/I_bias ===")
for name, pair in (("sr830_2_X","5-4 (2T)"), ("sr830_3_X","30-31 (4T Rxx)"), ("sr830_4_X","5-30 (3T)")):
    R = (run.col(name)/1e2)/Ibias
    print(f"  {name} [{pair}]: R med {np.median(R):.1f}  min {R.min():.1f}  max {R.max():.1f}  ohm")
    # SNR proxy: scatter of adjacent-point differences
    noise = np.std(np.diff(R))/np.sqrt(2)
    print(f"      pt-pt noise ~ {noise:.1f} ohm")

# grounded-short test: are all V channels identical?
r2 = (run.col("sr830_2_X")/1e2)/Ibias
r3 = (run.col("sr830_3_X")/1e2)/Ibias
print("\n=== grounded-short test (channels must DIFFER) ===")
print(f"  corr(sr2,sr3) = {np.corrcoef(r2, r3)[0,1]:.3f}  (identical->1.0 = short)")
print(f"  sr2 range {r2.max()-r2.min():.0f} ohm  vs  sr3 range {r3.max()-r3.min():.0f} ohm")

# CNP location from 2T (sr2) peak
imax = np.argmax(r2)
print(f"\n=== CNP recon ===")
print(f"  sr830_2 (2T) R peak at k_bg = {vbg[imax]:+.3f} V (R={r2[imax]:.0f} ohm)")
i3 = np.argmax(r3)
print(f"  sr830_3 (4T) R peak at k_bg = {vbg[i3]:+.3f} V (R={r3[i3]:.0f} ohm)")
