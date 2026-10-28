import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run

r = open_run('data/1')
mc = r.meta['measurement_config']
Ibias = mc['bias_voltage'] / mc['bias_resistor']
g0 = mc['sr0_gain']

V   = r.col('DC_bias')
I   = r.col('sr0_X') / g0                 # drain current (A)
Rxx1 = r.col('sr1_X') / Ibias             # Rxx T3-T4 (Ohm)
Rxx2 = r.col('sr2_X') / Ibias             # Rxx B4-B5
Rxy3 = r.col('sr3_X') / Ibias             # Rxy T5-B6
ibg = r.col('k_bg_curr'); isi = r.col('k_2410_curr')

print(f'I_bias = {Ibias*1e9:.3f} nA ; sr0_gain={g0:g}')
print(f'sr0 drain I: med {np.median(I)*1e9:.3f} nA, min {I.min()*1e9:.3f}, max {I.max()*1e9:.3f}  (flat => current-bias OK)')
print(f'sr1 Rxx: min {np.nanmin(Rxx1):.1f}  max {np.nanmax(Rxx1):.1f}  @Vpeak={V[np.nanargmax(Rxx1)]:.3f} V')
print(f'sr2 Rxx: min {np.nanmin(Rxx2):.1f}  max {np.nanmax(Rxx2):.1f}  @Vpeak={V[np.nanargmax(Rxx2)]:.3f} V')
print(f'sr3 Rxy: min {np.nanmin(Rxy3):.1f}  max {np.nanmax(Rxy3):.1f}')
print(f'LEAKAGE k_bg.curr:  max|I| {np.abs(ibg).max():.3e} A')
print(f'LEAKAGE k_2410.curr: max|I| {np.abs(isi).max():.3e} A')
# channel-independence / grounded-short check
print(f'corr(sr1,sr2) = {np.corrcoef(Rxx1,Rxx2)[0,1]:.3f} ; identical? {np.allclose(Rxx1,Rxx2)}')
# quantization step
dq = np.diff(np.unique(np.round(Rxx1,3)))
print(f'sr1 R smallest level step ~ {np.min(dq[dq>0]):.2f} Ohm (digitization grain)')

fig, ax = plt.subplots(2,1, figsize=(7,7), sharex=True)
ax[0].plot(V, Rxx1, '.-', label='sr1 Rxx T3-T4')
ax[0].plot(V, Rxx2, '.-', label='sr2 Rxx B4-B5')
ax[0].set_ylabel('Rxx (Ohm)'); ax[0].legend(); ax[0].grid(alpha=.3)
ax[0].set_title('Gate C liveness (run 1): TG trace, BG=Si=0, B=0  [sens 5mV -> quantized]')
ax[1].plot(V, I*1e9, '.-', color='k', label='sr0 drain I (nA)')
ax[1].plot(V, Rxy3, '.-', color='C3', label='sr3 Rxy (Ohm)')
ax[1].set_xlabel('DC_bias = V_TG (V)'); ax[1].legend(); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig('hera_scratch/ana_gateC.png', dpi=110)
print('saved hera_scratch/ana_gateC.png')
