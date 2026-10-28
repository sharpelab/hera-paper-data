from hera.analysis import resolve_channels, current_channel, sdh_onset
from scipy.signal import find_peaks

def spot_plot(rid, n_label):
    r = run(rid)
    B = r.col('magnet_field')
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    vol = next(c for c in ch if c.cid == 'sr1')
    I = r.col(cur.col) / cur.gain
    V = r.col(vol.col) / vol.gain
    R = np.abs(V / I)
    print(summarize_run(r))
    print(f'raw: I {I.min()*1e9:.2f}–{I.max()*1e9:.2f} nA; V {V.min()*1e6:.3f}–{V.max()*1e6:.3f} µV; '
          f'|Rxx| {R.min():.1f}–{R.max():.1f} Ω; T {r.col("T_sample").min():.3f}–{r.col("T_sample").max():.3f} K')
    print(f'gate-current maxima: TG {np.abs(r.col("k_2400_tg_curr")).max()*1e12:.0f} pA, '
          f'BG {np.abs(r.col("k_2400_bg_curr")).max()*1e12:.0f} pA')
    fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    ax[0].plot(B, V*1e6, lw=.8); ax[0].set_ylabel('sr1 X / gain (µV)')
    ax[1].plot(B, I*1e9, lw=.8); ax[1].set_ylabel('measured drain current (nA)'); ax[1].set_xlabel('B (T)')
    fig.suptitle(f'data/{rid}: raw channels, {n_label}'); fig.tight_layout(); plt.show()
    f, spec = sdh_fft(R[:, None], B, b_range=(1.5, 10), nfft=2048, bg_degree=5, log=False)
    y = spec[0]
    pk, _ = find_peaks(y, prominence=y.max()*.08)
    top = sorted((p for p in pk if 2 < f[p] < 50), key=lambda p: y[p], reverse=True)[:6]
    print('FFT 1.5–10 T peaks (T, relative amplitude):', [(round(float(f[p]), 1), round(float(y[p]/y.max()), 2)) for p in top])
    fig, ax = plt.subplots(2, 1, figsize=(9, 6))
    ax[0].plot(B, R, lw=.8); ax[0].set_xlim(0, 10); ax[0].set_ylabel('|Rxx| (Ω)')
    ax[1].plot(f, y); ax[1].set_xlim(0, 45); ax[1].set_xlabel('SdH frequency (T)'); ax[1].set_ylabel('FFT amplitude')
    fig.suptitle(f'data/{rid}: resistance and 1/B spectrum'); fig.tight_layout(); plt.show()
    return B, R

B6, R6 = spot_plot(6, 'n_A ≈ +3.2×10¹² cm⁻²')
