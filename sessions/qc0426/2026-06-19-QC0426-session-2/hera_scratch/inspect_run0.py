from hera.analysis import open_run, summarize_run
import numpy as np
r = open_run("data/0")
print(summarize_run(r))
print("interrupted:", r.interrupted)
print("cols:", list(r.cols))
