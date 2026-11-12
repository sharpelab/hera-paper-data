import json, numpy as np
B_lo = 1.0/np.arange(1/0.7, 1/3.6, -0.0115)
B_hi = np.linspace(3.74,10.0,43)
B=[float(x) for x in np.round(np.hstack(([0.0],B_lo,B_hi)),4)]
out={
 "status":"extracted","landed":"fan","form":"2d_megasweep","field_mode":"stitched",
 "B_values":B,
 "n_min_cm2":-1.25e12,"n_max_cm2":3.23e12,"n_columns":151,"D":0.0,
 "slow_axis":"B","slow_delay_s":5.0,"fast_delay_s":0.8,
 "lockins":[
  {"name":"sr0","sensitivity_V":0.02,"sensitivity_set_in_answer":False,"time_constant_s":0.3,"time_constant_set_in_answer":False},
  {"name":"sr1","sensitivity_V":1e-4,"sensitivity_set_in_answer":True,"time_constant_s":0.3,"time_constant_set_in_answer":False}],
 "gate_current_reads":[
  {"name":"k_2400_tg_curr","nplc":1.0,"nplc_set_in_answer":False},
  {"name":"k_2400_bg_curr","nplc":1.0,"nplc_set_in_answer":False}],
 "excitation_V":1.0,"bias_resistor_ohm":1e8,"n_fans":1,"stated_wall_clock_h":7.75,
 "flags":[],
 "notes":"Cell 48 (trailing code cell, markdown 47): s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtg_vec,Vbg_vec], slow_delay=5.0, fast_delay=0.8). Slow axis is a stitched 145-row vector np.round(np.hstack(([0.0], 1/np.arange(1/0.7,1/3.6,-0.0115), np.linspace(3.74,10.0,43))),4): a 0 T row, 101 uniform-1/B rows 0.7-3.590 T, then 43 rows at 0.149 T to 10 T. Fast axis n_vec = np.linspace(-1.25,3.23,151) in 1e12 cm^-2 at D=0 via calc_gate_voltages with the session's committed run-5 CAL (c_tg 2.796e-3, c_bg 2.161e-3, n_offset -0.0894, D_offset -0.013); the cell states the scale is still the geometry prior. Recorded lock-ins sr0 and sr1 (X,P): cell 48 sets sr1 sensitivity 100 uV; sr0 sens 0.02 V and both tau 0.3 s are inherited from the cell-44 close_out(restore=state0) printed readback. nplci 1/1 asserted (not set) in cell 48, matching that same readback. Drive 1.0 V at 13.777 Hz asserted in cell 48; 100 MOhm bias resistor from device_card.md:64. Headline 7 h 45 m stated in cell 47."
}
json.dump(out,open("/grade-run/output.json","w"),indent=1)
print("ok",len(B))
