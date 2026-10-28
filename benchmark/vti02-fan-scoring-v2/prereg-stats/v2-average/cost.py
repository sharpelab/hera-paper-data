"""Token / $ cost per episode from the run records.

    uv run --no-project --with numpy --with scipy python3 cost.py
Writes cost.md. Claude episodes: summary.csv cost (= the last result event's total_cost_usd),
tokens summed over the transcript's result events. Codex episodes: tokens from the rollout's
last token_count, priced from src/hera/replay/prices.toml (summary.csv under-reports the
episodes run before the token write-back fix).
"""
import numpy as np
import common as C
import devset as DV


def main():
    eps = DV.scored()
    L = []
    P = L.append
    P('# Cost per episode and per cell\n')
    P('Every episode that ran (counted and excluded alike: excluded episodes are paid for).\n')
    P('| model | effort | n | mean $ | median $ | min–max $ | mean tokens in (uncached) / cache write / cache read / out |')
    P('|---|---|---|---|---|---|---|')
    per = {}
    for m in ('fable', 'opus', 'sol', 'astra', 'sonnet', 'haiku', 'luna'):
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
    P('\nPer-cell and per-cut cost under the censored design: power_budget.md.')
    open(C.OUT / 'cost.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
