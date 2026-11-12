from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft, luttinger_frequency
from scipy.signal import find_peaks

out = Path('hera_scratch')
fig, ax = plt.subplots(3, 2, figsize=(12, 9))
records = []
for j, rid in enumerate((6, 7)):
    r = open_run(f'data/{rid}')
    channels = resolve_channels(r.meta)
    cc = current_channel(channels)
    vc = next(c for c in channels if c.cid == 'sr1')
    B = r.col('magnet_field')
    I = r.col(cc.col) / cc.gain
    V = r.col(vc.col) / vc.gain
    R = np.abs(V / I)
    order = np.argsort(B)
    B, R = B[order], R[order]
    records.append((rid, B, R))
    ax[0,j].plot(B, R, lw=.9)
    ax[0,j].set(ylabel='Raw |Vxx / I| (ohm)', xlabel='B setpoint (T)', title=f'Run {rid}: B_1 - B_2')
    ax[1,j].plot(r.col('magnet_field'), I*1e9, label='drain (nA)')
    ax[1,j].plot(r.col('magnet_field'), r.col('k_2400_tg_curr')*1e9, label='TG (nA)')
    ax[1,j].plot(r.col('magnet_field'), r.col('k_2400_bg_curr')*1e9, label='BG (nA)')
    ax[1,j].legend(); ax[1,j].set(xlabel='B setpoint (T)', ylabel='Current (nA)')
    ax[2,j].plot(r.col('magnet_field'), r.col('sr0_P'), label='sr0')
    ax[2,j].plot(r.col('magnet_field'), r.col('sr1_P'), label='sr1')
    ax[2,j].legend(); ax[2,j].set(xlabel='B setpoint (T)', ylabel='Phase (deg)')
    print(f'run {rid}: rows {r.rows}, interrupted={r.interrupted}, R={R.min():.2f}..{R.max():.2f} ohm, I={I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, max |Vxx|={abs(V).max()*1e6:.3f} uV, T={r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    print('max abs leakage pA:',*[float(abs(r.col(c)).max()*1e12) for c in ('k_2400_tg_curr','k_2400_bg_curr')])
    print('acquisition', {inst: {p: r.meta['instruments'][inst]['snapshot']['parameters'].get(p,{}).get('value') for p in ('amplitude','sensitivity','time_constant','filter_slope','nplci')} for inst in ('sr0','sr1','k_2400_tg','k_2400_bg')})
fig.tight_layout(); fig.savefig(out/'spots_raw.png', dpi=130); plt.show()
fig, ax = plt.subplots(2,2,figsize=(12,7))
for j, (rid, B, R) in enumerate(records):
    for lo in (1., 1.5, 2.):
        f, spec = sdh_fft(R[:,None], B, b_range=(lo,8.), nfft=4096)
        ax[0,j].plot(f, spec[0]/spec[0].max(), label=f'{lo:g}-8 T')
        peaks,_ = find_peaks(spec[0], prominence=.08*spec[0].max())
        print(f'run {rid}, FFT {lo:g}-8 T peaks:', sorted([(round(float(f[k]),2),round(float(spec[0,k]/spec[0].max()),2)) for k in peaks if f[k]<70],key=lambda p:-p[1])[:10])
    ax[0,j].set(xlim=(0,65),xlabel='Frequency (T)',ylabel='Normalized FFT',title=f'Run {rid}'); ax[0,j].legend()
    try:
        onset=sdh_onset(R,B,b_lo=.3,r_full_scale=5000.)
        print(f'run {rid}:',onset.summary())
        for tone in onset.tones:
            ax[1,j].plot(tone.b_centers,tone.snr,label=f'{tone.freq:.1f} T')
        ax[1,j].axhline(5,color='k',ls=':'); ax[1,j].legend()
    except ValueError as e:
        print(f'run {rid}: onset unresolved: {e}')
    ax[1,j].set(xlabel='B (T)',ylabel='Matched-filter SNR')
fig.tight_layout(); fig.savefig(out/'spots_sdh.png',dpi=130); plt.show()
