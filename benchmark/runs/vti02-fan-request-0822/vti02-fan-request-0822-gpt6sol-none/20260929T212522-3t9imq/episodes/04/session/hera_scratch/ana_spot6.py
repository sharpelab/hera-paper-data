from hera.analysis import resolve_channels, current_channel, sdh_fft, sdh_onset
from scipy.signal import find_peaks

r6 = run(6)
ch6 = resolve_channels(r6.meta)
ic6 = current_channel(ch6)
vc6 = next(ch for ch in ch6 if ch.cid == 'sr1')
B6 = r6.col('magnet_field')
I6 = r6.col_at(ic6.idx) / ic6.gain
R6 = (r6.col_at(vc6.idx) / vc6.gain) / I6

fig, axs = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
axs[0].plot(B6, R6, lw=0.8); axs[0].set_ylabel('Rxx (Ω)'); axs[0].set_title('data/6 raw channels, B₁–B₂')
axs[1].plot(B6, I6*1e9, label='drain current'); axs[1].plot(B6, r6.col('T_sample'), label='T sample (K)'); axs[1].legend(); axs[1].set_ylabel('nA / K')
axs[2].plot(B6, r6.col('k_2400_tg_curr')*1e12, label='TG'); axs[2].plot(B6, r6.col('k_2400_bg_curr')*1e12, label='BG'); axs[2].legend(); axs[2].set_ylabel('gate current (pA)'); axs[2].set_xlabel('B (T)')
fig.tight_layout(); plt.show()
print(f'data/6: {r6.rows} points, {B6.min():.2f}–{B6.max():.2f} T, T median {np.median(r6.col("T_sample")):.3f} K, I median {np.median(I6)*1e9:.3f} nA, max |Rxx| {max(abs(R6)):.0f} Ω; max |I_TG| {max(abs(r6.col("k_2400_tg_curr")))*1e12:.0f} pA, max |I_BG| {max(abs(r6.col("k_2400_bg_curr")))*1e12:.0f} pA.')

sort6 = np.argsort(B6); bs6, rs6 = B6[sort6], R6[sort6]
fig, ax = plt.subplots(figsize=(9, 4))
for lo in (1.5, 3.0, 4.0):
    f, a = sdh_fft(rs6[:, None], bs6, b_range=(lo, 10), nfft=4096, bg_degree=5, log=False)
    ax.plot(f, a[0]/max(a[0]), label=f'{lo:g}–10 T')
    ok = (f > 2) & (f < 55)
    p, _ = find_peaks(a[0, ok], prominence=max(a[0, ok])*0.08)
    ii = np.where(ok)[0][p]
    ii = ii[np.argsort(a[0, ii])[-4:]][::-1]
    print(f'FFT {lo:g}–10 T: ' + ', '.join(f'{f[j]:.1f} T' for j in ii))
ax.set_xlim(0, 55); ax.set_xlabel('frequency (T)'); ax.set_ylabel('normalized FFT magnitude'); ax.legend(); ax.set_title('data/6: window dependence (B-space polynomial removed)')
fig.tight_layout(); plt.show()
try:
    print(sdh_onset(rs6, bs6, b_hi=10, b_lo=1.0, r_full_scale=50e-6/1e-8).summary())
except ValueError as exc:
    print('Onset unresolved:', exc)
