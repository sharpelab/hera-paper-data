import json
from scipy.ndimage import gaussian_filter1d
rows=[]
for f in range(16,24):
    g=run(f); cfg=json.load(open(Path(file_path)/str(f)/"metadata.json"))["measurement_config"]
    hv=np.median(g.col("heater_volt")); ih=np.median(g.col("heater_curr"))
    Idc=g.col("dc205_1_voltage")/cfg["bias_resistor"]*1e9
    R=gaussian_filter1d((g.col("sr830_3_X")/cfg["sr3_gain"])/(g.col("sr830_1_X")/cfg["sr1_gain"]),1.5)
    o=np.argsort(Idc); I=Idc[o]; R=R[o]
    zb=np.median(R[np.abs(I)<1.0]); pos=I[I>0]; Rp=R[I>0]
    icp=pos[np.argmax(Rp>6)] if np.any(Rp>6) else np.nan
    rows.append((hv,hv*ih*1e3,zb,icp))
rows=np.array(rows)
Pa=np.array([0.0,4.5*0.39,6.5*0.70]); Ta=np.array([30.,250.,480.])     # device-card P->T anchors
T=np.interp(rows[:,1],Pa,Ta); o=np.argsort(T)
tc=np.interp(23,rows[o,2],T[o])
print(f"Tc (zero-bias dV/dI half-normal ~23Ω) ~ {tc:.0f} mK (coarse, power proxy)")
fig,ax=plt.subplots(1,2,figsize=(13,4.6))
ax[0].plot(T[o],rows[o,2],'o-',ms=5); ax[0].axhline(23,c='r',ls=':'); ax[0].axvline(tc,c='gray',ls=':',label=f'Tc~{tc:.0f}mK')
ax[0].set(xlabel="T (mK, device-card heater-power proxy)",ylabel="zero-bias dV/dI (Ω)",title="Rxx(0) vs T — SC collapse");ax[0].legend();ax[0].grid(alpha=.3)
ax[1].plot(T[o],rows[o,3],'o-',ms=5,color='C2');ax[1].set(xlabel="T (mK, proxy)",ylabel="Ic (nA)",title="Ic(T) collapse");ax[1].grid(alpha=.3);ax[1].axhline(0,c='gray',lw=.5)
plt.tight_layout(); plt.show()
