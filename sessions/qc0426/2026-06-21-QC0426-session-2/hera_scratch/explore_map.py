import numpy as np
from hera.analysis import fan_grids, resistance_grids

fan = fan_grids("data/1")
print("nrows", fan.nrows, "nfast", fan.nfast, "slow_param", fan.slow_param)
print("cols:", fan.cols)
VBG = fan.data["k_2400_volt"]   # slow
VTG = fan.data["DC_bias"]       # fast
print("VBG grid shape", VBG.shape, "row0 unique:", np.unique(VBG[0])[:3], "col const along fast?",
      np.allclose(VBG[:, 0], VBG[:, -1]))
print("VTG grid shape", VTG.shape, "VTG[0,:3]", VTG[0, :3], "VTG[0,-3:]", VTG[0, -3:])
print("VBG axis0 range:", VBG[:, 0].min(), VBG[:, 0].max())

rg = resistance_grids(fan)
print("type rg.R:", type(rg.R))
if isinstance(rg.R, dict):
    for k, v in rg.R.items():
        print("  R chan", k, "shape", np.shape(v), "absmax", np.nanmax(np.abs(v)))
else:
    print("  rg.R shape", np.shape(rg.R))
print("current_channel:", rg.current_channel)
