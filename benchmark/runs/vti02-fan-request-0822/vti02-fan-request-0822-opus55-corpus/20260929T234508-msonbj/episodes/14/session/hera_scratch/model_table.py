import sys; sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
from hera.analysis import luttinger_frequency
for n in [3.3, 3.2, 3.0, 2.5, 2.0, 1.5, 1.0, -0.6, -0.8, -1.0, -1.2]:
    FL = luttinger_frequency(abs(n)*1e16)
    ab = M.abab_fs(n*1e16)[1]; am = M.abab_mstar(n*1e16)
    ac = M.abca_mstar(n*1e16)
    print(f"n={n:+.1f}: F_L={FL:5.2f} | ABAB F=" + ",".join(f"{f:.2f}" for f,_ in ab) + " m*=" + ",".join(f"{m:.3f}" for _,m in am) + f" | ABCA F={ac[0]:.2f} m*={ac[1]:.3f}")
