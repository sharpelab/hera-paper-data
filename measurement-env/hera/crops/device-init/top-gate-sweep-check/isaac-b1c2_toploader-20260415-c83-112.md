> From `isaac/b1c2_toploader/20260415_measure.ipynb` cells 83–112.

# Gate test

## Top device

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
    "comment" : "top device",
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
s.plot(xp, sr830_1.X)
s.plot(xp, sr830_2.X)
s.plot(xp, sr830_3.X)
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
s.sweep(k_bg.volt, np.linspace(0, -4, 101), delay=0.4)
```

```python
s.reset()
```

```python
s.sweep(k_bg.volt, np.linspace(-2, 4, 201), delay=0.4)
```

```python
s.ramp(k_bg.volt, 0)
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


xp = k_tg.volt
s.plot(xp, k_bg.curr)
s.plot(xp, k_tg.curr)
s.plot(xp, sr830_1.X)
s.plot(xp, sr830_2.X)
s.plot(xp, sr830_3.X)
```

```python
s.sweep(k_tg.volt, np.linspace(0, 6, 201), delay=0.4)
```

```python
s.sweep(k_tg.volt, np.linspace(6, -7, 201), delay=0.4)
```

```python
s.ramp(k_tg.volt, -6)
```

```python
s = sweep.AsyncStation(meas_config)

s.fp(sr830_1.X).fp(sr830_1.P)
...
xp = k_bg.volt
s.plot(xp, k_bg.curr)
s.plot(xp, k_tg.curr)
s.plot(xp, sr830_4.X)
s.plot(xp, sr830_5.X)
s.plot(xp, sr830_8.X)
```

```python
# vtg -6, vbg f
s.sweep(k_bg.volt, np.linspace(0, 2, 101), delay=0.4)
```

```python
# vtg 0, vbg b
s.sweep(k_bg.volt, np.linspace(0, -4, 101), delay=0.4)
```

```python
# vtg 0, vbg f
s.sweep(k_bg.volt, np.linspace(-4, 4, 201), delay=0.4)
```

```python
s = sweep.AsyncStation(meas_config)
...
xp = k_tg2.volt
s.plot(xp, k_tg2.curr)
s.plot(xp, sr830_1.X)
s.plot(xp, sr830_2.X)
s.plot(xp, sr830_3.X)
```

```python
s.reset()
```

```python
# vtg 0, vbg f
s.sweep(k_tg2.volt, np.linspace(0, 4, 101), delay=0.4)
```

```python
# vtg 0, vbg b
s.sweep(k_tg2.volt, np.linspace(4, -4, 101), delay=0.4)
```

```python
s.ramp(k_tg2.volt, 0)
```

```python
s.ramp(k_bg.volt, 0)
s.ramp(k_tg.volt, 0)
```

### testing different config

```python
meas_config = {
    "sr1" : "15 - 27",
    ...
    "comment" : "top device, different sd",
}
```

(Cells 107–112 repeat the BG sweeps with a different source–drain pairing, mirroring the structure above.)

Isaac's b1c2 is a dual-device chip; "Top device" gates both `k_tg` (primary top gate) and `k_tg2` (a second top gate), and the section also runs back-gate sweeps for the same device because the gate ranges are validated together. The TG-only subset is c92–95 (`k_tg`, ±6/−7 V validator) and c100–105 (`k_tg2`, ±4 V); the rest of the cited range is BG cross-checking. `meas_config` is a plain dict with `sr_*_gain` and `bias_resistor` baked in (no `mc_N` convention; no `add_comment`). Cell content above is paraphrased where structurally identical to the first AsyncStation block to keep the crop manageable; full cells in the source.
