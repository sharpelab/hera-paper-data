import json
def load(fid):
    g=run(fid); cfg=json.load(open(Path(file_path)/str(fid)/"metadata.json"))["measurement_config"]
    B=g.col("magnet_field")*1e3
    Rxx=(g.col("sr830_3_X")/cfg["sr3_gain"])/(g.col("sr830_1_X")/cfg["sr1_gain"])
    return B, Rxx, g.col("T")*1e3
fig,ax=plt.subplots(1,2,figsize=(13,4.8))
allB=[]; allR=[]
for fid,lab,c in [(12,'+50→0','C0'),(13,'−50→0','C1')]:
    B,Rxx,T=load(fid); allB.append(B); allR.append(Rxx)
    ax[0].plot(B,Rxx,'.-',ms=3,color=c,label=lab); ax[1].plot(B,T,'.-',ms=2,color=c,label=lab)
B=np.concatenate(allB); R=np.concatenate(allR); o=np.argsort(B); B,R=B[o],R[o]
from scipy.ndimage import gaussian_filter1d
Rs=gaussian_filter1d(R,2); Rn=np.median(R[np.abs(B)>40])
half=Rn/2; bc=B[(B>0)][np.argmax(Rs[(B>0)]>half)] if np.any(Rs[(B>0)]>half) else np.nan
print(f"Rxx min={np.nanmin(R):.1f}Ω near B≈0; normal plateau={Rn:.0f}Ω; Bc⊥(half-normal)~{bc:.1f} mT")
import scipy.constants as cst
xi=(cst.h/(2*cst.e)/(2*np.pi*bc*1e-3))**0.5
print(f"xi ~ {xi*1e9:.0f} nm (order-of-magnitude, Hc2=Phi0/2pi xi^2)")
ax[0].set(xlabel="B (mT)",ylabel="Rxx (Ω)",title=f"B⊥ kill: Rxx {np.nanmin(R):.0f}→{Rn:.0f}Ω, Bc⊥~{bc:.0f}mT");ax[0].axhline(0,c='gray',lw=.5);ax[0].legend();ax[0].grid(alpha=.3)
ax[1].set(xlabel="B (mT)",ylabel="T (mK)",title="sample T — flat (no heating)",ylim=(30,38));ax[1].legend();ax[1].grid(alpha=.3)
plt.tight_layout(); plt.show()
