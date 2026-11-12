# Bias spectroscopy (dV/dI)

## What
Differential resistance $dV/dI$ as a function of DC bias current $I_{dc}$. Run either as a **point check** — a single 1D $dV/dI$ vs $I_{dc}$ sweep at a fixed operating point $(n, D)$, the quickest test for a finite $I_c$ — or as a **2D map** over a second axis (typically carrier density $n$, displacement field $D$, magnetic field $B$, or temperature $T$).

Point check (1D): dV/dI vs Idc at a fixed operating point.
```python
s.sweep(dc205_1.volt, Vdc_vec, delay=1)
```

Map (2D): bias vs a tuning axis (here top gate).
```python
s.megasweep(k_tg.volt, Vtg_vec, dc205_1.volt, Vdc_vec, fast_delay=1, slow_delay=3)
```
The measurement uses a **lock-in amplifier** (AC excitation) summed with a **DC voltage source** (e.g., Yokogawa GS200 or SRS DC205). The lock-in $X$ signal is proportional to the differential resistance $dV/dI$. In a superconducting state, $dV/dI$ is zero (or very low) for $|I_{dc}| < I_c$ and rises at the critical current $I_c$.

## When
- **SC Dome mapping** — after a zero-field gate map has identified a region of vanishing resistance. A nonlinear $dV/dI$ vs $I_{dc}$ — low differential resistance near zero bias that rises at a critical current $I_c$ — is consistent with a supercurrent.
- **Critical current extraction** — to map how $I_c$ varies with $n$, $D$, $B$, or $T$.

Prerequisites: A stable low-resistance state identified in a survey map, calibrated DC bias source (bias resistor $R_{bias}$ known), and lock-in parameters set to avoid heating fragile states (paper convention: 1 nA AC excitation).

## Why
A low-resistance region in a gate map could be a superconductor, a quantum anomalous Hall (QAH) state, or simply a good normal metal. Bias spectroscopy distinguishes them:
- **Superconductor**: nonlinear $dV/dI$ vs $I_{dc}$ with a supercurrent lobe terminating at $I_c$; Hall resistance $R_{xy} \approx 0$.
- **QAH state**: $R_{xx} \to 0$ so $dV/dI$ is also low until the gap breaks down, but there is no supercurrent lobe — the tell is a large nonzero $R_{xy}$, read simultaneously as $dV_{xy}/dI$ on a transverse contact pair.
- **Good (normal) metal**: finite but low resistance with roughly constant (ohmic) $dV/dI$ vs $I_{dc}$ — no supercurrent lobe, no quantization.

A Fraunhofer-like modulation of $I_c$ with perpendicular field $B_{\perp}$ is consistent with phase-coherent (Josephson) transport, with lobe spacing set by the junction area, $\Delta B \approx \Phi_0 / A$.

## Recipe
1. **Identify the Operating Point**: Pick $(n, D)$ coordinates from a survey map where the resistance is minimal.
2. **Setup the Bias Axis**:
   - The DC source (e.g., `dc205_1.volt`) drives a bias resistor $R_{bias}$ (typically 10–100 MΩ) to convert voltage to current: $I_{dc} = V_{dc} / R_{bias}$.
   - The lock-in AC excitation $V_{ac}$ also drives a large resistor (typically 100 MΩ–1 GΩ) to provide a small AC current $I_{ac}$.
   - Ensure $I_{ac} \ll I_c$ (typically $I_{ac} \approx 0.25 \text{--} 1$ nA).
3. **Configure the Sweep**:
   - **Fast Axis**: DC Bias. Usually a symmetric sweep around zero.
   - **Slow Axis**: The tuning parameter ($n$, $D$, $B$, or $T$).
   - **Delays**: Bias sweeps need time for the lock-in to settle at each point. Use `fast_delay ≈ 5 × TC` (TC = lock-in time constant).
   - **Round-Trip**: Consider using a round-trip sweep (forward + backward bias) to check for thermal heating or vortex-induced hysteresis. Land this as `np.hstack((fwd, bwd))`.
4. **Convert the bias axis**: Record $R_{bias}$ and scale the x-axis from source voltage to current, $I_{dc} = V_{dc}/R_{bias}$.
5. **Monitor for Heating**: If $I_c$ is unexpectedly low or the gap is smeared, reduce the AC excitation. High-resistance contacts can also cause local heating.

## Verify
The output is a 1D $dV/dI$ trace (point check) or a 2D map.

Point check (1D): Ic from a single dV/dI vs Idc trace.
```python
from sharpelab_nb.sc import extract_critical_current   # not yet shipped — extract by hand
import sweep.sweep_load as sl

data = sl.pload("<path>", <run_id>)
r = (data['<Vchan>_X'] / gain_V) / (data['<Ichan>_X'] / gain_I)   # dV/dI (Ω); channels + gains per device card
ic_neg, ic_pos = extract_critical_current(data['xs'], r, threshold=500)
```

Map (2D): Ic per slow-axis row.
```python
from sharpelab_nb.sc import map_ic_dome   # not yet shipped — extract by hand
import sweep.sweep_load as sl

data = sl.pload("<path>", <run_id>)
r = (data['<Vchan>_X'] / gain_V) / (data['<Ichan>_X'] / gain_I)   # dV/dI (Ω); channels + gains per device card
ic_neg, ic_pos = map_ic_dome(data['ys'], data['xs'], r, threshold=500)
```
(threshold in Ohms sets the SC-to-normal cutoff — e.g. 500 Ω for 4-terminal $R_{xx}$.)

- **Transition at $I_c$**: $dV/dI$ rises from near zero to the normal-state value at $I_c$ — a sharp switching peak or a smooth onset, depending on junction dynamics, temperature, and disorder. **Bracket the bias window past the switching peaks to the normal state at each end** — a window that stops near $I_c$ never reaches the normal state.
- **Symmetry**: A rigid *shift* of the $I_c$ lobe (~1–5 nA) is usually instrumental (amplifier offset, thermoelectric). A *magnitude* asymmetry $I_c^+ \neq I_c^-$ is physical — nonreciprocal (diode) transport or disorder.
- **"The Dome"**: In an $(I_{dc}, n)$ map, the $I_c$ values should form a dome shape, reaching a maximum at the "optimum" density.

## Examples
- `aaron/RPL_10/250201_measure.ipynb` cells 30–34 — "SC1' Idc vs T" (repeat 1D bias cuts).
- `isaac/b1c2_toploader/20260415_measure.ipynb` cells 263–271 — "Idc vs T" heater × bias megasweep.
- `aaron/RPL_19/20251103_measure.ipynb` cells 87–100 — The "Fraunhofer" sequence (bias vs B).

## Next
- **Fraunhofer mapping**: If $I_c$ is found, sweep perpendicular field $B_{\perp}$ to look for lobe modulation.
- **Temperature series**: Repeat bias spectroscopy as a function of temperature to extract $I_c(T)$ and fit to Ginzburg-Landau or BCS models.
- **Hysteresis check**: Check if $I_c$ depends on the sweep direction of the bias (thermal or vortex hysteresis).
