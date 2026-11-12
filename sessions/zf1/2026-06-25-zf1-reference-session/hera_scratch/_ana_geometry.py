# slot: geometry — gate-stack thicknesses (device card) + in-session (n,D) cal.
t_tg = 23.6e-9   # top-gate hBN thickness, m
t_bg = 20e-9     # back-gate hBN thickness, m
t_bgSiO2 = 0     # SiO2 term, m — zero for a graphite back gate

# Session gate calibration — run-4 CNP-ridge fit (cnp-and-dline-calibration):
# ratio data-pinned (c_tg/c_bg=0.844, agrees geometry prior 99.5%); absolute
# scale = geometry prior; n_offset shifts CNP -> n=0. USE EXACTLY (handoff §1).
N_OFF = -0.362e11 * 1e4   # m^-2
cal = GateCalibration.from_thicknesses(t_tg, t_bg, t_bgSiO2, n_offset=N_OFF)
# display units: n[1e11 cm^-2] = cal.n_D(Vtg,Vbg)[0]/1e4/1e11 ; D[V/nm] = [1]/1e9
