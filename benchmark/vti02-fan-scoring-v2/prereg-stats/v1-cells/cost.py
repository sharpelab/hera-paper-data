"""Token / $ cost per episode from the run records, and expected cost per cell under the
stopping rule (N landed fans, capped at 2N episodes).

    uv run --no-project --with numpy --with scipy python3 cost.py
Writes cost.md. Claude episodes: summary.csv cost (= the last result event's total_cost_usd),
tokens summed over the transcript's result events. Codex episodes: tokens from the rollout's
last token_count, priced from src/hera/replay/prices.toml (summary.csv under-reports the
episodes run before the token write-back fix).
"""
import numpy as np
import common as C
import devset as DV
import power as PW


def main():
    eps = DV.scored()
    L = []
    P = L.append
    P('# Cost per episode and per cell\n')
    P('Every episode that ran (counted and excluded alike: excluded episodes are paid for).\n')
    P('| model | effort | n | mean $ | median $ | min–max $ | mean tokens in (uncached) / cache write / cache read / out |')
    P('|---|---|---|---|---|---|---|')
    per = {}
    for m in C.MATRIX_MODELS + ('sonnet', 'haiku', 'luna'):
        for eff in ('high', 'medium', 'low'):
            sel = [e for e in eps if e['model'] == m and e['effort'] == eff and e['cost_usd'] is not None and e['status'] != 'interrupted']
            if not sel:
                continue
            c = np.array([e['cost_usd'] for e in sel])
            t = [e['tokens'] for e in sel if e.get('tokens')]
            tm = {k: np.mean([x[k] for x in t]) for k in ('input', 'cache_creation', 'cache_read', 'output')} if t else {}
            per[(m, eff)] = c
            P(f"| {m} | {eff} | {len(c)} | {c.mean():.2f} | {np.median(c):.2f} | {c.min():.2f}–{c.max():.2f} | "
              + (f"{tm['input']/1e3:.0f}k / {tm['cache_creation']/1e3:.0f}k / {tm['cache_read']/1e6:.2f}M / {tm['output']/1e3:.0f}k |" if tm else '— |'))
    # expected episodes per cell under the stopping rule, smoothed pilot landing rates
    pool, both, own = PW.build_pilots(eps)
    draw = PW.sampler('smoothed', pool, both, own)
    rng = np.random.default_rng(3)
    P('\n## Expected cost per cell, N landed fans capped at 2N (landing rate from the smoothed pilot; $ at the high-effort mean)\n')
    P('| model | arm | pilot landing rate | $/episode (high) | E[episodes] N=5 / 10 / 20 | E[$] N=5 / 10 / 20 |')
    P('|---|---|---|---|---|---|')
    tot = np.zeros(3)
    for m in C.MATRIX_MODELS:
        usd = per.get((m, 'high'))
        usd = usd.mean() if usd is not None else np.nan
        for a in ('corpus', 'none'):
            big = draw(m, a, rng, 20000)
            p = big[:, 2].mean()
            ne = [np.mean([len(PW.stop_rule_draw(draw, m, a, rng, N)) for _ in range(2000)]) for N in (5, 10, 20)]
            tot += np.array(ne) * usd
            P(f"| {m} | {a} | {p:.2f} | {usd:.2f} | {ne[0]:.1f} / {ne[1]:.1f} / {ne[2]:.1f} | {ne[0]*usd:.0f} / {ne[1]*usd:.0f} / {ne[2]*usd:.0f} |")
    P(f"\nWhole 4 × 2 matrix at one cut: E[$] = {tot[0]:.0f} / {tot[1]:.0f} / {tot[2]:.0f} for N = 5 / 10 / 20; "
      f"worst case (every cell at 2N) = {sum(2*N*(per[(m,'high')].mean()) for m in C.MATRIX_MODELS for _ in (0,1) for N in (5,)):.0f} / "
      f"{sum(2*10*(per[(m,'high')].mean()) for m in C.MATRIX_MODELS for _ in (0,1)):.0f} / {sum(2*20*(per[(m,'high')].mean()) for m in C.MATRIX_MODELS for _ in (0,1)):.0f}. "
      'The 2×2 cut design doubles it.')
    open(C.OUT / 'cost.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
