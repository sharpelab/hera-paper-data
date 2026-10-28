import json
from scipy.ndimage import gaussian_filter1d
g=run(11); cfg=json.load(open(Path(file_path)/"11"/"metadata.json"))["measurement_config"]
vdc=g.col("dc205_1_voltage"); Idc=vdc/cfg["bias_resistor"]*1e9
dVdI=(g.col("sr830_3_X")/cfg["sr3_gain"])/(g.col("sr830_1_X")/cfg["sr1_gain"])
half=len(vdc)//2
I=Idc[:half]; R=gaussian_filter1d(dVdI[:half],1.5); o=np.argsort(I); I,R=I[o],R[o]
Rn=np.median(R[np.abs(I)>16]); th=0.3*Rn
icp=I[(I>0)][np.argmax(R[(I>0)]>th)]; neg=I[(I<0)][::-1]; icn=neg[np.argmax(R[(I<0)][::-1]>th)]
print(f"zero-bias dV/dI ~ {np.median(R[np.abs(I)<1.5]):.1f} Ω; normal ~ {Rn:.0f} Ω")
print(f"Ic (30% threshold): Ic+ = {icp:.1f} nA, Ic- = {icn:.1f} nA")
fig,ax=plt.subplots(figsize=(7.5,4.8))
ax.plot(Idc[:half],dVdI[:half],'.-',ms=3,label='forward')
ax.plot(Idc[half:],dVdI[half:],'.-',ms=3,alpha=.6,label='backward')
ax.axvspan(icn,icp,color='cyan',alpha=.12,label=f'|I|<Ic~{icp:.0f} nA')
ax.set(xlabel="I_dc (nA)",ylabel="dV/dI (Ω)",title="Run 11 — supercurrent at n=−5.02e11, D=−0.673, B=0")
ax.axhline(0,c='gray',lw=.5); ax.legend(); ax.grid(alpha=.3); plt.tight_layout(); plt.show()
