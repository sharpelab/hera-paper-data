import numpy as np, json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, sdh_fft, sdh_onset

base = Path("data")
for rid in (6, 7):
    r = open_run(base/str(rid))
    print("="*70); print("RUN", rid); print(summarize_run(r))
    print("cols:", r.cols)
    print("comments:", r.meta.get("comments"))
    mc = r.meta.get("measurement_config", {})
    print("mc:", {k: v for k, v in mc.items() if not isinstance(v, (dict, list))})
