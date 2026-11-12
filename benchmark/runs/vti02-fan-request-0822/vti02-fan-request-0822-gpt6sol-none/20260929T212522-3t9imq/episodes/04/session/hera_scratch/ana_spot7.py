r7 = run(7)
ch7 = resolve_channels(r7.meta)
ic7 = current_channel(ch7)
vc7 = next(ch for ch in ch7 if ch.cid == 'sr1')
B7 = r7.col('magnet_field')
I7 = r7.col_at(ic7.idx) / ic7.gain
R7 = (r7.col_at(vc7.idx) / vc7.gain) / I7

fig, axs = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
axs[0].plot(B7, R7, lw=0.8); axs[0].set_ylabel('Rxx (Ω)'); axs[0].set_title('data/7 raw channels, B₁–B₂')
axs[1].plot(B7, I7*1e9, label='drain current'); axs[1].plot(B7, r7.col('T_sample'), label='T sample (K)'); axs[1].legend(); axs[1].set_ylabel('nA / K')
axs[2].plot(B7, r7.col('k_2400_tg_curr')*1e12, label='TG'); axs[2].plot(B7, r7.col('k_2400_bg_curr')*1e12, label='BG'); axs[2].legend(); axs[2].set_ylabel('gate current (pA)'); axs[2].set_xlabel('B (T)')
fig.tight_layout(); plt.show()
print(f'data/7: {r7.rows} points, {B7.min():.2f}–{B7.max():.2f} T, T median {np.median(r7.col("T_sample")):.3f} K, I median {np.median(I7)*1e9:.3f} nA, max |Rxx| {max(abs(R7)):.0f} Ω; max |I_TG| {max(abs(r7.col("k_2400_tg_curr")))*1e12:.0f} pA, max |I_BG| {max(abs(r7.col("k_2400_bg_curr")))*1e12:.0f} pA.')

sort7 = np.argsort(B7); bs7, rs7 = B7[sort7], R7[sort7]
fig, ax = plt.subplots(figsize=(9, 4))
for lo in (1.5, 2.0, 3.0):
    f, a = sdh_fft(rs7[:, None], bs7, b_range=(lo, 10), nfft=4096, bg_degree=5, log=False)
    ax.plot(f, a[0]/max(a[0]), label=f'{lo:g}–10 T')
    ok = (f > 2) & (f < 55)
    p, _ = find_peaks(a[0, ok], prominence=max(a[0, ok])*0.08)
    ii = np.where(ok)[0][p]
    ii = ii[np.argsort(a[0, ii])[-4:]][::-1]
    print(f'FFT {lo:g}–10 T: ' + ', '.join(f'{f[j]:.1f} T' for j in ii))
ax.set_xlim(0, 55); ax.set_xlabel('frequency (T)'); ax.set_ylabel('normalized FFT magnitude'); ax.legend(); ax.set_title('data/7: window dependence (B-space polynomial removed)')
fig.tight_layout(); plt.show()
try:
    print(sdh_onset(rs7, bs7, b_hi=10, b_lo=1.0, r_full_scale=50e-6/1e-8).summary())
except ValueError as exc:
    print('Onset unresolved:', exc)
