import numpy as np, json, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
import fs_count_b0 as M
RUN="data/3"; m=json.load(open(f"{RUN}/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
try: d=np.loadtxt(f"{RUN}/data.tsv.gz")
except OSError: d=np.loadtxt(f"{RUN}/data.tsv")
nfast=36; nr=d.shape[0]//nfast; g=d[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci["magnet_mag"]]; I_bias=5e-9; n_vec=np.linspace(-1.4e12,-5.0e12,nfast); absn=np.abs(n_vec)/1e12
sel=(B>=2.0)&(B<=8.0)
def spec(col,j,N=4096):
    x=1/B[sel]; r=g[sel,j,ci[col]]/I_bias; o=np.argsort(x); x,r=x[o],r[o]
    xu=np.linspace(x.min(),x.max(),N); ru=np.interp(xu,x,r); ru=ru-np.polyval(np.polyfit(xu,ru,6),xu)
    F=np.fft.rfftfreq(N,d=xu[1]-xu[0]); A=np.abs(np.fft.rfft(ru*np.hanning(N))); return F,A
F0,_=spec("sr1_X",0); fm=(F0>3)&(F0<70); Fax=F0[fm]
nn=np.abs(n_vec)*1e4; F_ml=[];F_bl=[];F_abc=[]
for x in nn:
    _,fs=M.aba_fs(x); fr=sorted(F for F,_ in fs)
    F_ml.append(fr[0] if len(fr)>=2 else np.nan); F_bl.append(fr[-1] if fr else np.nan); F_abc.append(M.abc_fs(x)[4])
F_ml=np.array(F_ml);F_bl=np.array(F_bl);F_abc=np.array(F_abc)
F_lutt=nn*6.62607e-34/(4*1.602177e-19); valid=np.abs(n_vec)<=3.5e12
fig,ax=plt.subplots(1,2,figsize=(14,5.5))
for k,col in enumerate(["sr1_X","sr2_X"]):
    SP=np.array([spec(col,j)[1][fm]/spec(col,j)[1][fm].max() for j in range(nfast)])
    ax[k].pcolormesh(absn,Fax,SP.T,shading="auto",cmap="inferno")
    ax[k].plot(absn[valid],F_lutt[valid],"w--",lw=1.6,label="full-density n·h/4e")
    ax[k].plot(absn[valid],F_bl[valid],"c:",lw=1.3,label="ABA BL (model)")
    ax[k].plot(absn[valid],F_ml[valid],"r:",lw=1.3,label="ABA ML (model, ~1-2 T)")
    ax[k].plot([4.0],[41.2],"co",ms=11,mfc="none",mew=2,label="go/no-go anchor 41.2 T")
    ax[k].set_xlabel("|n| (1e12 cm^-2)");ax[k].set_ylabel("F (T)");ax[k].set_ylim(0,70)
    ax[k].set_title(f"{col}: SdH FFT(n), D=0 (model valid |n|<=3.5)");ax[k].legend(fontsize=7,loc="upper left")
plt.tight_layout(); plt.savefig("hera_scratch/fan_figure.png",dpi=120); print("saved; rows",nr)
PY=0
