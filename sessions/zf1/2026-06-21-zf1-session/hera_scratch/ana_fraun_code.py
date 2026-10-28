import json
from scipy.interpolate import griddata
def load(fid):
    g=run(fid); cfg=json.load(open(Path(file_path)/str(fid)/"metadata.json"))["measurement_config"]
    B=g.col("magnet_field")*1e3; Idc=g.col("dc205_1_voltage")/cfg["bias_resistor"]*1e9
    dVdI=(g.col("sr830_3_X")/cfg["sr3_gain"])/(g.col("sr830_1_X")/cfg["sr1_gain"])
    return B,Idc,dVdI
B=[];I=[];R=[]
for fid in (14,15):
    b,i,r=load(fid); B+=[b];I+=[i];R+=[r]
B=np.concatenate(B);I=np.concatenate(I);R=np.concatenate(R)
bi=np.linspace(-3,3,61); ii=np.linspace(-12,12,81); BB,II=np.meshgrid(bi,ii)
G=griddata((B,I),R,(BB,II),method='linear')
# zero-bias dV/dI vs B (the field null = min)
Bv=np.unique(B); zb=np.array([[b,np.median(R[(B==b)&(np.abs(I)<1)])] for b in Bv])
print(f"field null (min zero-bias dV/dI) at B={zb[np.nanargmin(zb[:,1]),0]:+.2f} mT")
fig,ax=plt.subplots(1,2,figsize=(13,4.8))
pc=ax[0].pcolormesh(bi,ii,np.clip(G,0,40),shading='auto',cmap='inferno')
ax[0].set(xlabel="B (mT)",ylabel="I_dc (nA)",title="dV/dI (Ω): central supercurrent lobe");plt.colorbar(pc,ax=ax[0])
ax[1].plot(zb[:,0],zb[:,1],'o-',ms=4); ax[1].set(xlabel="B (mT)",ylabel="zero-bias dV/dI (Ω)",title="field null & B_c⊥ closing"); ax[1].grid(alpha=.3); ax[1].axhline(0,c='gray',lw=.5)
plt.tight_layout(); plt.show()
