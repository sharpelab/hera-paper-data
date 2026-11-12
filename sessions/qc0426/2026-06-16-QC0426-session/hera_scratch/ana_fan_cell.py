import sys, json
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
import fs_count_b0 as M

# --- load fan (file_id 3); B[2,8] is the SdH-clean window (onset ~2 T) ---
mF = load_meta(3); fi = {c: i for i, c in enumerate(mF['columns'])}
try: dF = load1d(3)
except OSError: dF = np.loadtxt(f"{file_path}/3/data.tsv")
nfast = 36; nr = dF.shape[0]//nfast; gF = dF[:nr*nfast].reshape(nr, nfast, -1)
Bf = gF[:,0,fi['magnet_mag']]; I_bias = 5e-9
n_vec = np.linspace(-1.4e12, -5.0e12, nfast); absn = np.abs(n_vec)/1e12
sel = (Bf >= 2.0) & (Bf <= 8.0)
print(f"fan rows {nr}/79; SdH window B[2,8] {sel.sum()} rows; dF_res ~ {1/(1/Bf[sel].min()-1/Bf[sel].max()):.1f} T")

def spec(col, j, N=4096):
    x = 1/Bf[sel]; r = gF[sel, j, fi[col]]/I_bias; o = np.argsort(x); x, r = x[o], r[o]
    xu = np.linspace(x.min(), x.max(), N); ru = np.interp(xu, x, r)
    ru = ru - np.polyval(np.polyfit(xu, ru, 6), xu)
    F = np.fft.rfftfreq(N, d=xu[1]-xu[0]); A = np.abs(np.fft.rfft(ru*np.hanning(N))); return F, A

F0, _ = spec("sr1_X", 0); fm = (F0 > 3) & (F0 < 70); Fax = F0[fm]
nn = np.abs(n_vec)*1e4; F_bl=[]; F_ml=[]; F_abc=[]
for x in nn:
    _, fs = M.aba_fs(x); fr = sorted(F for F,_ in fs)
    F_ml.append(fr[0] if len(fr) >= 2 else np.nan); F_bl.append(fr[-1] if fr else np.nan); F_abc.append(M.abc_fs(x)[4])
F_ml=np.array(F_ml); F_bl=np.array(F_bl); F_lutt = nn*cst_h/(4*cst_e); valid = np.abs(n_vec) <= 3.5e12

fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
for k, col in enumerate(["sr1_X", "sr2_X"]):
    SP = np.array([spec(col,j)[1][fm]/spec(col,j)[1][fm].max() for j in range(nfast)])
    ax[k].pcolormesh(absn, Fax, SP.T, shading="auto", cmap="inferno")
    ax[k].plot(absn[valid], F_lutt[valid], "w--", lw=1.6, label="full-density n·h/4e")
    ax[k].plot(absn[valid], F_bl[valid], "c:", lw=1.3, label="ABA BL (model)")
    ax[k].plot(absn[valid], F_ml[valid], "r:", lw=1.3, label="ABA ML (model ~1-2 T)")
    ax[k].plot([4.0], [41.2], "co", ms=11, mfc="none", mew=2, label="go/no-go anchor 41.2 T")
    ax[k].set_xlabel("|n| (1e12 cm^-2)"); ax[k].set_ylabel("F (T)"); ax[k].set_ylim(0, 70)
    ax[k].set_title(f"{col}: SdH FFT(n), D=0 (model valid |n|<=3.5)"); ax[k].legend(fontsize=7, loc="upper left")
plt.tight_layout(); plt.show()
print("Go/no-go (file 2, n=-4e12): dominant 41.2 T = full-density Luttinger 41.4 T (detrender-stable).")
print("Fan: single dispersing branch tracks the full-density line; ABA-BL coincides with it (non-discriminating).")
print("ML discriminator (F~1-2 T) below SdH onset (~2 T), below dF_res (~2.7 T), thermally smeared (T_e~8 K) -> not resolvable.")
print("Constant-F ~5-9 T band does NOT disperse -> artifact, not a pocket. No 2nd dispersing branch resolved.")
