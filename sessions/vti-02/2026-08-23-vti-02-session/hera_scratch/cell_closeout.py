# HERA — close-out on operator ask: return-to-initial (field 0, gates 0 at committed pacing,
# heaters off, state0 acquisition restore, full readback)
from sharpelab_nb.closeout import close_out
print(f"pre: B={magnet.field():.4f} T (ramping={magnet.is_ramping()}) | V_tg={k_tg.volt():.3f} V_bg={k_bg.volt():.3f} "
      f"V_si={dc205.voltage():.3f} | ranges {heater.sample_range()}/{heater.vaporizer_range()} | "
      f"T_sample={T_sample():.2f} K T_vap={T_vaporizer():.2f} K")
close_out(
    field=(magnet.field, 0.0),
    restore=state0,                       # drive/sens/tau/slope on sr0-sr3, NPLC, and V_tg=V_bg=V_si=0 (captured at bring-up; Keithley step 5 mV, DC205 0.5 V/s)
    heaters=[("heater.off(both)", heater.off)],
    extra_readback={
        "T_sample": T_sample, "T_vaporizer": T_vaporizer,
        "sample_range": heater.sample_range, "vaporizer_range": heater.vaporizer_range,
        "B_readback": magnet.field,
    },
)
print(f"post: B={magnet.field():.4f} T | V_tg={k_tg.volt():.4f} V_bg={k_bg.volt():.4f} V_si={dc205.voltage():.4f} | "
      f"ranges {heater.sample_range()}/{heater.vaporizer_range()} | T_sample={T_sample():.2f} K T_vap={T_vaporizer():.2f} K")
