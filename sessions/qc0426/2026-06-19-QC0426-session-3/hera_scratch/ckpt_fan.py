# Mid-run fan checkpoint: re-form a few n-columns from the PARTIAL data.tsv (mid-write),
# FFT to confirm the two-pocket structure tracks F(n); check leakage from disk.
import numpy as np, json
from hera.analysis import sdh_fft, luttinger_frequency

md = json.load(open("data/4/metadata.json"))
cols = md["columns"]; print("cols:", cols)
ci = {c:i for i,c in enumerate(cols)}
NF = len(md["fast_setpoints"][0]) if isinstance(md["fast_setpoints"][0], list) else len(md["fast_setpoints"])
ns_set = np.array(md["fast_setpoints"][0]) if isinstance(md["fast_setpoints"][0], list) else None
print("N_fast:", NF)

# robust partial load: keep only complete fast-rows
rows = []
with open("data/4/data.tsv") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) == len(cols):
            try: rows.append([float(x) for x in p])
            except ValueError: pass
A = np.array(rows)
nB = len(A)//NF
A = A[:nB*NF].reshape(nB, NF, len(cols))
print(f"complete B-rows so far: {nB}  (B {A[0,0,ci['magnet_mag']]:.2f} -> {A[-1,0,ci['magnet_mag']]:.2f} T)")

B = A[:,0,ci["magnet_mag"]]
I = A[:,:,ci["sr0_X"]]/1e6
ngrid = np.array(md["fast_setpoints"])  # may be [[DC_bias...],[k_2400...]] — use designed n instead
# designed n per fast index (from the calibration used to build the fan):
c_tg,c_bg,n_off = 1.7027e-3,2.2004e-3,-1.581e15
Vtg = A[0,:,ci["DC_bias"]]; Vbg = A[0,:,ci["k_2400_volt"]]
n_des = (c_tg*Vtg + c_bg*Vbg)/1.602176634e-19 + n_off   # m^-2

# leakage from disk
print("leakage |I_bg|max=%.2e |I_si|max=%.2e A" % (np.abs(A[:,:,ci["k_2400_curr"]]).max(),
                                                    np.abs(A[:,:,ci["k_2410_curr"]]).max()))

lo, hi = 1.0, B.max()
print(f"FFT window [{lo},{hi:.2f}] T  dF~{1/(1/lo-1/hi):.1f} T")
# pick a few unclipped metallic columns
for n_t in (2.5e16, 3.5e16, 4.0e16):
    j = int(np.argmin(np.abs(n_des - n_t)))
    Rj = np.abs(A[:,j,ci["sr1_X"]]/I[:,j])
    if Rj.max() > 540:  # clipped
        print(f" n~{n_des[j]/1e16:.2f}e12: CLIPPED (maxR {Rj.max():.0f}) — skip"); continue
    f,P = sdh_fft(Rj[:,None], B, b_range=(lo,hi), detrend=5, window="hann", log=False); P=P[0]
    FL = float(luttinger_frequency(abs(n_des[j])))
    band=(f>2.5)&(f<1.4*FL); fb,Pb=f[band],P[band]; seen=[]
    for k in np.argsort(Pb)[::-1]:
        if all(abs(fb[k]-s)>2.5 for s in seen): seen.append(fb[k])
        if len(seen)>=3: break
    print(f" n~{n_des[j]/1e16:.2f}e12  F_L={FL:.1f}T  maxR={Rj.max():.0f}Ω  tones(T): "+", ".join(f"{s:.1f}" for s in sorted(seen)))
