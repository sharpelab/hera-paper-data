from hera.analysis import open_run
import numpy as np
r = open_run("data/0")
vbg = r.col("k_2400_volt")
ibg = r.col("k_2400_curr")
isi = r.col("k_2410_curr")
sr0 = r.col("sr0_X"); sr1 = r.col("sr1_X"); sr2 = r.col("sr2_X"); sr3 = r.col("sr3_X")

Ibias = 0.5/100e6   # 5 nA
Rxx1 = sr1/Ibias; Rxx2 = sr2/Ibias            # voltage channels, no gain div
Idrain = sr0/1e6                              # Ithaco gain 1e6

print(f"{'Vbg':>7} {'I_bg(pA)':>9} {'I_si(pA)':>9} {'Rxx1(kohm)':>11} {'Rxx2(kohm)':>11} {'Idrain(nA)':>10}")
for i in range(0, 181, 12):
    print(f"{vbg[i]:7.2f} {ibg[i]*1e12:9.2f} {isi[i]*1e12:9.2f} {Rxx1[i]/1e3:11.3f} {Rxx2[i]/1e3:11.3f} {Idrain[i]*1e9:10.3f}")

print("\n--- leakage extremes ---")
print(f"|I_bg| max: {np.abs(ibg).max()*1e12:.1f} pA at Vbg={vbg[np.argmax(np.abs(ibg))]:.2f} V")
print(f"|I_si| max: {np.abs(isi).max()*1e12:.1f} pA at Vbg={vbg[np.argmax(np.abs(isi))]:.2f} V")
print(f"I_bg sign: min {ibg.min()*1e12:.1f} pA, max {ibg.max()*1e12:.1f} pA")
print("\n--- Rxx range ---")
print(f"Rxx1: {np.nanmin(Rxx1)/1e3:.2f}..{np.nanmax(Rxx1)/1e3:.2f} kohm ; peak at Vbg={vbg[np.argmax(Rxx1)]:.2f}")
print(f"Rxx2: {np.nanmin(Rxx2)/1e3:.2f}..{np.nanmax(Rxx2)/1e3:.2f} kohm ; peak at Vbg={vbg[np.argmax(Rxx2)]:.2f}")
print(f"Idrain: {Idrain.min()*1e9:.3f}..{Idrain.max()*1e9:.3f} nA")
