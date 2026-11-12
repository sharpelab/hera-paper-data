import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_fft, luttinger_frequency
file_path = "data"
def run(i): return open_run(Path(file_path) / str(i))
_show = plt.show
plt.show = lambda: plt.savefig("hera_scratch/sdh_spots_6_7.png", dpi=90)
exec(open("hera_scratch/ana_sdh_body.py").read())
