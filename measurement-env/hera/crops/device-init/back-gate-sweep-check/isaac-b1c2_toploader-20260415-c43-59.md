> From `isaac/b1c2_toploader/20260415_measure.ipynb` cells 43–59.

# Gate test

## Bottom device

```python
meas_config = {
    "sr1" : "15 - 27",
    "sr1_gain" : -1e6,
    "sr2" : "14 - 18",
    "sr2_gain" : 1e2,
    "sr3" : "14 - 13",
    "sr3_gain" : 1e2,
    "sr4" : "6 - 4",
    "sr4_gain" : -1e6,
    "sr5" : "theta",
    "sr5_gain" : 1,
    "sr6" : "phi",
    "sr6_gain" : 1,
    "sr7" : "5 - 28",
    "sr7_gain" : 1e2,
    "sr8" : "28 - 30",
    "sr8_gain" : 1e2,
    "bias_resistor" : 1e8,
    "bias_voltage_1" : sr830_1.amplitude(),
    "lockin_freq_1" : sr830_1.frequency(),
    "bias_voltage_4" : sr830_4.amplitude(),
    "lockin_freq_4" : sr830_4.frequency(),
    "comment" : "bottom device",
}
```

```python
s = sweep.AsyncStation(meas_config)

s.fp(sr830_1.X).fp(sr830_1.P)
s.fp(sr830_2.X).fp(sr830_2.P)
s.fp(sr830_3.X).fp(sr830_3.P)
s.fp(sr830_4.X).fp(sr830_4.P)
s.fp(sr830_5.X).fp(sr830_5.P)
s.fp(sr830_6.X).fp(sr830_6.P)
s.fp(sr830_7.X).fp(sr830_7.P)
s.fp(sr830_8.X).fp(sr830_8.P)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(k_tg.volt).fp(k_tg.curr)


xp = k_bg.volt
s.plot(xp, k_bg.curr)
s.plot(xp, k_tg.curr)
s.plot(xp, sr830_4.X)
s.plot(xp, sr830_5.X)
s.plot(xp, sr830_8.X)
```

```python
k_bg.volt.vals = validators.Numbers(-4,4.4)
k_tg.volt.vals = validators.Numbers(-7,6)
```

```python
k_bg.nplci(10)
k_tg.nplci(10)
```

```python
s.sweep(k_bg.volt, np.linspace(-0.5, -4, 151), delay=0.4)
```

```python
s.sweep(k_bg.volt, np.linspace(-4, 4, 201), delay=0.4)
```

```python
s.sweep(k_bg.volt, np.linspace(4, 4.4, 51), delay=0.4)
```

```python
s = sweep.AsyncStation(meas_config)
...
xp = k_tg.volt
s.plot(xp, k_bg.curr)
s.plot(xp, k_tg.curr)
s.plot(xp, sr830_4.X)
s.plot(xp, sr830_5.X)
s.plot(xp, sr830_8.X)
```

```python
s.sweep(k_tg.volt, np.linspace(0, 6, 201), delay=0.4)
```

```python
s.sweep(k_tg.volt, np.linspace(6, -7, 201), delay=0.4)
```

```python
s = sweep.AsyncStation(meas_config)
...
xp = k_bg.volt
```

```python
# vtg -7, vbg f
s.sweep(k_bg.volt, np.linspace(0, 4.4, 101), delay=0.4)
```

```python
# vtg -7, vbg b
s.sweep(k_bg.volt, np.linspace(4.4, -4, 101), delay=0.4)
```

```python
s = sweep.AsyncStation(meas_config)
...
xp = k_tg.volt
```

```python
#vbg -4, vtg f
s.sweep(k_tg.volt, np.linspace(-7, 6, 201), delay=0.4)
```

```python
s.ramp(k_bg.volt, 0)
s.ramp(k_tg.volt, 0)
```

Isaac's "Bottom device" gate test on the dual-device chip. BG validator at ±4/4.4 V (cell 46) — much tighter than Aaron's RPL hBN devices because b1c2 has a different gate stack. Pattern: BG sweeps in three pieces (cells 48–50 cover −0.5 → −4, −4 → 4, 4 → 4.4 V — a stitched range to avoid running the full sweep in one go), then TG sweeps (cells 51–53), then BG sweeps at fixed V_tg=−7 (cells 54–56), then TG sweeps at fixed V_bg=−4 (cells 57–58). The post-TG BG cross-checks (cells 54–58) are a hysteresis/cross-bias spot check to validate that the TG sweep didn't shift the BG response. Inline comments like `# vtg -7, vbg f` document the operating point and direction (`f` = forward, `b` = backward). Cell content above is paraphrased where structurally identical to the first AsyncStation block to keep the crop manageable; full cells in the source.
