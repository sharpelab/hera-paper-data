from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft, summarize_run
# Session-only disk input; this cell is independent of ana setup execution.
file_path = Path.cwd() / "data"
assert file_path.parent.name == "20260822-vti-02", file_path
for rid, n in [(6, 3.2), (7, -1.2)]:
    r = open_run(Path(file_path) / str(rid))
    print(summarize_run(r))
    plot_raw(r); plt.show()  # raw precedes every derived read
    chans = resolve_channels(r.meta)
    ci = current_channel(chans); cv = next(c for c in chans if c.cid == 'sr1')
    I = r.col(ci.col) / ci.gain
    R = (r.col(cv.col) / cv.gain) / I
    B = r.col('magnet_field')
    ix = np.argsort(B); B, R = B[ix], R[ix]
    print(f'R range {R.min():.2f} .. {R.max():.2f} Ohm; current {I.min()*1e9:.3f} .. {I.max()*1e9:.3f} nA')
    print('T bounds', r.col('T_sample').min(), r.col('T_sample').max())
    print('max |gate current| pA', {c: float(np.max(np.abs(r.col(c))) * 1e12) for c in ['k_2400_tg_curr', 'k_2400_bg_curr']})
    print('Full-record onset diagnostic (censoring/residual flags are binding):')
    on = sdh_onset(R, B, r_full_scale=5000)
    print(on.summary())
    if rid == 6:
        print('Restrict onset background fit below the large 8-10 T MR excursion:')
        for hi, degree in [(4,5), (5,4), (5,5)]:
            onset = sdh_onset(R, B, b_hi=hi, bg_degree=degree, r_full_scale=5000)
            print(f'B_hi={hi}, degree={degree}\n{onset.summary()}')
        cut = onset.onset_b
    else:
        cut = on.onset_b
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for degree in [3,5]:
        for cutoff in [cut, max(cut,1.0), max(cut,1.5)]:
            for window, axis in [('hann',ax[0]),('blackman',ax[1])]:
                f, spec = sdh_fft(R[:,None], B, b_range=(cutoff,10), bg_degree=degree, window=window, log=False, nfft=4096)
                norm = np.max(spec[0][(f>3)&(f<40)])
                axis.plot(f, spec[0]/norm, label=f'{cutoff:.2f}-10 T, deg {degree}', alpha=.7)
    for a,w in zip(ax,['Hann','Blackman']):
        a.axvline(abs(n)*10.33916924, color='k',ls=':',label='nominal F_L')
        a.set(xlim=(0,45),ylim=(0,1.4),xlabel='frequency (T)',ylabel='relative FFT magnitude',title=f'run {rid}: {w}')
        a.legend(fontsize=6)
    fig.tight_layout(); plt.show()
    print('Positive-field data only: no even-in-B symmetrization possible; Hall admixture remains a caveat.')
