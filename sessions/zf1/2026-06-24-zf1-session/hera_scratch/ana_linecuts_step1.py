"""Step-1 locate: analyze constant-D n-linecuts (data/5-8) for an SC dip."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

c_tg = stack_capacitance([(23.6,3)]); c_bg = c_tg*1.1833
n_off = -calc_nD(0.1634,0.0,c_tg,c_bg)[0]
runs = {5:-0.7, 6:-0.6, 7:-0.5, 8:+0.5}

fig, ax = plt.subplots(figsize=(9,5))
for rid, D0 in runs.items():
    try:
        r = open_run(f"data/{rid}")
    except Exception as e:
        print(f"data/{rid}: {e}"); continue
    vtg = r.col_at(r.col_indices("k_tg_volt")[0])
    vbg = r.col_at(r.col_indices("k_bg_volt")[0])
    R4 = (r.col_at(r.col_indices("sr830_3_X")[0])/100.0)/1e-9
    itg = np.abs(r.col("k_tg_curr")); ibg = np.abs(r.col("k_bg_curr"))
    n, D = calc_nD(vtg, vbg, c_tg, c_bg, n_offset=n_off)
    o = np.argsort(n)
    kmin = int(np.argmin(R4))
    print("D=%+.2f (data/%d): R4 min=%.2f ohm at n=%.3f (Vtg=%.2f Vbg=%.2f);  R4 med=%.1f  range[%.1f,%.1f];  leak |Itg|%.0fpA |Ibg|%.0fpA"
          % (D0, rid, R4[kmin], n[kmin], vtg[kmin], vbg[kmin], np.median(R4), R4.min(), R4.max(),
             itg.max()*1e12, ibg.max()*1e12))
    ax.plot(n[o], R4[o], ".-", ms=3, label=f"D={D0:+.2f} (run {rid})")
ax.axvspan(-0.6,-0.4, color="k", alpha=0.07, label="prior n band")
ax.set_xlabel("n (e12 cm^-2)"); ax.set_ylabel("4T Rxx (ohm)")
ax.set_title("Step-1 locate: constant-D n-linecuts"); ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("hera_scratch/linecuts_step1.png", dpi=120)
print("saved hera_scratch/linecuts_step1.png")
