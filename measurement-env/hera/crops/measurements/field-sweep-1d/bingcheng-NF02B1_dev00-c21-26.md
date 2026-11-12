> From `bingcheng/NF02B1_dev00/NF02B1_dev00_measurement.ipynb` cells 21–26 (brief cited 25–26; recipe consumer needs the meas_config and Station setup at cells 21–22 to understand the surface).

## Theta = 0; Phi = 34.26  (parent section header at cell 18)

```python
meas_config = {
    "lia1" : "current",
    "lia2" : "B - D (28 - 22)",
    "lia3" : "D - E (6 - 21)",
    "lia4" : "E - F (7 - 10)",
    "lia1_gain" : 1e6, # ithaco gain ,
    "bias_resistor" : 1e8,
    "bias_voltage" : sr830_1.amplitude(),
    "lockin_freq" : sr830_1.frequency(),
    "comment" : "magnetoresistance at top loader base; theta = 0; phi = -55.74",
}
```

```python
smagneto = sweep.Station(meas_config)
smagneto.fp(mag_temperature).fp(fridge_temperature).fp(fridge_50mk_temperature).fp(still_temperature).fp(probe2_temperature)

smagneto.fp(sr830_1.X, gain=-1e6).fp(sr830_1.P)
smagneto.fp(sr830_2.X, gain=100).fp(sr830_2.P)
smagneto.fp(sr830_3.X, gain=100).fp(sr830_3.P)
smagneto.fp(sr830_4.X, gain=100).fp(sr830_4.P)


smagneto.plot('time', mag.field)
smagneto.plot(mag.field, [mag_temperature, probe2_temperature])
smagneto.plot(mag.field, sr830_1.X)
smagneto.plot(mag.field, sr830_2.X)
smagneto.plot(mag.field, sr830_3.X)
smagneto.plot(mag.field, sr830_4.X)

smagneto.plot(mag.field, [sr830_1.P, sr830_2.P, sr830_3.P, sr830_4.P])
```

```python
lia_vec = [sr830_1, sr830_2, sr830_3, sr830_4]
```

```python
delay = 3
```

```python
B_max, B_min, B_step = 12,-12, 0.005
time_constant = 1
delay = 3*time_constant
for lia in lia_vec:
    lia.time_constant(time_constant)
field_vec = calc_field_vec2(B_max, B_min, B_step, delay)
```

## 0T to 10T (header at cell 30 — but cell 26 below is the first long ±12 T traversal)

```python
smagneto.sweep(mag.field, field_vec, delay=delay)
```

The earliest example in the corpus of strict full-range 1D MR — Bingcheng's mode. Distinctive features:
- **`sweep.Station` (synchronous), not `sweep.AsyncStation`.** Bingcheng's rotator workflow doesn't benefit from async; the lock-in time constants and `delay=3*time_constant` give plenty of margin per point.
- **No `add_comment` calls.** The recipe-tag lives entirely in `meas_config["comment"]`. This survives in metadata but is static — once the Station is built, it can't be re-tagged mid-session. (Recipe asks for `add_comment` going forward.)
- **Gateless config.** `meas_config` enumerates lock-in roles (`"current"`, `"B - D (28 - 22)"`, etc.) but no gate channels — the device is held at one gating condition for the entire angular survey. No `s.ramp(k_tg.volt, ...)`.
- **`field_vec = calc_field_vec2(B_max, B_min, B_step, delay)`** — Bingcheng's helper builds the field traversal vector. Cell 25 sets `B_max, B_min, B_step = 12, -12, 0.005`, giving ~4801 points for a single ±12 T sweep at 5 mT step. With `delay=3`, that's ~4 hours wall-clock per sweep.
- **Temperature fingerprinting via 5 separate parameters** (`mag_temperature`, `fridge_temperature`, `fridge_50mk_temperature`, `still_temperature`, `probe2_temperature`) — Bingcheng's data layer has more thermometers than Aaron's because the rotator workflow needs to know which of several temperature sensors the device is actually equilibrating to.
- **Plot list explicitly labeled**: `smagneto.plot(mag.field, sr830_2.X)` for each contact pair, plus a multi-Phase combined plot at the end.

The `# Theta = 0; Phi = 34.26` header at cell 18 means this is the initial-orientation field sweep, before the systematic theta survey begins at cell 56. The hysteresis check at cells 41–55 (separate recipe `hysteresis-check`) sits between the two ±12 T sweeps and the systematic survey. The whole notebook is a series of `field-sweep-1d` calls at progressively-different rotator orientations — this first cell pair is the warmup.
