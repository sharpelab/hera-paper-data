import json, scipy.constants as cst
c_tg=cst.epsilon_0*3/23.6e-9; c_bg=cst.epsilon_0*3/20e-9; n_off=-c_bg*0.0259/cst.e
def load(fid):
    g=run(fid); cfg=json.load(open(Path(file_path)/str(fid)/"metadata.json"))["measurement_config"]
    vtg=g.col("k_tg_volt"); vbg=g.col("k_bg_volt")
    I=g.col("sr830_1_X")/cfg["sr1_gain"]
    Rxx=(g.col("sr830_3_X")/cfg["sr3_gain"])/I
    n=((c_tg*vtg+c_bg*vbg)/cst.e+n_off)*1e-4
    return n, Rxx, cfg["bias_voltage_1"]/cfg["bias_resistor"]*1e9
fig,ax=plt.subplots(figsize=(7.5,4.5))
for fid,c in [(5,'C0'),(8,'C3')]:
    n,Rxx,InA=load(fid); ax.plot(n/1e11,Rxx,'-',color=c,lw=1.3,label=f"run{fid}  {InA:.2f} nA")
ax.axvspan(-6,-4,color='cyan',alpha=.12,label='prior n band')
ax.set(xlabel="n (1e11 cm^-2)",ylabel="4T Rxx (Ω)",ylim=(0,60),xlim=(-8,-2),
       title="D=−0.60 V/nm: 0.2 nA vs 1 nA — identical, no Rxx→0")
ax.legend(); ax.axhline(0,c='gray',lw=.5); plt.tight_layout(); plt.show()
