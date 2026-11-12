import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run

run = open_run("data/0")
tg   = run.col('DC_bias')
sr0X = run.col('sr0_X')
I    = sr0X / (-1e6)                 # drain current (A), Ithaco gain -1e6
ibias = 0.5/100e6                    # 5 nA nominal
R1 = run.col('sr1_X')/I             # T3-T4
R2 = run.col('sr2_X')/I             # B4-B5
R3 = run.col('sr3_X')/I             # T5-B6 Hall
ileak_bg = run.col('k_2400_curr')
ileak_si = run.col('k_2410_curr')

def cnp(tg, R):
    # smooth then argmax
    from scipy.ndimage import gaussian_filter1d
    Rs = gaussian_filter1d(R, 2)
    i = int(np.argmax(Rs))
    return tg[i], R[i], i

for nm, R in [('sr1 T3-T4', R1), ('sr2 B4-B5', R2)]:
    v, rmax, i = cnp(tg, R)
    edge = (i<=2 or i>=len(tg)-3)
    print(f'{nm}: CNP V_tg={v:+.3f} V  R_peak={rmax/1e3:8.2f} kOhm  edge_clipped={edge}')
print(f'Hall sr3 at CNP region: R3 range {R3.min()/1e3:.2f}..{R3.max()/1e3:.2f} kOhm')
print(f'I_drain: min {I.min()*1e9:.3f} nA  max {I.max()*1e9:.3f} nA  (Ibias~{ibias*1e9:.2f} nA)')
print(f'leakage |I_bg|max={np.abs(ileak_bg).max()*1e12:.1f} pA  |I_si|max={np.abs(ileak_si).max()*1e12:.1f} pA')
print(f'R1 metallic floor (away from CNP): {np.median(np.sort(R1)[:20])/1e3:.2f} kOhm')

fig, ax = plt.subplots(2,1, figsize=(7,7), sharex=True)
ax[0].plot(tg, R1/1e3, label='sr1 T3-T4')
ax[0].plot(tg, R2/1e3, label='sr2 B4-B5')
ax[0].plot(tg, R3/1e3, label='sr3 T5-B6 (Hall)', alpha=0.6)
ax[0].set_ylabel('R (kOhm)'); ax[0].legend(); ax[0].grid(alpha=0.3)
ax[0].set_title('QC0426 recon TG cut @ BG=0, Si=0, B=0 (run 0)')
ax[1].plot(tg, ileak_bg*1e12, label='BG leak')
ax[1].plot(tg, ileak_si*1e12, label='Si leak')
ax[1].plot(tg, I*1e9, label='I_drain (nA)', color='k', alpha=0.5)
ax[1].set_ylabel('I (pA) / I_drain(nA)'); ax[1].set_xlabel('V_tg (V)'); ax[1].legend(); ax[1].grid(alpha=0.3)
plt.tight_layout(); plt.savefig('hera_scratch/recon0.png', dpi=110)
print('saved hera_scratch/recon0.png')
