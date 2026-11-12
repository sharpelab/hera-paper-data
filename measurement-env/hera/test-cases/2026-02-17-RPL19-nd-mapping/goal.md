# Goal

> "Map the (n, D) landscape at positive D to find the SC / anomalous-Hall region and pin down where it sits, so we can choose where to do the detailed field/bias/temperature follow-ups."
>
> — expert framing (Aaron, RPL_19 device, 2026-02-17 cooldown)

This is the experimentalist's stated intent for the section of measurements
captured here. An offline HERA test should treat this as the campaign-goal
context an analyst would receive at the start of the session.

The section captured spans the post-power-loss **(n, D) mapping phase** — a
coarse recon map of a thin high-D sliver, then a coverage extension to the full
reachable range, then a D-first re-sweep to clean up sweep-direction streaks. The
fixture carries **two chained decision frontiers** drawn from this sequence (see
`README.md` and the `frontiers/` files):

- `after-rough-nd-map` (COVERAGE) — coarse sliver in hand → extend the map to the
  full reachable (n, D) range.
- `after-broaden-map` (DATA-QUALITY) — broaden map in hand but streaking n-first
  → re-sweep D-first to fix the artifact.

Both are clear-answer *decision* frontiers (what to do next), not a depth/rigor
probe — the original "how finely to map it" framing was corrected by Aaron on
2026-06-08.
