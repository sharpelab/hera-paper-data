# Gate range finding — VTI variant

**Base**: `device-init/gate-range-finding.md`. This file carries only
the deltas (STYLE rule 13); read the base first. Runs executed under
this variant tag `s.add_comment('gate-range-finding-vti')`.

**Overridden steps and the rig facts that force them:**

- **Step 1, leakage readback** — the VTI top gate is driven by an SRS
  DC205: a pure voltage source with **no current readback at all**; and
  the rig's second Keithley (the Si gate's K2410) is **too noisy at pA
  scale for leakage duty**. The only pA-capable instrument on the gate
  rack is the back-gate K2400 ⇒ step 1 for any gate the K2400 doesn't
  normally drive becomes the **Keithley-repatch workflow** below.
- **Step 2, corner readback grade** — same facts: with the K2400
  restored to the back gate, the parked-gate corner values are held by
  sources without pA readback ⇒ the corner check on this rig is
  **gross-breakdown-grade, not onset-grade** (base step 2's caveat is
  the rule here, not the edge case). Record that grade in the closing
  comment.
- **Step 3, validator target** — the top gate is swept through a
  wrapper parameter around the DC205's ramped set (the device card
  names it; `dc205_volt` on the reference campaign) ⇒ commit the
  validator on **the wrapper parameter the sweep cells use**, and
  re-commit after the repatch is undone (a validator left on the K2400
  from its top-gate stint bounds the wrong gate once the cable moves
  back).

## The repatch workflow (step 1 replacement for readback-less gates)

1. Range-find the back gate first, with its own K2400 — that leg is
   pure base recipe.
2. **Repatch**: operator moves the K2400 cable from the back gate to
   the gate under test (top gate). In the same cell that first uses the
   new wiring, rewrite `measurement_config` — channel entries and a
   comment naming the actual wiring ("push top gate with k_bg
   (changed cable)") — per the base's truth precondition. From here
   every `k_bg.volt` column is a *top-gate* voltage; nothing but the
   config says so.
3. Walk the gate's endpoints per base step 1, reading leakage on the
   repatched K2400 at high integration. The base's onset-bracketing
   refinement is cheap insurance here — this is the one chance to see
   this gate's onset at pA grade for the whole cooldown.
4. **Restore**: cable back to the back gate; config rewritten again in
   the next cell that sweeps. Hand the range-found gate to its real
   source (DC205) and confirm the handover at a benign voltage — set a
   small value through the wrapper parameter and check the transport
   channels respond as the repatch-era sweeps said they should. From
   this point the gate's leakage is **unmonitored by construction**:
   the committed validator plus the geometry ceiling are the only
   guards, which is why neither may be skipped on this rig.

Liveness reads during all of the above follow the device card's channel
conventions (current channel with mandatory gain division on the
reference device) — card facts, not recipe facts.

## Examples

- `vti/qingrui/20260601-QC0426-3LGr/measurement.ipynb`
  *(our-measurement, the campaign this variant encodes)*: cells 36–48
  back gate with its own K2400 (workflow item 1); cell 51 the repatch
  declaration ("temporarily use k_bg keithley for TG and push") and
  cell 52 the rewritten config; cells 54–61 the repatched top-gate walk
  ending in the 0.1 V bracketing sweep (cell 61); cell 62 the chosen
  range; cell 78 the handover — `dc205_volt` defined as a wrapper
  parameter over the DC205's `ramp_voltage` and zeroed (workflow
  item 4). Cells 64–80 are the four-corners block at
  gross-breakdown grade, with the Si K2410 holding back-gate corner
  values — the base's Examples carry the full label-lie war story.

## Next

Base `## Next` applies unchanged. On this rig the natural successor is
the 0 T gate map that feeds CNP/D-line calibration.

## Obsolescence

A switch matrix on the rig's lines (e.g. the QSwitch already present on
the VTI rack, once gate lines are routed through it) lets the pA-capable
K2400 be routed to any gate without touching a cable — the repatch
workflow collapses to a routing step and this variant reduces to the
base plus one line. A top-gate source with usable current readback
(replacing the DC205, or a series current preamp on that gate line)
does the same. Either change: delete this file, fold anything still
true into the base's Examples.
