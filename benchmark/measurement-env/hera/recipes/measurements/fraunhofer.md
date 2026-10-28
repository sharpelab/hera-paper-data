# Fraunhofer (Ic vs B-perpendicular)

## What
2D map of differential resistance $dV/dI$ as a function of DC bias current $I_{dc}$ and perpendicular magnetic field $B_{\perp}$, at a fixed operating point (fixed $n, D$).
```python
s.megasweep(mag.field, B_vec, dc205_1.volt, Vdc_vec, fast_delay=1, slow_delay=3)
```
In a Josephson junction or proximity-coupled superconductor, the critical current $I_c$ is modulated by the magnetic flux through the junction. This produces an interference pattern—the **Fraunhofer pattern**—where $I_c$ reaches a maximum at zero effective field and exhibits periodic lobes as the field is swept.

## When
- **SC confirmation** — after finding a low/zero-resistance dome and observing a finite $I_c$ in bias spectroscopy. A clean Fraunhofer pattern is consistent with phase-coherent (Josephson) transport; its absence does not rule out superconductivity — many SC samples show no clean pattern (wide or non-uniform junctions, non-Josephson geometry).
- **Junction characterization** — the shape and periodicity of the lobes constrain the spatial distribution of the supercurrent (e.g., uniform junction vs. edge-dominated SQUID-like interference), though this interpretation breaks down for a disordered junction.
- **Finding the Field Null** — identifying the exact $B_{eff}=0$ point (compensating for trapped flux in the magnet or the sample's own magnetic history).

Prerequisites: A candidate SC state at $(n, D)$ with a finite $I_c$ measured in bias spectroscopy ($V_{dc}$ range known), and a magnet capable of mT-scale steps.

## Why
A "supercurrent-like" low/zero-resistance dome at $B=0$ can sometimes be mimicked by experimental artifacts or ballistic transport. Modulation of the critical current by a small field ($< 100$ mT), periodic in the flux through the junction, is characteristic of phase-coherent (Josephson) transport.
- **Single Junction**: $I_c(B)$ follows a sinc-like $|\sin(x)/x|$ envelope.
- **SQUID / 2-Path Interference**: a symmetric SQUID gives $|\cos(\pi\Phi/\Phi_0)|$ oscillations that modulate fully to zero; rapid oscillations riding on a non-vanishing baseline indicate an asymmetric SQUID.
- **Lobe Spacing**: $\Delta B$ relates to the junction area $A$ via the flux quantum: $\Delta B \cdot A = \Phi_0$.

## Recipe
1. **Map the dome vs field, then pick a candidate**:
   - Take a line cut across the widest part of the SC dome and run a density-vs-$B_\perp$ sweep (density as the fast axis, $B_\perp$ slow) to see how the low/zero-resistance region evolves with field.
   - Bound the field range by the perpendicular critical field: sweep up to (and just above) $H_c$, where the dome closes — no need to go higher.
   - This map can be coarse: field steps several times larger than $\Phi_0/A_{\rm device}$ are fine — you're locating where modulation might appear, not resolving lobes yet (that comes in the fine bias-vs-$B$ sweep at the candidate).
   - From that map, pick a candidate density where the region looks like it may modulate with field; if no obvious oscillations appear, pick the density where $H_c$ is highest. Fix $(V_{tg}, V_{bg})$ there for the bias-vs-field sweep below.
2. **Setup the Field Window**:
   - Choose the field step to resolve the expected lobe period $\Delta B = \Phi_0/A$ — a few points per lobe.
   - **Caution**: Trapped flux in superconducting magnets can shift the pattern by several mT.
3. **Configure the Sweep**:
   - **Fast Axis**: DC Bias (e.g., `dc205_1.volt`). Use a range that safely brackets the expected $I_c$.
   - **Slow Axis**: Magnetic field (`mag.field`).
   - **Settle Time**: Let the field settle at each step (`slow_delay` ≈ 3s).
4. **Excitation Hygiene**: Use the lowest AC excitation that gives a clean signal (typically ~0.5 nA). High excitation will "wash out" the Fraunhofer lobes.
5. **Hysteresis check**: The map sweeps $I_{dc}$ and $B$ in one direction each, so it can't reveal hysteresis on its own. To check for intrinsic sample hysteresis, re-take a few curves with both the $I_{dc}$ and $B$ sweep directions reversed and compare — it's uncommon, so a coarse check suffices.

## Verify
The output is a 2D "diamond" or "lobe" plot.

```python
from hera.analysis import open_run
import numpy as np

run = open_run("<data_dir>/<file_id>")
# Look for the characteristic central lobe (highest Ic) and side lobes.
```

- **Central Maximum**: The highest $I_c$ should occur at the effective zero field. 
  - **Trapped Flux**: In superconducting magnets (like the AMI430 on the toploader), trapped flux can shift the "zero" by O(1 mT). 
- **Lobe Periodicity**: Side lobes should be symmetric and periodic. Non-periodic lobes suggest non-uniform current distribution or multiple junctions.

## Examples
- `aaron/RPL_19/20251103_measure.ipynb` cells 100–102 — "2D fraunhofer at TG=0.47V, BG=-5.2V" (file 150/151).
- `isaac/b1c2_toploader/20260601_measure.ipynb` (QC0426) — Fraunhofer work at the SC dome center.

## Next
- **Temperature series**: Repeat the Fraunhofer map at different temperatures to see how the lobes collapse as $T \rightarrow T_c$.
- **Gate-ladder**: Repeat Fraunhofer at different densities to see how the junction area/character changes across the dome.
- **In-plane field**: Rotate the field into the plane ($B_{\parallel}$) to look for the Pauli limit or orbital effects.
