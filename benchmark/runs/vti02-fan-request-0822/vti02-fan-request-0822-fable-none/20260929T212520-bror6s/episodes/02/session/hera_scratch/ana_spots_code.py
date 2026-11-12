"""sdh-spot-check read: runs 6 (electron, n=+3.2e12, B 0->10 T) + 7 (hole, n=-1.2e12, 10->0.3 T), D=0.
Raw R(B) first, then per-tone onset tracks (sdh_onset) and FFT in 1/B against the model expectations."""
from hera.analysis import sdh_onset

SPOTS = {6: ('electron', +3.2), 7: ('hole', -1.2)}
MODEL = {6: {'ABAB pair': (7.5, 25.6), 'ABCA': (33.1,)},   # step-2 model table, m* (0.028/0.061) / 0.074
         7: {'ABAB pair': (5.3, 7.1), 'ABCA': (12.4,)}}
fig, ax = plt.subplots(2, 3, figsize=(15, 8))
for row, (rid, (side, n12)) in enumerate(SPOTS.items()):
    r = run(rid)
    B = r.col('magnet_field')
    I = r.col('sr0_X') / -1e6
    R = np.abs(r.col('sr1_X') / I)
    o = np.argsort(B); B, R = B[o], R[o]
    F_L = float(luttinger_frequency(abs(n12) * 1e16))
    so = sdh_onset(R, B, r_full_scale=50e-6 / np.median(np.abs(I)))
    print(f"=== run {rid} ({side}, n = {n12:+.1f}e12, F_L = {F_L:.1f} T) ===")
    print(so.summary())
    print()
    a = ax[row, 0]; a.plot(B, R, lw=0.5, color='k')
    a.set_xlabel('B (T)'); a.set_ylabel('|Rxx| (Ohm)')
    a.set_title(f"run {rid} — {side} n = {n12:+.1f}e12 (raw)")
    m = B >= 1.2
    a = ax[row, 1]; a.plot(1 / B[m], R[m], lw=0.5, color='k')
    a.set_xlabel('1/B (1/T)'); a.set_title('vs 1/B (B > 1.2 T)')
    a = ax[row, 2]
    for blo, c in ((1.5, 'C0'), (2.5, 'C1')):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, 10.0), nfft=4096, log=False)
        a.plot(f, sp[0] / sp[0].max(), lw=0.8, color=c, label=f'FFT window B > {blo} T')
    for t in so.tones:
        if not (t.marginal or t.near_residual):
            a.axvline(t.freq, color='0.6', lw=0.6, zorder=0)
    for lbl, (fs, c) in zip(MODEL[rid], [(MODEL[rid]['ABAB pair'], 'g'), (MODEL[rid]['ABCA'], 'r')]):
        for fm in fs:
            a.axvline(fm, color=c, ls='--', lw=1)
        a.plot([], [], color=c, ls='--', label=f'{lbl}: {"/".join(f"{x:.1f}" for x in fs)} T')
    a.axvline(F_L, color='r', ls=':', lw=1)
    a.set_xlim(0, 45); a.set_xlabel('F (T)'); a.set_ylabel('FFT (norm.)')
    a.legend(fontsize=7); a.set_title('FFT in 1/B — tones (grey) vs model (dashed)')
fig.tight_layout(); plt.show()
