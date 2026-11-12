---
slug: after-qo-confirmed
user: aaron
cut_index: 176
latest_fileid: 1776
included:
  data: [1541, 1542, 1543, 1544, 1545, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1597, 1598, 1599, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631, 1632, 1633, 1634, 1635, 1636, 1637, 1638, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1651, 1652, 1653, 1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1665, 1666, 1667, 1668, 1669, 1670, 1671, 1672, 1673, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1681, 1682, 1683, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 1699, 1700, 1701, 1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721, 1722, 1723, 1724, 1725, 1726, 1727, 1728, 1729, 1730, 1731, 1732, 1733, 1734, 1735, 1736, 1737, 1738, 1739, 1740, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749, 1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1758, 1759, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1774, 1775, 1776]
  images: []
leak_terms:
  - "Cuts at fixed"
  - "Large series"
  - "Heating at CSC"
  - "Cooling in QM"
  - "CSC out to 5T"
  - "Second series"
forward_scan: "kept region is cells 0-176 (Init/Configs through '# Small fan to check if oscillations are real' inclusive — i.e. the AH work, the full effective-mass temperature series, and the small confirmation fan). Greped the kept markdown + code comments for forward references to the post-cut sections; the headers '# Cuts at fixed n and D' (177), '## Large series' (182), '# Heating at CSC' (185), '# Cooling in QM' (215), '# Second series' (226), '# CSC out to 5T' (230) appear only AFTER the cut. In-region notes ('i actually want the three rxxs' [97], 'Probably take a couple bigger loops...?' [76]) are self-notes, not forward refs. Clean."
---

# Frontier — cut at end of `# Small fan to check if oscillations are real` (CONTESTED)

*Freezes the RPL_19 2026-01-24 campaign just after the oscillations have been
confirmed real, before `# Cuts at fixed n and D`. The YAML above is the
machine-readable contract; the prose is for humans.*

## Cut
- **Cut index 176** is the last cell of `# Small fan to check if oscillations
  are real` — cell 176 is the second small fan (the D = 1 fan → `data/1776`).
  Cell 177 is the `# Cuts at fixed n and D` header, the first cell of the next
  section and the thing the agent must predict.
- Confirmed on a section boundary via `nb sections` (`# Small fan …` [173] →
  `# Cuts at fixed n and D` [177]) and `nb summary 146-185`.

## What's live at the cut
Toward the AH/effective-mass/QO goal, the campaign has now completed:
1. `# AH Spot Checks` / `# AH in the normal state` / `# Large AH MAP` — the AH
   characterization at and around the dome point.
2. `# Effective mass` + `# Resuming effective mass` — a substantial
   temperature-dependent field-sweep series at fixed (n = 1, D = 1) plus
   interspersed fans (`## Test fan`, `# Zoomed in fan`), out to higher field range.
3. `# Small fan to check if oscillations are real` — two small Landau fans
   (D = 0.2 and D = 1, `mag.field` 0.9 → 2.5 T) taken specifically to verify the
   field-periodic structure is a genuine quantum oscillation, not noise.

**Latest landed sweep: `data/1776/`** (cell 176): the D = 1 small fan
(`mag.field` 0.9 → 2.5 T slow, gates along n = 0.9 → 0.5 fast). State at the
cut: base T, V_Si = 48 V, gates parked, DC bias 0, config `mc_25`. See
`../ground_truth/after-qo-confirmed/reading.md`.

## Why this is a CONTESTED frontier
The oscillations are real — now what? Several moves are all defensible:
- **Fixed-(n, D) line cuts** (high-resolution 1D `mag.field` cuts at chosen
  (n, D) points) to read the QO *frequency* B_F cleanly and convert it to a
  Fermi-surface area / carrier density — Aaron's actual next move.
- **A full effective-mass temperature series** at the now-confirmed oscillation
  point (the m* extraction proper, building on the data already taken).
- **Broader Landau-fan mapping** (a wider, denser fan over (n, B)) to chart how
  the oscillations and gaps evolve across the dome before drilling into one point.
These trade off "characterize the feature you found" vs. "map where it lives" vs.
"finish the m* number" — a genuine strategic branch. Hence the full 2×2 briefs.

## Leak terms
Post-cut-only tripwires, each verified `> 176` with `nb grep -i`:
`Cuts at fixed` (177, the answer header), `Large series` (182), `Heating at
CSC` (185), `Cooling in QM` (215), `CSC out to 5T` (230), `Second series` (226).
(The effective-mass / small-fan headers are PRE-cut for this deeper frontier, so
they are deliberately NOT leak terms here.)

## Caveats carried into the cut
- **Cooldown drift** — as in `before-effmass`: card is current-cooldown, data is
  older same-chip. Flag if it matters.
- **No transport `plot.png`.** `data/1776/plot.png` is the gate-leakage monitor
  (blank); transport is only in `data/1776/data.tsv` — see reading.md.
