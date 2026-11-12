from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, plot_raw, resolve_channels, current_channel, sdh_onset, sdh_fft
for rid in (6,7):
    r=open_run(f'data/{rid}')
    plot_raw(r); plt.show()
exec(Path('hera_scratch/spot_analysis.py').read_text())
plt.show()
print('Verdict: B1-B2 is informative for fan design, but stacking remains unassigned. Electron n=3.2 has a roughly 7.3/14.7/22.2/29.4 T comb; harmonic versus distinct-pocket origins require n-dependence. Hole n=-1.2 is outside the preferred |n|>=2-3 design window and its close tones are ambiguous. No absent-pocket claim follows from these traces.')
print('Onset caveat: electron default sdh_onset is censored at 0.3 T; the coarse 50 mT grid below 1 T fails fastest-tone Nyquist. Higher background orders move the carrying onset to about 0.9 T. A short, adequately sampled extension is needed before pricing the fan. Neither trace is even-in-B; Hall admixture remains untested.')
