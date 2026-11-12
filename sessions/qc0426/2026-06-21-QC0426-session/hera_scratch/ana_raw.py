import os, numpy as np, hera.analysis as a
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance
MDIR = r"C:\Users\DGG\VTI_local_data\zack\20260621-QC0426"
run = a.open_run(os.path.join(MDIR, "data", "0"))
fg = a.fan_grids(run); rg = a.resistance_grids(fg)
Vbg = np.asarray(fg.slow); Vtg = fg.grid("DC_bias")[0, :]
ext = [Vtg.min(), Vtg.max(), Vbg.min(), Vbg.max()]
print("interrupted:", run.interrupted,
      "| leakage |I_bg|max=%.2e |I_si|max=%.2e A" % (
      np.abs(fg.grid('k_2400_curr')).max(), np.abs(fg.grid('k_2410_curr')).max()))
fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
for k, (cid, lab) in enumerate([("sr1","sr1 T3-T4 |Rxx|"),("sr2","sr2 B4-B5 |Rxx|"),("sr3","sr3 T5-B6 Rxy")]):
    R = rg.R[cid]
    if cid == "sr3":
        im = ax[k].imshow(R/1e3, origin="lower", aspect="auto", extent=ext, cmap="RdBu_r", vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax[k], label="Rxy (kOhm)")
    else:
        im = ax[k].imshow(np.abs(R)/1e3, origin="lower", aspect="auto", extent=ext, cmap="viridis",
                          vmax=np.nanpercentile(np.abs(R), 99)/1e3)
        plt.colorbar(im, ax=ax[k], label="|Rxx| (kOhm)")
    ax[k].set_xlabel("V_tg (DC_bias) [V]"); ax[k].set_ylabel("V_bg (k_2400) [V]"); ax[k].set_title(lab)
fig.suptitle("Run 0 RAW — 0 T TG-BG gate map (Vsi=0, 0.5 V/5 nA, B=0)"); fig.tight_layout(); plt.show()
