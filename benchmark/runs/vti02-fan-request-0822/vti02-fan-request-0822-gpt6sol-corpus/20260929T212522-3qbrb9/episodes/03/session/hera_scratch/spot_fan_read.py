"""Run 6/7 raw and FFT read for the first D=0 Landau fan design."""
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft

for file_id, n in [(6, 3.2), (7, -1.2)]:
    run = open_run(f"data/{file_id}")
    b = run.col("magnet_field")
    current = run.col("sr0_X") / -1e6
    r = run.col("sr1_X") / current
    tg = run.col("k_2400_tg_curr")
    bg = run.col("k_2400_bg_curr")
    t = run.col("T_sample")
    print(f"RUN {file_id}: B {b[0]:.3f}->{b[-1]:.3f} T, R {np.nanmin(r):.1f}..{np.nanmax(r):.1f} ohm, "
          f"T {np.nanmin(t):.3f}..{np.nanmax(t):.3f} K, "
          f"I_tg med {np.nanmedian(tg)*1e12:.1f} pA, I_bg med {np.nanmedian(bg)*1e12:.1f} pA")
    try:
        onset = sdh_onset(r, b, r_full_scale=50e-6/10e-9)
        print(onset.summary())
    except Exception as exc:
        print(f"ONSET ERROR: {type(exc).__name__}: {exc}")
        onset = None
    for cutoff in [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]:
        if cutoff >= b.max()-1.5:
            continue
        freqs, spec = sdh_fft(r[:, None], b, b_range=(cutoff, float(b.max())), log=False, nfft=4096)
        power = spec[0]
        peaks, _ = find_peaks(power, prominence=np.max(power)*0.03)
        peaks = [p for p in peaks if 3 <= freqs[p] <= 45]
        peaks = sorted(peaks, key=lambda p: power[p], reverse=True)[:7]
        print(f"FFT {cutoff:.1f}-{b.max():.1f}: " + ", ".join(f"{freqs[p]:.2f} T ({power[p]:.1f})" for p in peaks))
