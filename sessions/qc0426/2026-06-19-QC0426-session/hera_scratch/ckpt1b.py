import numpy as np, os
from scipy.ndimage import gaussian_filter1d
d = "data/1"
cols = ['time','k_2400_volt','DC_bias','k_2400_curr','k_2410_curr','sr0_X','sr0_P','sr1_X','sr1_P','sr2_X','sr2_P','sr3_X','sr3_P']
raw = np.genfromtxt(os.path.join(d,"data.tsv"), delimiter="\t")
C = {c:raw[:,i] for i,c in enumerate(cols)}
bg = C['k_2400_volt']; tg = C['DC_bias']
I = C['sr0_X']/(-1e6)
R1 = C['sr1_X']/I; R2 = C['sr2_X']/I
ibg = C['k_2400_curr']; isi = C['k_2410_curr']

# group by BG row
rows = np.unique(np.round(bg,3))
print("BG rows present:", len(rows))
print("ridge V_tg per row (argmax smoothed R), expect slope ~ -1.3 (V_tg = -1.3*V_bg):")
ridge_bg=[]; ridge_tg1=[]
for b in rows:
    m = np.abs(bg-b)<1e-4
    if m.sum()<10: continue
    t = tg[m]; r1 = R1[m]; r2 = R2[m]
    order=np.argsort(t); t=t[order]; r1=r1[order]; r2=r2[order]
    i1=int(np.argmax(gaussian_filter1d(r1,2)))
    i2=int(np.argmax(gaussian_filter1d(r2,2)))
    clip1 = np.sum(r1>4.2e3)  # near rail count
    pred = -1.3*b
    print(f"  BG={b:+.2f}  sr1_CNP={t[i1]:+.2f} (clip_pts={clip1:2d})  sr2_CNP={t[i2]:+.2f}  | pred(-1.3*BG)={pred:+.2f}")
    ridge_bg.append(b); ridge_tg1.append(t[i1])
ridge_bg=np.array(ridge_bg); ridge_tg1=np.array(ridge_tg1)
if len(ridge_bg)>=3:
    p=np.polyfit(ridge_bg, ridge_tg1, 1)
    print(f"\nsr1 ridge fit: V_tg = {p[0]:+.3f}*V_bg + {p[1]:+.3f}  (slope=-c_bg/c_tg; geom prior -1.3)")
print(f"\nleakage: |I_bg|max={np.abs(ibg).max()*1e12:.0f} pA  |I_si|max={np.abs(isi).max()*1e12:.0f} pA")
print(f"drain I: {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA")
