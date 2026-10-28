# Cost per episode and per cell

Every episode that ran (counted and excluded alike: excluded episodes are paid for).

| model | effort | n | mean $ | median $ | min–max $ | mean tokens in (uncached) / cache write / cache read / out |
|---|---|---|---|---|---|---|
| fable | high | 3 | 8.72 | 8.87 | 8.05–9.25 | 0k / 141k / 3.28M / 52k |
| fable | medium | 3 | 6.26 | 5.78 | 5.24–7.75 | 0k / 103k / 2.44M / 35k |
| opus | high | 2 | 3.76 | 3.76 | 2.98–4.53 | 0k / 132k / 2.84M / 41k |
| opus | medium | 3 | 2.71 | 3.44 | 0.56–4.14 | 0k / 99k / 1.95M / 30k |
| sol | high | 2 | 2.25 | 2.25 | 1.77–2.73 | 148k / 0k / 3.11M / 21k |
| sol | medium | 1 | 1.78 | 1.78 | 1.78–1.78 | 101k / 0k / 2.65M / 16k |
| astra | high | 4 | 1.96 | 1.82 | 1.78–2.43 | 92k / 0k / 0.73M / 6k |
| astra | medium | 8 | 1.91 | 1.90 | 1.39–2.78 | 89k / 0k / 0.75M / 5k |
| sonnet | medium | 16 | 1.73 | 1.84 | 0.19–2.85 | 0k / 108k / 4.58M / 38k |
| haiku | medium | 7 | 0.55 | 0.54 | 0.29–0.79 | 0k / 77k / 2.58M / 26k |
| luna | medium | 2 | 0.06 | 0.06 | 0.06–0.06 | 117k / 0k / 1.17M / 9k |
| luna | low | 1 | 0.03 | 0.03 | 0.03–0.03 | 66k / 0k / 0.62M / 4k |

Per-cell and per-cut cost under the censored design: power_budget.md.
