import sys, warnings, numpy as np
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, sdh_onset, luttinger_frequency, fan_grids
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
I=1e-8
r=open_run("data/6"); B=r.col("magnet_field"); R=r.col("sr1_X")/I
for blo in (0.9,1.0):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on=sdh_onset(R,B,b_lo=blo,r_full_scale=5000); print(f"run6 b_lo={blo}:",on.summary()); [print("  W:",x.message) for x in w]
r7=open_run("data/7"); B7=r7.col("magnet_field"); R7=r7.col("sr1_X")/I
print("run7 R(0.3T)=%.0f  R max %.0f at %.2f T"%(R7[np.argmin(B7)],R7.max(),B7[np.argmax(R7)]))
print("run6 R(0T)=%.0f R(1T)=%.0f  max %.0f at %.2f T, min %.0f"%(R[np.argmin(B)],R[np.argmin(abs(B-1))],R.max(),B[np.argmax(R)],R.min()))
# D=0 line window
C=dict(c_tg=2.796e-03,c_bg=2.161e-03,n_offset=-0.0894,D_offset=-0.013)
ns=np.linspace(-2,4,6001); vt,vb=calc_gate_voltages(ns,0*ns,C["c_tg"],C["c_bg"],C["n_offset"],C["D_offset"])
ok=(vt>=-0.3)&(vt<=1.0)&(vb>=-1.3)&(vb<=2.0); print("D=0 n window: %.3f .. %.3f"%(ns[ok].min(),ns[ok].max()))
for n in (1.2,1.4,1.5,2.0,3.2,3.25): print(n, calc_gate_voltages(n,0,C["c_tg"],C["c_bg"],C["n_offset"],C["D_offset"]))
# zero-field R along D=0 from run 5
g=fan_grids("data/5"); print(type(g), [a for a in dir(g) if not a.startswith('_')])
