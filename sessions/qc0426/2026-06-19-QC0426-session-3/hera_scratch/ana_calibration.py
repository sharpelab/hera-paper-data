import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, GateCalibration

run = open_run("data/1"); md = json.load(open("data/1/metadata.json"))
nbg, ntg = len(md["slow_setpoints"]), len(md["fast_setpoints"])
g = lambda n: np.asarray(run.col(n)).reshape(nbg, ntg)
BG, TG, I = g("k_2400_volt"), g("DC_bias"), g("sr0_X")/1e6
bg_axis, tg_axis = BG[:,0], TG[0,:]
R = {ch: g(f"{ch}_X")/I for ch in ("sr1","sr2","sr3")}
SAT = 2e-5/5e-9

def ridge(Rxx):
    pos=[]
    for i in range(nbg):
        rs=gaussian_filter1d(np.abs(Rxx[i]),2.0); sel=rs>=0.90*rs.max()
        pos.append(np.average(tg_axis[sel],weights=rs[sel]))
    return np.array(pos)

# averaged data-calibrated ratio + intercept (both Rxx agree)
ratios, intercepts = [], []
for ch in ("sr1","sr2"):
    p=np.polyfit(bg_axis, ridge(R[ch]),1); ratios.append(-p[0]); intercepts.append(p[1])
ratio=float(np.mean(ratios)); inter=float(np.mean(intercepts))

cal_geom = GateCalibration.from_thicknesses(15.6e-9,12e-9)
c_tg = cal_geom.c_tg                 # anchor TG at geometry prior
c_bg = ratio*c_tg                    # data-calibrated ratio
# choose n_offset so n=0 along the fitted CNP line. Use a tmp cal (n_off=0).
tmp = GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=0.0, D_offset=0.0)
ridge_tg = inter + (-ratio)*bg_axis
n_raw,_ = tmp.n_D(ridge_tg, bg_axis)
n_offset = -float(np.mean(n_raw))   # density() ADDS n_offset -> negate to put n=0 on the ridge
cal = GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_offset, D_offset=0.0)

# closure
n_clo, D_clo = cal.n_D(ridge_tg, bg_axis)
print(f"ratio c_bg/c_tg = {ratio:.4f} (geom 1.300)   intercept V_tg@bg0 = {inter:+.4f} V")
print(f"c_tg={c_tg:.4e}  c_bg={c_bg:.4e} F/m^2   n_offset={n_offset:.3e} m^-2")
print(f"closure: |n| along ridge max = {np.abs(n_clo).max():.3e} m^-2 (= {np.abs(n_clo).max()/1e16:.3e} e12 cm^-2)")
print(f"         D along ridge spans {D_clo.min()/1e9:+.3f} .. {D_clo.max()/1e9:+.3f} (1e9 V/m)")

# (n,D) for every grid point; metallic survey along D~0
ngrid, Dgrid = cal.n_D(TG, BG)
n12 = ngrid/1e16; Dnm = Dgrid/1e9
# realized n-window at D=0 within the box
mask0 = np.abs(Dnm) < 0.02
print(f"\nD~0 realized n-window: {n12[mask0].min():+.2f} .. {n12[mask0].max():+.2f} e12 cm^-2")

# metallic survey: R vs n along D~0 (bin) per channel
order = np.argsort(n12[mask0])
nn = n12[mask0][order]
fig, ax = plt.subplots(1,2, figsize=(13,4.6), constrained_layout=True)
for ch,c in (("sr1","C0"),("sr2","C1"),("sr3","C2")):
    rr=np.abs(R[ch])[mask0][order]/1e3
    ax[0].plot(nn, rr, ".", ms=3, color=c, label=ch, alpha=.6)
ax[0].set_yscale("log"); ax[0].set_xlabel("n (1e12 cm^-2) at D~0"); ax[0].set_ylabel("|R| (kΩ)")
ax[0].axvline(0,color="k",lw=.5); ax[0].legend(); ax[0].set_title("R vs n along D~0 (metallic survey)")
ax[0].grid(alpha=.3, which="both")
# (n,D) coverage of the box
sc=ax[1].scatter(n12.ravel(), Dnm.ravel(), s=1, c=np.clip(np.abs(R["sr1"]).ravel()/1e3,0,3), cmap="viridis")
ax[1].set_xlabel("n (1e12 cm^-2)"); ax[1].set_ylabel("D (1e9 V/m)"); ax[1].set_title("box coverage in (n,D), |R_sr1|")
ax[1].axhline(0,color="r",lw=.6); fig.colorbar(sc,ax=ax[1],label="|R| kΩ")
fig.savefig("hera_scratch/calibration_run1.png", dpi=110)

# metallic check at representative high |n| on each side (where spot checks will sit)
for nt in (-3.0, -2.0, 2.0, 3.0):
    sub = mask0 & (np.abs(n12-nt)<0.25)
    if sub.sum():
        print(f"  n~{nt:+.1f} D~0: sr1 {np.median(np.abs(R['sr1'])[sub]):6.0f}Ω  "
              f"sr2 {np.median(np.abs(R['sr2'])[sub]):6.0f}Ω  sr3 {np.median(np.abs(R['sr3'])[sub]):6.0f}Ω")
print("saved hera_scratch/calibration_run1.png")
