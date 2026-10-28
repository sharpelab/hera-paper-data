from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# --- go/no-go fixed-(n=-4e12, D=0) B-sweep, file_id 2 ---
mg = load_meta(2); gi = {c: i for i, c in enumerate(mg['columns'])}
dd = load1d(2)
Bg = dd[:, gi['magnet_mag']]; I_bias = 5e-9
n_gng = -4.0e12
F_tot = abs(n_gng*1e4)*cst_h/(4*cst_e)
print(f"go/no-go n={n_gng:.1e} cm^-2 -> Luttinger F_tot = {F_tot:.1f} T")

def sdh_spec(col, Blo, Bhi, detr, N=2048):
    sel = (Bg >= Blo) & (Bg <= Bhi); x = 1.0/Bg[sel]; R = dd[sel, gi[col]]/I_bias
    o = np.argsort(x); x, R = x[o], R[o]
    xu = np.linspace(x.min(), x.max(), N); Ru = np.interp(xu, x, R); dx = xu[1]-xu[0]
    osc = (Ru - np.polyval(np.polyfit(xu, Ru, detr[1]), xu)) if detr[0] == 'poly' \
          else (Ru - gaussian_filter1d(Ru, detr[1]/dx))
    F = np.fft.rfftfreq(N, d=dx); A = np.abs(np.fft.rfft(osc*np.hanning(N)))
    return F, A

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
for k, col in enumerate(['sr1_X', 'sr2_X']):
    for detr in [('poly', 6), ('poly', 8), ('gauss', 0.045)]:
        F, A = sdh_spec(col, 2.5, 7.95, detr)
        kk = (F > 3) & (F < 55); Fk, Ak = F[kk], A[kk]/A[kk].max()
        ax[k].plot(Fk, Ak, lw=0.9, label=f'{detr[0]}{detr[1]}')
        if detr == ('poly', 6):
            pk, _ = find_peaks(Ak, height=0.3, distance=10)
            print(f"{col} B[2.5,7.95] poly6 peaks[T]: "
                  f"{', '.join(f'{p:.1f}' for p in sorted(Fk[pk[np.argsort(Ak[pk])[::-1]][:3]]))}")
    ax[k].axvline(F_tot, color='g', ls='--', lw=0.8, label='Luttinger F_tot')
    ax[k].set_title(f'{col}  SdH FFT (B 2.5-7.95 T)'); ax[k].set_xlabel('F (T)')
    ax[k].set_ylabel('|FFT| (norm)'); ax[k].legend(fontsize=7)
plt.tight_layout(); plt.show()
print("Main tone (sr1) ~ Luttinger F_tot -> big BL/single tone, non-discriminating alone.")
print("Deciding read = fan F(n): main tone on vs below the full-density line (file_id 3).")
