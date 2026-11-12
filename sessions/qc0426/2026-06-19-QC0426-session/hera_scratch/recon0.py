import numpy as np
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print("=== summary ===")
print(summarize_run(run))
print("=== cols ===")
print(list(run.cols))
