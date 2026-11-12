import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from hera.analysis import open_run, summarize_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

r = open_run('data/8')
print(summarize_run(r)); print('interrupted', r.interrupted)
itg=np.abs(r.col('k_tg_curr')).max(); ibg=np.abs(r.col('k_bg_curr')).max()
print(f'leakage max tg {itg:.2e} bg {ibg:.2e} A')

# planned gate setpoints = first occurrence of each name
tgi = r.col_indices('k_tg_volt'); bgi = r.col_indices('k_bg_volt')
Vtg = r.col_at(tgi[0]); Vbg = r.col_at(bgi[0])
R4 = (r.col('sr830_3_X')/100.0)/1e-9

c_tg=stack_capacitance([(23.6,3.0)]); c_bg=1.189*c_tg
n_off=-calc_nD(0.0,0.0895,c_tg,c_bg)[0]
n, D = calc_nD(Vtg, Vbg, c_tg, c_bg, n_offset=n_off)
n11 = n*10.0

print(f'\nR4: min {R4.min():.3f}  max {R4.max():.1f} Ohm  (sub-Ohm cells: {np.sum(R4<1)})')
# optimum = lowest-R cell
jm = np.argmin(R4)
print(f'OPTIMUM: R4 {R4[jm]:.3f} Ohm at n={n11[jm]:+.2f}e11, D={D[jm]:+.3f} V/nm  (Vtg={Vtg[jm]:+.2f}, Vbg={Vbg[jm]:+.2f})')
# how R_min varies with |D| (does it deepen toward the gate edge?)
print('\nR_xx vs D (min over n per D-bin):')
for Dlo in np.arange(-0.70,-0.44,0.04):
    m=(D>=Dlo)&(D<Dlo+0.04)
    if m.any(): print(f'  D~[{Dlo:.2f},{Dlo+0.04:.2f}]: R_min {R4[m].min():.2f}  R_med {np.median(R4[m]):.1f} Ohm')

fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))
tp=ax[0].tripcolor(n11, D, np.clip(R4,0.05,None), norm=LogNorm(0.1,200), cmap='inferno', shading='gouraud')
ax[0].plot(n11[jm], D[jm], 'c*', ms=16, label=f'opt R={R4[jm]:.2f}Ω')
ax[0].set(xlabel='n (1e11 cm^-2)', ylabel='D (V/nm)', title='4T R_xx zoom (n,D)  [log]'); ax[0].legend()
fig.colorbar(tp, ax=ax[0], label='R_xx (Ohm)')
tp2=ax[1].tripcolor(n11, D, np.clip(R4,0,60), cmap='viridis', shading='gouraud')
ax[1].plot(n11[jm], D[jm], 'r*', ms=16)
ax[1].set(xlabel='n (1e11 cm^-2)', ylabel='D (V/nm)', title='4T R_xx zoom (n,D)  [linear 0-60]')
fig.colorbar(tp2, ax=ax[1], label='R_xx (Ohm)')
plt.tight_layout(); plt.savefig('hera_scratch/zoom_nD.png', dpi=120)
print('saved hera_scratch/zoom_nD.png')
np.savez('hera_scratch/zoom.npz', n11=n11, D=D, R4=R4, Vtg=Vtg, Vbg=Vbg,
         opt_n=n11[jm], opt_D=D[jm], opt_Vtg=Vtg[jm], opt_Vbg=Vbg[jm])
