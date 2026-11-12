# sc-survey

The answer is a gate-space sweep on the zf1 toploader device looking for the
superconducting region: a two-gate map, an edge sweep, or a cut. Extract every
(V_tg, V_bg) point the sweep visits.

```json
{
  "status": "extracted",
  "V_tg": {"min": -7.0, "max": 6.0, "n": 105},
  "V_bg": {"min": -4.0, "max": 4.2, "n": 83},
  "points": null,
  "flags": [],
  "notes": "cell 32: megasweep(k_tg.volt, linspace(-7, 6, 105), k_bg.volt, linspace(-4, 4.2, 83))"
}
```

- For a grid (one gate per axis of a `megasweep`): `V_tg` and `V_bg` each as `{min, max, n}`.
  The scorer forms the outer product.
- For anything else (a diagonal cut, a `multisweep` of both gates together, a stitched set of
  segments): `points` as a list of `[V_tg, V_bg]` pairs, and leave `V_tg`/`V_bg` null. Compute
  the list with a scratch script from the cell's own expressions.
- Which gate is the top gate: `k_tg` (top) and `k_bg` (back) in this notebook's bindings; check
  the notebook's gate-bindings cell if the answer uses other names.
