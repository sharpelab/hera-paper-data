import json, scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
def load(fid):
    g=run(fid); cfg=json.load(open(Path(file_path)/str(fid)/"metadata.json"))["measurement_config"]
    vtg=g.col("k_tg_volt"); vbg=g.col("k_bg_volt")
    I=g.col("sr830_1_X")/cfg["sr1_gain"]; X4=g.col("sr830_3_X")
    Rxx=(X4/cfg["sr3_gain"])/I
    n=((c_tg*vtg+c_bg*vbg)/cst.e+n_off)*1e-4
    D=(c_tg*vtg-c_bg*vbg)/(2*cst.epsilon_0)*1e-9
    return n,np.median(D),Rxx,(np.abs(X4)>2e-4*0.98)
fig,ax=plt.subplots(1,2,figsize=(13,4.8))
for fid,c in [(5,'C0'),(6,'C1'),(7,'C2')]:
    n,D,Rxx,clip=load(fid)
    for a in ax: a.plot(n/1e11,Rxx,'-',color=c,lw=1.3,label=f"run{fid} D={D:+.2f} V/nm")
    cand=(n<-4e11)&(n>-6e11)
    print(f"run{fid} D={D:+.2f}: candidate-band Rxx med={np.nanmedian(Rxx[cand]):.0f} min={np.nanmin(Rxx[cand]):.0f} Ω; "
          f"global min={np.nanmin(Rxx):.1f} Ω; deep-hole floor={np.nanmedian(Rxx[n<-7e11]):.0f} Ω")
ax[0].axvspan(-6,-4,color='cyan',alpha=.12); ax[0].set(xlabel="n (1e11 cm^-2)",ylabel="4T Rxx (Ω)",ylim=(-5,400),title="full: gap→CNP, metallic→deep hole")
ax[1].axvspan(-6,-4,color='cyan',alpha=.12,label='prior n band'); ax[1].set(xlabel="n (1e11 cm^-2)",ylabel="4T Rxx (Ω)",ylim=(0,60),xlim=(-8,-3),title="zoom: candidate band — no Rxx→0, ±D symmetric")
ax[0].legend(); ax[1].legend(); ax[1].axhline(0,c='gray',lw=.5); plt.tight_layout(); plt.show()
