from hera.analysis import resolve_channels, current_channel, sdh_fft

fig, axes = plt.subplots(2, 3, figsize=(15, 7), constrained_layout=True)
for row, rid in enumerate((6, 7)):
    r = run(rid)
    cs = resolve_channels(r.meta)
    ic = current_channel(cs)
    vc = next(ch for ch in cs if ch.cid == 'sr1')
    I = r.col(ic.col) / ic.gain
    R = np.abs((r.col(vc.col) / vc.gain) / I)
    B = r.col('magnet_field')
    order = np.argsort(B)
    B, R = B[order], R[order]
    axes[row, 0].plot(B, R, lw=0.65)
    axes[row, 0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title=f'data/{rid}: raw Rxx')
    sel = B >= 1.0
    axes[row, 1].plot(1/B[sel], R[sel], lw=0.65)
    axes[row, 1].set(xlabel='1/B (T⁻¹)', ylabel='|Rxx| (Ω)', title='raw versus 1/B')
    f, power = sdh_fft(R[:, None], B, b_range=(2, 10), nfft=2048, bg_degree=4)
    axes[row, 2].plot(f, power[0], lw=0.8)
    axes[row, 2].set(xlim=(0, 55), xlabel='frequency (T)', ylabel='FFT amplitude (a.u.)', title='2–10 T, detrended FFT')
    print(f'data/{rid}: {len(B)} points, B {B[0]:.2f}–{B[-1]:.2f} T, |Rxx| {R.min():.1f}–{R.max():.1f} Ω, median I {np.median(I)*1e9:.3f} nA; max |I_TG| {np.max(np.abs(r.col("k_2400_tg_curr")))*1e12:.0f} pA, max |I_BG| {np.max(np.abs(r.col("k_2400_bg_curr")))*1e12:.0f} pA')
plt.show()
