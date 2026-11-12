# Runs 6 & 7 — SdH tone read: matched-filter onset track + FFT in 1/B above 1.5 T
from hera.analysis import sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
from scipy.signal import find_peaks

F_L = {6: luttinger_frequency(3.2e16), 7: luttinger_frequency(1.2e16)}  # full-density Onsager (run-5 cal, geometry-prior scale)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, rid in zip(ax, (6, 7)):
    r = open_run(f'data/{rid}')
    B = np.abs(r.col('magnet_field'))
    mc = r.meta['measurement_config']
    Rxx = (r.col('sr1_X') / 1.0) / (r.col('sr0_X') / mc['sr0_gain'])
    rfs = 50e-6 / np.median(np.abs(r.col('sr0_X') / mc['sr0_gain']))
    try:
        so = sdh_onset(Rxx, B, r_full_scale=rfs)
        print(f"--- run {rid} (F_L full-density = {float(F_L[rid]):.1f} T)")
        print(so.summary())
    except SdhOnsetError as e:
        print(f"run {rid}: sdh_onset failed: {e}")
    fr, sp = sdh_fft(Rxx[:, None], B, b_range=(1.5, B.max()), nfft=2048)
    a.plot(fr, sp[0], lw=0.8)
    pk, pr = find_peaks(sp[0], height=sp[0].max() * 0.05)
    for i in np.argsort(pr['peak_heights'])[::-1][:6]:
        a.annotate(f"{fr[pk[i]]:.1f}", (fr[pk[i]], pr['peak_heights'][i]), fontsize=8)
    a.axvline(float(F_L[rid]), color='r', ls='--', lw=0.8, label=f'F_L = {float(F_L[rid]):.1f} T')
    a.set_xlim(0, 80); a.set_xlabel('F (T)'); a.set_ylabel('FFT mag'); a.legend()
    a.set_title(f'run {rid} SdH FFT, B 1.5-10 T')
fig.tight_layout()
