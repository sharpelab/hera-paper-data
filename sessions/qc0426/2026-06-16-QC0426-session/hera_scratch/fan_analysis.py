import numpy as np, json, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
import fs_count_b0 as M   # aba_fs(n_m2), abc_fs(n_m2)

RUN = "data/3"
m = json.load(open(f"{RUN}/metadata.json")); ci = {c:i for i,c in enumerate(m["columns"])}
try: d = np.loadtxt(f"{RUN}/data.tsv.gz")
except OSError: d = np.loadtxt(f"{RUN}/data.tsv")
nfast = 36; nr = d.shape[0]//nfast
g = d[:nr*nfast].reshape(nr, nfast, -1)
B = g[:,0,ci["magnet_mag"]]; I_bias = 5e-9
n_vec = np.linspace(-1.4e12, -5.0e12, nfast)
print(f"rows {nr}/79  B {B[0]:.2f}->{B[-1]:.2f} T  interrupted={m['interrupted']}")

BLO, BHI = 2.0, 8.0          # SdH-clean window (onset ~2 T)
sel = (B >= BLO) & (B <= BHI)
dFres = 1/(1/B[sel].min() - 1/B[sel].max()) if sel.sum() > 4 else np.inf
print(f"FFT window B[{BLO},{BHI}]: {sel.sum()} rows, dF_res ~ {dFres:.1f} T")

def col_peaks(col, detr=("poly",6), N=2048):
    R = g[:,:,ci[col]]/I_bias
    peaks_per_n = []
    for j in range(nfast):
        x = 1/B[sel]; r = R[sel,j]; o = np.argsort(x); x,r = x[o],r[o]
        xu = np.linspace(x.min(), x.max(), N); ru = np.interp(xu, x, r); dx = xu[1]-xu[0]
        ru = (ru - np.polyval(np.polyfit(xu,ru,detr[1]),xu)) if detr[0]=="poly" \
             else (ru - gaussian_filter1d(ru, detr[1]/dx))
        F = np.fft.rfftfreq(N, d=dx); A = np.abs(np.fft.rfft(ru*np.hanning(N)))
        k = (F>3)&(F<70); Fk,Ak = F[k], A[k]
        pk,_ = find_peaks(Ak, height=Ak.max()*0.25, distance=max(1,int(3/(F[1]-F[0]))))
        pk = pk[np.argsort(Ak[pk])[::-1]][:3]
        peaks_per_n.append(sorted(Fk[pk].tolist()))
    return peaks_per_n

# --- model-predicted curves (D=0) ---
nn = np.abs(n_vec)*1e4
F_ml=[]; F_bl=[]; F_abc=[]
for nm in nn:
    _,fs = M.aba_fs(nm); fr=sorted(F for F,_ in fs)
    F_ml.append(fr[0] if len(fr)>=2 else np.nan); F_bl.append(fr[-1] if fr else np.nan)
    F_abc.append(M.abc_fs(nm)[4])
F_ml=np.array(F_ml); F_bl=np.array(F_bl); F_abc=np.array(F_abc)
F_lutt = nn*6.62607e-34/(4*1.602177e-19)   # full-density line

fig, ax = plt.subplots(1, 2, figsize=(13,5))
for k,col in enumerate(["sr1_X","sr2_X"]):
    pks = col_peaks(col)
    # scatter all detected peaks
    for j,ps in enumerate(pks):
        for p in ps: ax[k].plot(abs(n_vec[j])/1e12, p, 'k.', ms=4)
    ax[k].plot(nn/1e16, F_abc, 'c-', label='ABC single (model)')
    ax[k].plot(nn/1e16, F_bl, 'm--', label='ABA BL (model)')
    ax[k].plot(nn/1e16, F_ml, 'r--', label='ABA ML (model)')
    ax[k].plot(nn/1e16, F_lutt, 'g:', label='full-density n·h/4e')
    ax[k].set_xlabel('|n| (1e12 cm^-2)'); ax[k].set_ylabel('F (T)')
    ax[k].set_title(f'{col} F(n) vs Onsager'); ax[k].legend(fontsize=7); ax[k].set_ylim(0,70)
plt.tight_layout(); plt.savefig("hera_scratch/fan_onsager.png", dpi=110)
print("saved hera_scratch/fan_onsager.png")

# Luttinger sum check (sum of detected peaks per column) for sr1
pks1 = col_peaks("sr1_X")
print("\nsr1 Luttinger: n[1e12]  sum(F_peaks)  F_full   ratio")
for j in range(0,nfast,5):
    s = sum(pks1[j]); print(f"  {n_vec[j]/1e12:+.2f}   {s:6.1f}     {F_lutt[j]:5.1f}   {s/F_lutt[j]:.2f}  peaks={['%.0f'%p for p in pks1[j]]}")
