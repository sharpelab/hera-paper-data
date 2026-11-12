> From `bingcheng/NF02B1_dev00/NF02B1_dev00_measurement.ipynb` cells 41–55.

## 1.5T to 4.5 T sweep back and forth

### sweep to 1.5T

```python
smagneto.sweep(mag.field, spoints(0,1.5,151), delay=delay)
```

### sweep 1.5T -> 4.5T -> 1.5T (hysteresis)

```python
smagneto.sweep(mag.field, np.concatenate((spoints(1.5, 4.5, 301), spoints(4.5, 1.5, 301))), delay=delay)
```

```python
sleep(4000)
```

```python
smagneto.sweep(mag.field, np.concatenate((spoints(1.5, 4.5, 301), spoints(4.5, 1.5, 301))), delay=delay)
```

```python
smagneto.sweep(mag.field, spoints(1.5,0,151), delay=delay)
```

```python
mag.field()
```

```python
smagneto.reset()
```

```python
smagneto.sweep(mag.field, spoints(0.899,1,11), delay=delay)
```

```python
smagneto.sweep(mag.field, np.concatenate((spoints(1, -1, 201), spoints(-1, 0, 101))), delay=delay)
```

```python
mag.field()
```

```python
smagneto.reset()
```

```python
smagneto.sweep(mag.field, spoints(-0.45,0,46), delay=delay)
```

The Bingcheng-style Flavor B (single-file hstack) for the field axis. Two distinct hysteresis runs of the same gate-free orientation, with a `sleep(4000)` interlude between them — Bingcheng is testing whether the hysteresis loop is time-dependent over ~1 hour timescales (4000 s ≈ 67 min). The concatenation pattern `np.concatenate((spoints(1.5, 4.5, 301), spoints(4.5, 1.5, 301)))` is the direct equivalent of Aaron's `np.hstack((ns1, ns1[::-1]))` — forward (1.5 → 4.5 T, 301 points) then backward (4.5 → 1.5 T, 301 points) concatenated into a single 602-point sweep producing one file.

Notable departures from the Aaron mature form:
- **`sweep.Station` (synchronous), not `sweep.AsyncStation`.** Reused from cells 21–22 — this section inherits the Station built upfront for the entire angular survey.
- **No `s.add_comment` calls anywhere.** The recipe-tag lives in `meas_config["comment"]` from cell 21 (`"magnetoresistance at top loader base; theta = 0; phi = -55.74"`) which is static and section-wide — won't differentiate the 1.5–4.5 T loop from the cell 52 ±1 T loop. **This is a real loss** for downstream analysis; `comment_to_gates` cannot recover the loop's specific bounds. Recipe asks for `add_comment` going forward.
- **No gate ramps.** The device is held at a fixed gating condition for the entire angular survey — the loop is purely a function of field at this orientation.
- **`spoints(B_lo, B_hi, N)`** is Bingcheng's helper (not in `sharpelab_nb`) for building field traversal vectors. Functionally equivalent to `np.linspace`.
- **Cell 43 sweeps 0 → 1.5 T** as a setup move (positions the magnet at 1.5 T to start the hysteresis loop) — this is a single-direction sweep, *not* a hysteresis check. Same idiom Aaron uses at cell 42 of RPL_19/20260124. Cell 48 then does the reverse setup (1.5 → 0 T) after the hysteresis is done.
- **`smagneto.reset()`** between cells 50 and 51 (and again at 54 and 55) — Bingcheng resets the Station between distinct sub-runs even when reusing the same `meas_config`. Aaron's mature form keeps the same Station throughout (RPL_19/20260124 c41–53).
- **Cell 52 is a different hysteresis loop**: `np.concatenate((spoints(1, -1, 201), spoints(-1, 0, 101)))` — 1 → −1 → 0 T, an asymmetric loop that doesn't return to its starting point. The recipe consumer should know this is a *partial* hysteresis check (only one half of a full loop); a true check would be `np.concatenate((spoints(1, -1, 201), spoints(-1, 1, 201)))`.

The science context: NF02B1 is a Eu²⁺-doped material; Bingcheng's analysis (`NF02B1_dev00_analysis.ipynb` cell 21) interprets these hysteresis loops as evidence of magnetic-domain rearrangement at 1.5–4.5 T, distinct from purely orbital MR. The 4000 s wait between the two 1.5 → 4.5 → 1.5 T loops is the time-dependence check for that interpretation — domain configurations can relax slowly. This is the kind of physics question that requires single-file hstack hysteresis: any noise from rebuilding a Station between the forward and backward halves would obscure the small loop area.

The hysteresis is the science here, not a side-test — making this the cleanest example in the corpus of "hysteresis-check is the *primary* measurement, not a secondary check on something else." Recipe consumers writing rotator/magnetism code should treat this as the canonical pattern; recipe consumers in the (n, D) world should treat it as a constraint surface.
