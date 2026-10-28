import numpy as np, json, os
d="data/7"
meta=json.load(open(os.path.join(d,"metadata.json")))
cols=meta["columns"]; print("columns:", cols)
fast_sp=meta.get("fast_setpoints"); slow_sp=meta.get("slow_setpoints")
print("n_fast pts:", len(fast_sp[0]), " n_slow rows:", len(slow_sp[0]))
print("fast DC_bias[:3]:", np.round(fast_sp[0][:3],3), " ... unique?", "col0 dup:", abs(fast_sp[0][0]-fast_sp[0][1])<1e9)
raw=np.genfromtxt(os.path.join(d,"data.tsv"),delimiter="\t")
print("rows so far:", raw.shape)
idx={}; seen={}
for i,c in enumerate(cols):
    k=c if c not in seen else f"{c}.{seen[c]}"; seen[c]=seen.get(c,0)+1; idx[k]=i
# reshape: rows arrive as (slow_row, fast_pt). Group by unique k_2400_volt (fast)
Bcol=raw[:,idx['magnet_mag']]; vbg=raw[:,idx['k_2400_volt']]
I=np.abs(raw[:,idx['sr0_X']]/1e6); R2=raw[:,idx['sr2_R']]/I
nfast=len(fast_sp[0])
nrows_done=raw.shape[0]//nfast
print(f"complete slow-rows: {nrows_done} (each {nfast} fast pts)")
# assemble a fixed-n column: pick fast index for n=-5e12 (Vbg~-1.811)
target_vbg=-1.811; col_idx=int(np.argmin(np.abs(np.array(fast_sp[1])-target_vbg)))
print(f"n=-5e12 ~ fast col {col_idx} (Vbg={fast_sp[1][col_idx]:.3f})")
sel=np.arange(nrows_done)*nfast+col_idx
B_col=Bcol[sel]; R_col=R2[sel]
print(f"n=-5e12 column: {len(B_col)} pts, B {B_col.min():.2f}-{B_col.max():.2f}T, R2 {R_col.min():.0f}-{R_col.max():.0f} Ohm")
