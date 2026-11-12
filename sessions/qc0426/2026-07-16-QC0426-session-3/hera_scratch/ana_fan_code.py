# Run 9: raw fan + per-column FFT + continuity-tracked branches + Luttinger partition
from scipy.signal import find_peaks
import scipy.constants as cst

C_TG = cst.epsilon_0*3.0/15.6e-9; RATIO, N_OFF = 1.2839, -2.407e14
FLN = cst.h/(4*cst.e)*1e16
fan9 = fan_grids(run(9)); rg9 = resistance_grids(fan9)
B9 = fan9.slow[:fan9.nrows]
vtg9 = fan9.grid("k_2400_tg_volt")[0]; vbg9 = fan9.grid("k_2400_bg_volt")[0]
n9 = ((C_TG*vtg9 + RATIO*C_TG*vbg9)/cst.e + N_OFF)*1e-16

def track(ch):
    R = np.abs(rg9.R[ch])[:fan9.nrows]
    freqs, spec = sdh_fft(R, B9, b_range=(1.8, 8.0), bg_degree=5)
    sn = spec/(spec.max(axis=1, keepdims=True)+1e-30)
    pks = []
    for j in range(len(n9)):
        m = freqs > 3
        pk, pr = find_peaks(sn[j][m], height=0.10, prominence=0.05)
        pks.append((freqs[m][pk], pr["peak_heights"]))
    order = np.argsort(-np.abs(n9))
    fML = np.full(len(n9), np.nan); fBL = np.full(len(n9), np.nan)
    j0 = order[0]; FL0 = FLN*abs(n9[j0]); fp, hp = pks[j0]
    sB = (fp > 0.55*FL0) & (fp < 1.0*FL0); sM = (fp < 0.4*FL0) & (fp > 4)
    if sB.any(): fBL[j0] = fp[sB][np.argmax(hp[sB])]
    if sM.any(): fML[j0] = fp[sM][np.argmax(hp[sM])]
    for prev, j in zip(order[:-1], order[1:]):
        fp, hp = pks[j]
        if len(fp) == 0: continue
        sc = abs(n9[j])/abs(n9[prev])
        for arr in (fML, fBL):
            if np.isfinite(arr[prev]):
                pred = arr[prev]*sc
                c = np.abs(fp - pred) < np.maximum(2.5, 0.12*pred)
                if c.any(): arr[j] = fp[c][np.argmax(hp[c])]
    return freqs, sn, fML, fBL

freqs, sn1, fML, fBL = track("sr1")
fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
R1 = np.abs(rg9.R["sr1"])[:fan9.nrows]
pm = axes[0].pcolormesh(n9, B9, np.log10(np.clip(R1, 1, None)), shading="auto", cmap="inferno")
axes[0].set_xlabel("n (1e12)"); axes[0].set_ylabel("B (T)"); axes[0].set_title("log10 R_sr1")
plt.colorbar(pm, ax=axes[0])
axes[1].pcolormesh(n9, freqs, sn1.T, shading="auto", cmap="viridis")
axes[1].plot(n9, FLN*np.abs(n9), "w--", lw=1, label="F_L nominal")
axes[1].plot(n9, fML, "c.", ms=3, label="f_ML"); axes[1].plot(n9, fBL, "r.", ms=3, label="f_BL")
axes[1].set_ylim(0, 100); axes[1].set_xlabel("n (1e12)"); axes[1].set_ylabel("F (T)")
axes[1].set_title("per-column FFT + tracked branches"); axes[1].legend(fontsize=7)
ok = np.isfinite(fML) & np.isfinite(fBL)
lam = np.nansum((fML[ok]+fBL[ok])*np.abs(n9[ok]))/np.nansum(FLN*n9[ok]**2)
res = (fML[ok]+fBL[ok]) - lam*FLN*np.abs(n9[ok])
axes[2].plot(np.abs(n9[ok]), fML[ok]+fBL[ok], "ko", ms=4, label="f_ML+f_BL")
nn = np.linspace(0, 6.3, 40)
axes[2].plot(nn, FLN*nn, "b--", lw=1, label="F_L nominal")
axes[2].plot(nn, lam*FLN*nn, "r-", lw=1, label=f"λ·F_L, λ={lam:.3f}")
axes[2].set_xlabel("|n| (1e12)"); axes[2].set_ylabel("F (T)"); axes[2].legend(fontsize=7)
axes[2].set_title(f"Luttinger partition: rms {np.sqrt(np.mean(res**2)):.2f} T on {ok.sum()} cols")
fig.tight_layout()
print(f"sr1: lambda={lam:.4f}, partition rms {np.sqrt(np.mean(res**2)):.2f} T over {ok.sum()}/87 columns")
print(f"fan col at -6e12: fML={fML[-1]:.1f}, fBL={fBL[-1]:.1f} vs SC1 (uniform-B) 11.1/55.3 — grid-change check")
print(f"ML fraction: {np.nanmin(fML[ok]/(fML[ok]+fBL[ok])):.3f}..{np.nanmax(fML[ok]/(fML[ok]+fBL[ok])):.3f}")
