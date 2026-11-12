# HERA — mandated close-out via the canonical helper, at the operator's instruction.
# close_out() replays state0 param-by-param in capture order, steps the named stages,
# then lands the field and prints a full readback.
from sharpelab_nb.closeout import close_out

print("pre: B = {:+.5f} T | V_tg = {:+.5f} | V_bg = {:+.5f} | V_si = {:+.5f}".format(
    magnet.field(), k_tg.volt(), k_bg.volt(), dc205.voltage()))
print("pre: sr1 sens = {:.3g} V, tau = {:g} s  (state0 will restore 2e-06 V / 0.3 s)".format(
    sr1.sensitivity(), sr1.time_constant()))
print(f"pre: T_sample = {T_sample():.3f} K  T_vaporizer = {T_vaporizer():.3f} K")
print()

close_out(
    (magnet.field, 0.0),          # explicit endpoint — never defaulted, never "hold"
    restore=state0,               # replays drive, all four lock-ins, NPLCs, V_tg/V_bg/V_si
    heaters=[
        (heater.sample_range, 0),
        (heater.vaporizer_range, 0),
    ],
    gates=[
        (k_2400_tg.volt, 0.0),
        (k_2400_bg.volt, 0.0),
    ],
    extra_readback={
        "T_sample": T_sample,
        "T_vaporizer": T_vaporizer,
        "leak_TG": k_2400_tg.curr,
        "leak_BG": k_2400_bg.curr,
        "psw": magnet.persistent_switch_on,
        "output": magnet.output_enabled,
    },
)
