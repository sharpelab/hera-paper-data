# Spot-check analysis: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0
# Raw R(B), then sdh_onset tone read + FFT above onset.
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

BASE = '.'

def load(rid):
    r = open_run(f'data/{rid}')
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    I = r.col(cur.col) / 1.0  # fp gain-divided already at write time? NO: fp stores param()/gain only if gain passed.
    return r, chs, cur

for rid in (6, 7):
    r = open_run(f'data/{rid}')
    B = r.col('magnet_field')
    # columns written raw (fp without gain): apply gains from measurement_config
    mc = r.meta['measurement_config']
    g0 = mc['sr0_gain']
    I = r.col('sr0_X') / g0          # amps
    V = r.col('sr1_X') / 1.0         # sr1 gain 1
    Rxx = V / I
    print(f"--- run {rid}: {r.rows} rows, B {B[0]:+.3f} -> {B[-1]:+.3f} T, interrupted={r.interrupted}")
    print(f"    I median {np.median(np.abs(I))*1e9:.3f} nA; R(B~min) {Rxx[np.argmin(np.abs(B))]:.1f} ohm; "
          f"R range {np.nanmin(Rxx):.1f} .. {np.nanmax(Rxx):.1f} ohm")
    # full scale check: sens 50 uV, I_bias nominal 10 nA
    sens = 50e-6
    ib = np.median(np.abs(I))
    rfs = sens / ib
    print(f"    R full-scale ~ {rfs:.0f} ohm; max |V|/sens = {np.max(np.abs(V))/sens*100:.1f} %")

    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=False)
    ax[0].plot(np.abs(B), Rxx, lw=0.6)
    ax[0].set_xlabel('|B| (T)'); ax[0].set_ylabel('Rxx (ohm)'); ax[0].set_title(f'run {rid} raw Rxx(B)')

    try:
        so = sdh_onset(Rxx, np.abs(B), r_full_scale=rfs)
        print(so.summary())
        onset = so.onset_b
    except SdhOnsetError as e:
        print(f"    sdh_onset FAILED: {e}")
        onset = None

    # FFT over the high-field window
    blo = max(1.5, onset if onset else 3.0)
    fr, sp = sdh_fft(Rxx[:, None], np.abs(B), b_range=(blo, np.abs(B).max()), nfft=2048)
    sp1 = sp[0]
    ax[1].plot(fr, sp1, lw=0.8)
    ax[1].set_xlabel('F (T)'); ax[1].set_ylabel('FFT mag'); ax[1].set_xlim(0, 120)
    ax[1].set_title(f'run {rid} SdH FFT, B in [{blo:.1f}, {np.abs(B).max():.1f}] T')
    # top peaks
    from scipy.signal import find_peaks
    pk, props = find_peaks(sp1, height=np.max(sp1) * 0.05)
    order = np.argsort(props['peak_heights'])[::-1][:8]
    print("    FFT peaks (F [T], rel amp):",
          [(round(float(fr[pk[i]]), 1), round(float(props['peak_heights'][i] / sp1.max()), 2)) for i in order])
    fig.tight_layout()
    fig.savefig(f'hera_scratch/spot_run{rid}.png', dpi=110)
    plt.close(fig)
print("done")
