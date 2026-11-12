# Run 7 fan — per-column FFT, branch extraction, scale pin, model overlay (scratch)
import sys

sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\trilayer_fs_count")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from hera.analysis import fan_grids, resistance_grids, sdh_fft, sdh_onset, luttinger_frequency

fan = fan_grids("data/7")
rg = resistance_grids(fan)
print("channels:", list(rg.R.keys()) if hasattr(rg, "R") else dir(rg))
