"""Size of the within-model permutation test and of the bootstrap CI under the null pilot (T = 8 h).

    uv run --no-project --with numpy --with scipy python3 null_size.py
Three seeds of 2000 simulations per N, pooled. Writes null_size.md.
"""
import numpy as np
import common as C
import devset as DV
import power_budget as PB

SEEDS, SIMS = (23, 101, 202), 2000


def main():
    own, pool, both = PB.dev_cells(DV.scored())
    pl = PB.pilot('null', own, pool, both)
    f = lambda x: f"{100 * np.mean(x):.1f} ± {100 * np.sqrt(np.mean(x) * (1 - np.mean(x)) / len(x)):.1f} %"
    L = ['# Decision test under the null pilot\n', f'{len(SEEDS)} seeds × {SIMS} simulations; 1000 permutations, 500 bootstraps.\n',
         '| N | permutation p < 0.05 | bootstrap CI excludes 0 |', '|---|---|---|']
    for N in (10, 20):
        rp, rc = [], []
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            for _ in range(SIMS):
                cells = {c: PB.run_cell(src, cz, rng, N)[0] for c, (src, cz) in pl.items()}
                rp.append(PB.perm_p(cells, 8.0, rng, 1000) < 0.05)
                est, lo, hi = PB.boot_ci(cells, 8.0, rng, 500)
                rc.append(lo > 0 or hi < 0)
        L.append(f'| {N} | {f(rp)} | {f(rc)} |')
    open(C.OUT / 'null_size.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
