## HERA — Step 1b: 0 T TG-BG gate map (E1 auto, ~40 min)

`cnp-and-dline-calibration` Step 1 / `gatemap`. Axis-aligned megasweep in **raw gate volts**
(first map — cap ratio not yet trusted, so no (n,D) projection in the sweep): slow = **BG
[-4, 4] V x17 rows**, fast = **TG [-6, 7] V x105** (0.125 V), Si held at **0** (contact gate),
B = 0. Two deliverables: the **CNP ridge** V_tg(V_bg) -> slope = -c_bg/c_tg for the (n,D)
calibration, and the **metallic/insulating survey** across n at D~0 to pick fan contact pairs
that stay metallic (recipe Step 1).

Sizing from run 0: CNP intercept +0.44 V at BG=0, geometry slope prior -1.3 -> ridge
V_tg = -1.3·V_bg + 0.44 runs +5.64 .. -4.76 V across BG[-4,4], inside [-6,7] with >1 V margin
even at slope 1.5 (robust to slope uncertainty; BG capped at +-4, not +-4.5, to keep that margin).

**Cost:** run-0 calibrates 1.21 s/pt; 1785 pts + ~17 row-turnarounds ~= **40 min**. BG steps at
its 5 mV `volt.step` (graphite gate, safe); slow_delay 2 s. Leakage fp'd on both Keithleys (<1 nA
guard). **Checkpoint at ~row 5 (~12 min):** confirm a clean CNP ridge sits inside the TG window
(not edge-clipped), leakage <1 nA, lock-ins not railed -> continue / shift TG / abort. Preconditions
asserted (T<5 K, |B|<0.05 T, live current). Parks gates to 0 on completion. Tags `gatemap`.
