import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run
from scipy.ndimage import gaussian_filter1d

# device-card heater anchors: V -> T(mK); we map via measured POWER P=V*I
# anchors (V, T): 0->30, 4.5->250, 6.0->423, 6.5->480  (zf1 device card)
# build P-anchors using measured heater currents at those V (from the ladder)
rows=[]
for f in range(16,24):
    r=open_run(f"data/{f}"); cfg=json.load(open(f"data/{f}/metadata.json"))["measurement_config"]
    hv=np.median(r.col("heater_volt")); ih=np.median(r.col("heater_curr"))
    Idc=r.col("dc205_1_voltage")/cfg["bias_resistor"]*1e9
    dVdI=(r.col("sr830_3_X")/cfg["sr3_gain"])/(r.col("sr830_1_X")/cfg["sr1_gain"])
    o=np.argsort(Idc); I=Idc[o]; R=gaussian_filter1d(dVdI[o],1.5)
    zb=np.median(R[np.abs(I)<1.0])
    Rn=np.median(R[np.abs(I)>13]) if np.any(np.abs(I)>13) else np.nan
    # Ic at 6 Ohm threshold (fixed, since normal varies with T here)
    pos=I[I>0]; Rp=R[I>0]; icp=pos[np.argmax(Rp>6)] if np.any(Rp>6) else np.nan
    rows.append((hv, ih, hv*ih*1e3, zb, icp))   # V, I(A), P(mW), zerobias, Ic+
rows=np.array(rows)
# P->T anchors from device card (T at 4.5/6.0/6.5 V; P from this ladder's currents)
Pa=np.array([0.0, 4.5*0.39, 6.5*0.70]); Ta=np.array([30.,250.,480.])  # mW, mK (6.0 omitted; monotone)
T=np.interp(rows[:,2], Pa, Ta)
print("heaterV  P(mW)  T_proxy(mK)  zerobias_dVdI(Ω)  Ic+(nA)")
for (hv,ih,P,zb,icp),t in zip(rows,T):
    print(f"  {hv:.1f}    {P:.2f}   {t:6.0f}      {zb:6.1f}        {icp:.1f}")
# Tc: zero-bias dV/dI midpoint between SC(~1Ω) and normal(~45Ω) -> ~23Ω
zb=rows[:,3]; order=np.argsort(T); Ts=T[order]; Z=zb[order]
tc=np.interp(23, Z, Ts)
print(f"\nTc (zero-bias dV/dI = half-normal ~23Ω): ~{tc:.0f} mK (device-card power proxy; live sensor frozen)")
print(f"SC fully normal by heater 4.5V (~250 mK); SC robust at base (0.9Ω)")

fig,ax=plt.subplots(1,2,figsize=(13,4.8))
ax[0].plot(Ts,Z,'o-',ms=5); ax[0].axhline(23,c='r',ls=':',label='half-normal'); ax[0].axvline(tc,c='gray',ls=':',label=f'Tc~{tc:.0f}mK')
ax[0].set(xlabel="T (mK, device-card heater-power proxy)",ylabel="zero-bias dV/dI (Ω)",title="SC collapse: Rxx(0) vs T"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(Ts,rows[order,4],'o-',ms=5,color='C2'); ax[1].set(xlabel="T (mK, proxy)",ylabel="Ic (nA, 6Ω thr)",title="Ic(T) collapse"); ax[1].grid(alpha=.3); ax[1].axhline(0,c='gray',lw=.5)
plt.tight_layout(); plt.savefig("hera_scratch/tc.png",dpi=110); print("saved tc.png")
