---
slug: before-effmass
user: aaron
cut_index: 100
latest_fileid: 1638
included:
  data: [1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638]
  images: []
leak_terms:
  - "# Effective mass"
  - "Test fan"
  - "Zoomed in fan"
  - "Resuming effective mass"
  - "Small fan"
  - "oscillations are real"
  - "Cuts at fixed"
forward_scan: "kept region is cells 0-100 (Init/Configs, AH Spot Checks, AH in the normal state, Rerun hall map, Cool back down, Large AH MAP, Preping for effective mass). Greped the kept markdown + code comments for forward references (effective mass execution, fan, oscillation, cuts at fixed). Only section headers describing completed/current work are present; cell 85 '# Preping for effective mass' announces THIS (cut) section's intent, which is consistent context for a directive/depth brief (cf. b1c2 early-characterization). Cell 76 ('Probably take a couple bigger loops...?') and 97 ('i actually want the three rxxs') are in-section self-notes, not forward refs. The post-cut answer header '# Effective mass' (cell 101) does NOT appear before the cut. Clean."
---

# Frontier — cut at end of `# Preping for effective mass` (DEPTH)

*Freezes the RPL_19 2026-01-24 campaign at the boundary after the prep maps for
the effective-mass measurement and before the dedicated `# Effective mass`
series. The YAML above is the machine-readable contract `hera-replay` reads;
the prose is for humans.*

## Cut
- **Cut index 100** is the last cell of `# Preping for effective mass` — cell 100
  is the final prep `multimegasweep` (a density × field map at D = 0.2, → `data/1638`).
  Cell 101 is the `# Effective mass` markdown header, the first cell of the next
  section and the thing the agent must predict.
- Confirmed on a section boundary via `nb sections` (`# Preping for effective
  mass` [85] → `# Effective mass` [101]) and `nb summary 85-101`.

## What's live at the cut
The campaign has, toward the AH/QO/effective-mass goal:
1. `# AH Spot Checks` — `mag.field` hysteresis loops at the dome point (0.465, 1.000).
2. `# AH in the normal state` / `# Large AH MAP` — normal-state AH (n,D) maps in field.
3. `# Preping for effective mass` — (n,D)-line maps and a couple of field-vs-(n,D)
   fans, establishing where to sit and that the rig is ready for the temperature work.

**Latest landed sweep: `data/1638/`** (cell 100): a field × density map (Landau
fan), `mag.field` 0 → 1.5 T slow, gates along n = 0 → 1.5 at D = 0.2. State at
the cut: base T (~29–32 mK), V_Si = 48 V, gates parked after the map, DC bias 0,
config `mc_25` (current on `sr830_4` = `I_{30-21}`). See
`../ground_truth/before-effmass/reading.md`.

## Why this is a DEPTH frontier
The next experiment is barely in doubt: the section header literally says
"Effective mass," and m* in a 2D system is extracted from the temperature
damping of quantum oscillations — i.e. **repeat a field sweep at the fixed
(n, D) anchor at a ladder of temperatures** (set by the `heater`) and fit the
Lifshitz–Kosevich amplitude decay. What is genuinely open is the *depth /
rigor*: how many temperature points, the field range and step density (you need
enough oscillation periods and fine enough ΔB to resolve them), and how much
averaging. The briefs (`briefs/before-effmass/`) probe `quick` / `deep` /
`paper` on that single directive anchor.

## Leak terms
Post-cut-only tripwires, each verified `> 100` with `nb grep -i`:
`# Effective mass` (101, the answer header — note "effective mass" lowercase
appears pre-cut in "Preping for effective mass", so the term is anchored with
the leading `# `), `Test fan` (117), `Zoomed in fan` (131), `Resuming
effective mass` (146), `Small fan` (173), `oscillations are real` (173),
`Cuts at fixed` (177). These also catch the deeper `after-qo-confirmed`
frontier's answer region.

## Caveats carried into the cut
- **Cooldown drift.** `device_card.md` is the current-cooldown summary; the data
  on disk is the same chip but treat card vs. data as "fresh summary, older data."
- **No transport `plot.png`.** `data/1638/plot.png` is the gate-leakage monitor
  (blank); the transport signal is only in `data/1638/data.tsv.gz` — see reading.md.
