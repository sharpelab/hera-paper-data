# Fan design numbers: onset from run 6 fine segment + model F(n) table + Nyquist/cost
import numpy as np
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError
import sys
sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as fs

run = open_run('/home/hera/measurements/zack/20260822-vti-02/data/6')
B = run.col('magnet_field'); order = np.argsort(B); B = B[order]
I = run.col('sr0_X')[order] / (-1e6)
R = run.col('sr1_X')[order] / np.abs(I)

m = B >= 1.0   # fine 10 mT segment only
try:
    on = sdh_onset(R[m], B[m], r_full_scale=5e-5/np.median(np.abs(I)))
    print(on.summary())
except SdhOnsetError as e:
    print('SdhOnsetError:', e)

# B-window split (low/high halves in 1/B) for the tone set
from scipy.signal import find_peaks
for lo, hi, tag in ((1.0, 10.0, 'full'), (1.0, 3.2, 'low-B'), (3.2, 10.0, 'high-B'), (1.0, 7.4, 'pre-QH')):
    freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(lo, hi), bg_degree=5)
    s = spec[0]
    ip, _ = find_peaks(s, height=0.02*s.max(), prominence=0.015*s.max())
    top = sorted(zip(s[ip], freqs[ip]), reverse=True)[:8]
    print(f'{tag} [{lo},{hi}]: ' + ', '.join(f'({a/s.max():.2f},{f:.1f}T)' for a, f in top))

# ---- model F(n): ABAB pair + ABCA singleton, electron side ----
print('\n n(e12)   F_L    ABAB tones (T)          m*(ABAB)        ABCA F_tot  m*(ABCA)')
for n12 in (1.0, 1.5, 2.0, 2.5, 3.0, 3.2, 3.3):
    n = n12 * 1e16   # m^-2
    FL = 6.62607e-34 / (4 * 1.602177e-19) * n
    ef, orbs = fs.abab_fs(n)
    ms = fs.abab_mstar(n)
    ftot_a, ms_a = fs.abca_mstar(n)
    orbs_s = ', '.join(f'{F:.1f}' for F, kf in orbs)
    ms_s = ', '.join(f'{mm:.3f}' for F, mm in ms)
    print(f'{n12:6.1f}  {FL:6.2f}   [{orbs_s}]   [{ms_s}]   {ftot_a:8.2f}  {ms_a:.3f}')

# ---- design arithmetic ----
h_4e = 6.62607e-34 / (4 * 1.602177e-19) * 1e4  # T per cm^-2
n_max = 3.2e12
F_fast = 33.1  # F_L at n_max (fastest credible tone incl. breakdown sum)
dinvB = 1/(3*F_fast)
print(f'\nDelta(1/B) <= 1/(3 F_L(n_max)) = {dinvB:.5f} /T')
for B_lo in (1.5, 2.0):
    print(f' B_lo={B_lo}: uniform-B step (Nyquist at low edge) dB = {dinvB*B_lo**2*1000:.1f} mT')
# n-axis: ray spacing at lowest read B: dn = 4 e/h * B
for Bl in (1.5, 2.0):
    dn = 4*Bl/ h_4e / 4  # careful: ray spacing = g e/h B = B/h_4e * ... compute directly
print('ray spacing dn = g*(e/h)*B =', 4*1.602177e-19/6.62607e-34*1.5/1e4/1e12, 'e12 at 1.5 T')
