import numpy as np, json, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    print(f"===== run {rid}"); print(summarize_run(r))
    print("cols", r.cols)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col(r.cols[1]) if r.cols[1] != 'magnet_field' else r.col_at(1)
    idx = r.col_indices('magnet_field'); print("field col idx", idx)
    Bset = r.col_at(1)
    I = r.col("sr0_X")/ch["sr0"].gain
    R = (r.col("sr1_X")/ch["sr1"].gain)/I
    print(f"I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; R {R.min():.1f}..{R.max():.1f} Ohm; itg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA; ibg {r.col('k_2400_bg_curr').min()*1e12:.0f}..{r.col('k_2400_bg_curr').max()*1e12:.0f}; T {r.col('T_sample').min():.3f}..{r.col('T_sample').max():.3f}")
    o = np.argsort(Bset); Bs, Rs = Bset[o], R[o]
    for b in [0.3,1,2,3,4,5,6,7,8,9,10]:
        k = np.argmin(abs(Bs-b)); print(f"  B={Bs[k]:.2f}  R={Rs[k]:.1f}")
    t = r.col("time"); print("duration h", (t.max()-t.min())/3600, "pts", len(t))
    ax[0,j].plot(Bs, Rs); ax[0,j].set_title(f"run {rid} R vs B"); ax[0,j].set_xlabel("B")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            so = sdh_onset(Rs, Bs, r_full_scale=50e-6/10e-9, b_lo=0.5)
        print(so.summary())
        for ww in w: print("WARN", ww.message)
    except Exception as e:
        print("sdh_onset error:", e)
    for k,(lo,hi) in enumerate([(2,10),(4,10)]):
        f, s = sdh_fft(Rs[:,None], Bs, b_range=(lo,hi), nfft=4096, bg_degree=5, log=True)
        s = s[0]
        m = f < 80
        ax[1+k,j].plot(f[m], s[m]); ax[1+k,j].set_title(f"run {rid} FFT {lo}-{hi} T"); ax[1+k,j].set_xlabel("F (T)")
        pk = np.argsort(s[m])[::-1]
        from scipy.signal import find_peaks
        p,_ = find_peaks(s[m]); p = p[np.argsort(s[m][p])[::-1]][:6]
        print(f"  FFT {lo}-{hi} T peaks:", ", ".join(f"{f[m][q]:.1f}T({s[m][q]:.3g})" for q in p), " dF~", 1/(1/lo-1/hi))
fig.tight_layout(); fig.savefig("hera_scratch/sdh67.png", dpi=90)
