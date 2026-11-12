import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, plot_raw, sdh_fft, resolve_channels

file_path = Path('/home/hera/measurements/zack/20260822-vti-02/data')
def run(rid):
    return open_run(file_path / str(rid))

for rid in (6, 7):
    r = run(rid)
    print(summarize_run(r))
    plot_raw(r)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col('sr0_X') / ch['sr0'].gain
    R = (r.col('sr1_X') / ch['sr1'].gain) / I
    B = r.col('magnet_field')
    print(f'run {rid}: |Rxx| 10/50/90/max = {np.percentile(np.abs(R),[10,50,90,100]).round(1)} Ω; '
          f'I_drain {I.min()*1e9:.2f}–{I.max()*1e9:.2f} nA; '
          f'|I_tg| max {np.max(np.abs(r.col("k_2400_tg_curr")))*1e12:.0f} pA; '
          f'|I_bg| max {np.max(np.abs(r.col("k_2400_bg_curr")))*1e12:.0f} pA; '
          f'T {r.col("T_sample").min():.3f}–{r.col("T_sample").max():.3f} K')
    plt.show()
