import numpy as np, json
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
m=json.load(open("data/3/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d=np.loadtxt("data/3/data.tsv"); nfast=36
nr=d.shape[0]//nfast; print("interrupted:",m["interrupted"]," rows done:",nr,"/79  pts:",d.shape[0])
if nr<3: raise SystemExit("too few rows")
g=d[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci["magnet_mag"]]; I_bias=5e-9
n_vec=np.linspace(-1.4e12,-5.0e12,36)
print(f"B rows so far: {B[0]:.2f} -> {B[-1]:.2f} T")
print(f"drain I nA last row: med {np.median(g[-1,:,ci['sr0_X']]/(-1e6))*1e9:.2f}")
print(f"leak k_bg {np.abs(g[:,:,ci['k_bg_curr']]).max():.1e} k_2410 {np.abs(g[:,:,ci['k_2410_curr']]).max():.1e}")
# per-column FFT over the high-field rows available (B>=4)
def colfft(col):
    R=g[:,:,ci[col]]/I_bias  # (nr, nfast)
    out=[]
    for j in range(nfast):
        sel=B>=4.0
        if sel.sum()<8: out.append(np.nan); continue
        x=1/B[sel]; r=R[sel,j]; o=np.argsort(x); x,r=x[o],r[o]
        xu=np.linspace(x.min(),x.max(),1024); ru=np.interp(xu,x,r)
        ru=ru-np.polyval(np.polyfit(xu,ru,4),xu)
        F=np.fft.rfftfreq(1024,d=xu[1]-xu[0]); A=np.abs(np.fft.rfft(ru*np.hanning(1024)))
        k=(F>5)&(F<70); 
        out.append(F[k][np.argmax(A[k])])
    return np.array(out)
print(f"\nhigh-field rows used: {(B>=4).sum()} (dF_res~{1/(1/B[B>=4].min()-1/B[B>=4].max()):.0f} T)")
for col in ["sr1_X"]:
    Fpk=colfft(col)
    print(f"{col} dominant F(n) [T] vs full-density Luttinger:")
    for j in range(0,nfast,4):
        Flutt=abs(n_vec[j]*1e4)*6.62607e-34/(4*1.602177e-19)
        print(f"  n={n_vec[j]:+.2e}  F_peak={Fpk[j]:5.1f}  Luttinger_full={Flutt:5.1f}  ratio={Fpk[j]/Flutt:.2f}")
