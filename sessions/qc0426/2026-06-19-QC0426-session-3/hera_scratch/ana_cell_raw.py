# Run 1 — 0 T gate map, RAW. Re-formed from the TSV (plot.png does not show the 2D map).
# R = V_xx / I, I = sr0_X/|gain 1e6|; sr1/sr2 = Rxx, sr3 = Rxy. Note: sr1/sr2 saturate at
# the CNP (sens 2e-5 -> ~4.37k ceiling) at the high-|D| ends; metallic flanks are tens of Ω.
import numpy as np, json
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

run = open_run("data/1"); md = json.load(open("data/1/metadata.json"))
print(summarize_run(run))
nbg, ntg = len(md["slow_setpoints"]), len(md["fast_setpoints"])
g = lambda n: np.asarray(run.col(n)).reshape(nbg, ntg)
BG, TG, I = g("k_2400_volt"), g("DC_bias"), g("sr0_X")/1e6
bg_axis, tg_axis = BG[:,0], TG[0,:]
R = {ch: g(f"{ch}_X")/I for ch in ("sr1","sr2","sr3")}
print("leakage |I_bg|max=%.2e  |I_si|max=%.2e A" % (np.abs(run.col("k_2400_curr")).max(),
                                                    np.abs(run.col("k_2410_curr")).max()))
fig, ax = plt.subplots(1,3, figsize=(15,4.4), constrained_layout=True)
for a,ch,lab in zip(ax,("sr1","sr2","sr3"),("sr1 T3-T4 Rxx","sr2 B4-B5 Rxx","sr3 T5-B6 Rxy")):
    im=a.pcolormesh(tg_axis,bg_axis,np.clip(np.abs(R[ch])/1e3,0,5),shading="auto",cmap="viridis")
    fig.colorbar(im,ax=a,label="|R| kΩ (clip@5)"); a.set_xlabel("V_tg (V)"); a.set_ylabel("V_bg (V)"); a.set_title(lab)
fig.suptitle("Run 1 — 0 T TG-BG gate map (raw, re-formed from TSV)")
plt.show()
