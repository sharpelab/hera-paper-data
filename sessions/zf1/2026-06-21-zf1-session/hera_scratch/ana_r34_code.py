import json, scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
def load(fid):
    g=run(fid); cfg=json.load(open(Path(file_path)/str(fid)/"metadata.json"))["measurement_config"]
    vtg=g.col("k_tg_volt"); vbg=g.col("k_bg_volt")
    I=g.col("sr830_1_X")/cfg["sr1_gain"]; X4=g.col("sr830_3_X")
    Rxx=(X4/cfg["sr3_gain"])/I
    n=((c_tg*vtg+c_bg*vbg)/cst.e+n_off)*1e-4
    D=(c_tg*vtg-c_bg*vbg)/(2*cst.epsilon_0)*1e-9
    clip=np.abs(X4)>5e-6*0.98
    return n,D,Rxx,clip
fig,ax=plt.subplots(figsize=(7.5,4.5))
for fid,c in [(3,'C0'),(4,'C1')]:
    n,D,Rxx,clip=load(fid)
    ax.plot(n/1e11,Rxx,'.-',ms=3,color=c,label=f"run{fid} D={np.median(D):.2f} V/nm")
    ax.plot(n[clip]/1e11,Rxx[clip],'x',ms=4,color=c,alpha=.5)
    u=Rxx[~clip]; print(f"run{fid} D={np.median(D):+.2f}: clipped {clip.mean()*100:.0f}%, unclipped floor {np.nanmin(u):.1f} Ω")
ax.axhline(0,c='gray',lw=.5); ax.axhline(50,c='r',ls=':',lw=.8,label='clip ~50Ω')
ax.set(xlabel="n (1e11 cm^-2)",ylabel="4T Rxx (Ω)",ylim=(-5,80),title="n-linecuts (clipped): no Rxx→0 dip")
ax.legend(); plt.tight_layout(); plt.show()
