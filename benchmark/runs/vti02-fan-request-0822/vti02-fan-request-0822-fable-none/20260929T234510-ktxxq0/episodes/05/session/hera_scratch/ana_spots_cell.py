"""Runs 6 & 7 — SdH spot checks at D = 0 (run-5 cal): raw R(B), then FFT in 1/B + tone onsets."""
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, luttinger_frequency)

SPOTS = [(6, +3.2e16, 'electron, n = +3.2e12 cm^-2'),   # n in SI m^-2 for luttinger_frequency
         (7, -1.2e16, 'hole, n = -1.2e12 cm^-2')]
fig, axs = plt.subplots(2, 3, figsize=(15, 8))
for (rid, n_si, lab), ax in zip(SPOTS, axs):
    r = open_run(f'data/{rid}')
    chs = resolve_channels(r.meta); cur = current_channel(chs)
    vch = next(c for c in chs if not c.is_current)
    B, I = r.col('magnet_field'), r.col(cur.col) / cur.gain
    R = (r.col(vch.col) / vch.gain) / I
    o = np.argsort(B); B, R = B[o], R[o]
    F_L = float(luttinger_frequency(abs(n_si)))
    # raw
    ax[0].plot(B, R, lw=0.6, color='k')
    ax[0].set(xlabel='B (T)', ylabel=r'$R_{xx}$ ($\Omega$)', title=f'run {rid}: {lab} — raw')
    m = B > 1.0
    ax[1].plot(1 / B[m], R[m], lw=0.6, color='k')
    ax[1].set(xlabel='1/B (1/T)', ylabel=r'$R_{xx}$ ($\Omega$)', title='vs 1/B (B > 1 T)')
    # FFT windows + onset read
    for b_lo, c in ((2.0, 'C0'), (4.0, 'C1'), (6.0, 'C3')):
        f, sp = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()))
        s1 = sp[0] / sp[0][f > 2].max()
        ax[2].plot(f, s1, c, lw=0.9, label=f'{b_lo:.0f}–{B.max():.0f} T')
    ax[2].axvline(F_L, color='0.5', ls='--', label=f'F_full = {F_L:.1f} T')
    ax[2].set(xlabel='F (T)', ylabel='norm |FFT|', xlim=(0, 60), title='SdH FFT in 1/B')
    ax[2].legend(fontsize=8)
    print(f'--- run {rid} ({lab}): F_full(4-fold) = {F_L:.1f} T ---')
    so = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
    print(so.summary(), '\n')
fig.tight_layout()
