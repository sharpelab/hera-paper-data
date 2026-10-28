import numpy as np, pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from hera.analysis import open_run
c=pickle.load(open("hera_scratch/calib.pkl","rb"))
run=open_run("data/1")
bg=run.col('k_2400_volt'); tg=run.col('DC_bias'); I=run.col('sr0_X')/(-1e6)
R={'sr1 T3-T4':run.col('sr1_X')/I,'sr2 B4-B5':run.col('sr2_X')/I,'sr3 Hall':run.col('sr3_X')/I}
BG=np.unique(np.round(bg,3)); TG=np.unique(np.round(tg,3))
nb,nt=len(BG),len(TG)
def grid(v):
    g=np.full((nb,nt),np.nan)
    bi={b:i for i,b in enumerate(BG)}; ti={t:i for i,t in enumerate(TG)}
    for k in range(len(v)):
        g[bi[round(bg[k],3)], ti[round(tg[k],3)]]=v[k]
    return g
slope,intc,ratio=c['slope'],c['intc'],c['ratio']; vtgD0,bgD0=c['vtg_D0'],c['bg_D0']
cnp_tg=slope*BG+intc            # CNP line
d0_tg=vtgD0+ratio*(BG-bgD0)     # D=0 line
fig,ax=plt.subplots(1,3,figsize=(15,4.6),sharex=True,sharey=True)
for a,(nm,v) in zip(ax,R.items()):
    g=grid(v)/1e3
    im=a.pcolormesh(TG,BG,g,shading='nearest',cmap='inferno',
                    vmin=0,vmax=np.nanpercentile(g,98))
    a.plot(cnp_tg,BG,'c--',lw=1,label='CNP fit')
    a.plot(d0_tg,BG,'w:',lw=1,label='D=0')
    a.set_title(nm); a.set_xlabel('V_tg (V)'); a.set_xlim(-6,7); a.set_ylim(-4.5,4.5)
    plt.colorbar(im,ax=a,label='R (kOhm)')
ax[0].set_ylabel('V_bg (V)'); ax[0].legend(loc='lower left',fontsize=8)
plt.suptitle('QC0426 run1 0T gatemap (re-formed TSV) + CNP/D=0 overlays')
plt.tight_layout(); plt.savefig('hera_scratch/map1.png',dpi=105)

# channel health along D=0 line (metallic vs insulating away from CNP)
print("channel health along D=0 (median R over |n|>3e12 region):")
nval=run.col('sr1_X')  # placeholder
from hera.analysis import GateCalibration
cal=GateCalibration.from_thicknesses(c['t_tg'],c['t_bg_eff'],0.0,n_offset=c['n_offset'],D_offset=c['D_offset'])
nD=cal.density(tg,bg)
mask_hi=np.abs(nD)>3e16   # |n|>3e12 cm^-2
mask_D0=np.abs(cal.displacement_field(tg,bg))<2e7  # near D=0 band
for nm,v in R.items():
    sel=mask_hi&mask_D0
    rr=v[sel]
    print(f"  {nm}: along-D0 |n|>3e12  med={np.median(rr):.1f} Ohm  p95={np.percentile(rr,95):.1f} Ohm  (metallic if low/finite)")
print("saved map1.png")
