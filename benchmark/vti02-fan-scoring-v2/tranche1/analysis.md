# vti-02 fan-design analysis: vti02-fan-request-0822

- script sha256 `33adaaac8af38243125b34c74ba1ce7afc89b0da2a50dffa7e337ea768e87462`
- permutations 10000, seed 20260929; floor unscored: False
- run dirs:
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-astra-corpus/20260929T212521-qy46wv`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-astra-none/20260929T212522-w72phb`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-fable51-corpus/20260929T212520-paekuu`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-fable51-none/20260929T212521-w3uii4`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-fable-corpus/20260929T212520-bdyomi`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-fable-none/20260929T212520-bror6s`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-gpt6sol-corpus/20260929T212522-3qbrb9`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-gpt6sol-none/20260929T212522-3t9imq`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-opus55-corpus/20260929T212519-xn4twg`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-opus55-none/20260929T212519-ci0plf`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-opus-corpus/20260929T212518-pacxe4`
  - `/data/sharpelab/hera-data/replay/runs/vti02-fan-request-0822-opus-none/20260929T212518-7hk80x`
- grader (sha256, git blob):
  - `hera/graders/fan-design/grade.py` `0d22ee156953305854cf9696372c8ddcdd853468d01f0637cbd8589be4222339` `32d39e00`
  - `hera/graders/fan-design/box.py` `edcd5506e6fa83f0b98656c5b273d47c9220debd833795ee6e7c355edf332f27` `b1242820`
  - `hera/graders/fan-design/resolution.py` `a3b38020a218542396ecb7796e3ad9b883b6bc7dbb6b5e77b233fdcc0e455caa` `2f4d36ea`
  - `hera/graders/fan-design/cases.toml` `0f289f086d88b499ecacc4c4bee0878eedd833dbc8a6dd153dd59d3e30c20789` `53511fba`
  - `hera/graders/fan-design/tones.csv` `d05190319d58e4983a4b36f8874dde07ef44ac0cd0f1b1050a59d7011c6e6460` `a6b007c7`
  - `hera/graders/fan-design/rmax.csv` `e5324377596708b131072bcfc1c5f29f109169a26607468d6c396eec1f068444` `b2f22480`
  - `hera/graders/fan-design/prompt.md` `d7e78564b988279d69d094aa037e92e4d17756e44e52eec4d7b13179ff39430c` `152661ec`
  - `hera/graders/devices.py` `976118daff1776608dabe6d59c0581aa1dc9b2543ee987d87b7f82f87a4efc52` `4d9385c3`

## Cells

| model | arm | episodes | fans | spot check | B = 0 | nothing landed | excluded | re-extract | S1 P(call) 8 h | S2 span | S3 rows/F_L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-fable-5 | corpus | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0.333 | 4.26 | 3.40 |
| claude-fable-5 | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.421 | 2.47 | 2.12 |
| claude-opus-5 | corpus | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0.991 | 3.82 | 4.08 |
| claude-opus-5 | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.593 | 2.77 | 2.54 |
| claude-fable-5-1 | corpus | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0.997 | 4.44 | 3.32 |
| claude-fable-5-1 | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.181 | 1.03 | 0.45 |
| claude-opus-5-5 | corpus | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0.978 | 3.63 | 2.48 |
| claude-opus-5-5 | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.975 | 4.38 | 2.88 |
| gpt-6-astra | corpus | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 0.526 | 1.54 | 8.58 |
| gpt-6-astra | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.045 | 1.96 | 3.46 |
| gpt-6-sol | corpus | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.728 | 2.69 | 3.42 |
| gpt-6-sol | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0.020 | 0.08 | 0.34 |

## Registered metrics

| metric | statistic | models | raw p | Holm p |
|---|---|---|---|---|
| 1 P(call) within 8 h | +0.386 | 6 (claude-fable-5, claude-opus-5, claude-fable-5-1, claude-opus-5-5, gpt-6-astra, gpt-6-sol) | 0.0011 | 0.0022 |
| 2 tracked span (bins) | +1.284 | 6 (claude-fable-5, claude-opus-5, claude-fable-5-1, claude-opus-5-5, gpt-6-astra, gpt-6-sol) | 0.0032 | 0.0032 |
| 3 rows per F_L period at top n | +2.249 | 6 (claude-fable-5, claude-opus-5, claude-fable-5-1, claude-opus-5-5, gpt-6-astra, gpt-6-sol) | 0.0003 | 0.0009 |
| 4 Pareto dominance D | +0.384 | 6 (claude-fable-5, claude-opus-5, claude-fable-5-1, claude-opus-5-5, gpt-6-astra, gpt-6-sol) | 0.0002 | 0.0008 |
- 1 P(call) within 8 h: per model claude-fable-5 -0.088, claude-opus-5 +0.398, claude-fable-5-1 +0.816, claude-opus-5-5 +0.003, gpt-6-astra +0.481, gpt-6-sol +0.708
- 2 tracked span (bins): per model claude-fable-5 +1.794, claude-opus-5 +1.052, claude-fable-5-1 +3.412, claude-opus-5-5 -0.747, gpt-6-astra -0.415, gpt-6-sol +2.608
- 3 rows per F_L period at top n: per model claude-fable-5 +1.281, claude-opus-5 +1.543, claude-fable-5-1 +2.869, claude-opus-5-5 -0.402, gpt-6-astra +5.122, gpt-6-sol +3.081
- 4 Pareto dominance D: per model claude-fable-5 +0.000, claude-opus-5 +0.400, claude-fable-5-1 +0.600, claude-opus-5-5 +0.467, gpt-6-astra +0.400, gpt-6-sol +0.440

## Registered sensitivities

| axis | level | metric | Δ | models | raw p |
|---|---|---|---|---|---|
| budget | 6 h | 1 P(call) within 8 h | +0.495 | 6 | 0.0001 |
| budget | 12 h | 1 P(call) within 8 h | +0.394 | 6 | 0.0004 |
| budget | none | 1 P(call) within 8 h | +0.368 | 6 | 0.0004 |
| column spacing | 0.25 bin | 1 P(call) within 8 h | +0.412 | 6 | 0.0011 |
| column spacing | 0.25 bin | 2 tracked span (bins) | +1.183 | 6 | 0.0042 |
| column spacing | 1 bin | 1 P(call) within 8 h | +0.301 | 6 | 0.0023 |
| column spacing | 1 bin | 2 tracked span (bins) | +1.485 | 6 | 0.0020 |
| P(call) curve | a step at four points | 1 P(call) within 8 h | +0.297 | 6 | 0.0057 |
| P(call) curve | linear | 1 P(call) within 8 h | +0.376 | 6 | 0.0011 |
| P(call) combination | the parts averaged | 1 P(call) within 8 h | +0.241 | 6 | 0.0124 |
| P(call) combination | their product | 1 P(call) within 8 h | +0.357 | 6 | 0.0016 |
| censoring | censored scored 0 | 1 P(call) within 8 h | +0.131 | 6 | 0.2502 |

## Fans

| episode | model | arm | field axis | hours | P(call) | v (8 h) | span light | span split | span | rows/F_L | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vti02-fan-request-0822-fable-corpus/20260929T212520-bdyomi/00 | claude-fable-5 | corpus | 2d_megasweep (invB): B 0.75–10.00 T × 126; n(actual) +1.06…+2.88e12 × 81 | 7.08 | 0.998 | 0.998 | 7.04 | 4.58 | 4.58 | 3.40 |  |
| vti02-fan-request-0822-fable-corpus/20260929T212520-bdyomi/02 | claude-fable-5 | corpus | 2d_megasweep (invB): B 0.40–6.00 T × 233; n(actual) +1.59…+2.84e12 × 81 | 11.68 | 0.988 | 0.000 | 5.56 | 3.75 | 3.75 | 3.39 |  |
| vti02-fan-request-0822-fable-corpus/20260929T212520-bdyomi/04 | claude-fable-5 | corpus | 2d_megasweep (invB): B 0.50–10.00 T × 191; n(actual) +1.06…+2.84e12 × 91 | 11.24 | 0.997 | 0.000 | 6.83 | 4.46 | 4.46 | 3.41 |  |
| vti02-fan-request-0822-fable-none/20260929T212520-bror6s/00 | claude-fable-5 | none | 2d_megasweep (stitched): B 0.25–10.00 T × 131; n(actual) -1.11…+2.87e12 × 151 | 7.67 | 0.999 | 0.999 | 6.07 | 4.56 | 4.56 | 4.72 |  |
| vti02-fan-request-0822-fable-none/20260929T212520-bror6s/01 | claude-fable-5 | none | 2d_megasweep (B): B 1.00–10.00 T × 91; n(actual) -1.11…+2.84e12 × 151 | 5.93 | 0.107 | 0.107 | 4.44 | 0.40 | 0.40 | 0.38 |  |
| vti02-fan-request-0822-fable-none/20260929T212520-bror6s/02 | claude-fable-5 | none | 2d_megasweep (B): B 0.35–10.00 T × 194; n(actual) -1.10…+2.87e12 × 181 | 13.42 | 0.777 | 0.000 | 7.00 | 2.35 | 2.35 | 0.71 |  |
| vti02-fan-request-0822-fable-none/20260929T212520-bror6s/03 | claude-fable-5 | none | 2d_megasweep (invB): B 1.00–10.00 T × 120; n(actual) -1.11…+2.88e12 × 141 | 7.07 | 0.998 | 0.998 | 4.59 | 4.59 | 4.59 | 4.44 |  |
| vti02-fan-request-0822-fable-none/20260929T212520-bror6s/04 | claude-fable-5 | none | 2d_megasweep (B): B 0.20–10.00 T × 99; n(actual) -1.11…+2.87e12 × 205 | 8.23 | 0.111 | 0.000 | 6.29 | 0.44 | 0.44 | 0.37 |  |
| vti02-fan-request-0822-fable51-corpus/20260929T212520-paekuu/00 | claude-fable-5-1 | corpus | 2d_megasweep (stitched): B 0.60–10.00 T × 143; n(actual) +1.06…+2.84e12 × 76 | 5.16 | 0.998 | 0.998 | 6.77 | 4.45 | 4.45 | 3.39 |  |
| vti02-fan-request-0822-fable51-corpus/20260929T212520-paekuu/01 | claude-fable-5-1 | corpus | 2d_megasweep (invB): B 0.70–10.00 T × 121; n(actual) +0.89…+2.84e12 × 45 | 4.73 | 0.996 | 0.996 | 6.77 | 4.40 | 4.40 | 3.08 |  |
| vti02-fan-request-0822-fable51-corpus/20260929T212520-paekuu/04 | claude-fable-5-1 | corpus | 2d_megasweep (invB): B 1.00–10.00 T × 93; n(actual) +0.89…+2.84e12 × 101 | 4.95 | 0.997 | 0.997 | 4.46 | 4.46 | 4.46 | 3.49 |  |
| vti02-fan-request-0822-fable51-none/20260929T212521-w3uii4/00 | claude-fable-5-1 | none | 2d_megasweep (B): B 1.00–10.00 T × 91; n(actual) -1.12…+2.87e12 × 130 | 5.27 | 0.105 | 0.105 | 4.55 | 0.43 | 0.43 | 0.37 |  |
| vti02-fan-request-0822-fable51-none/20260929T212521-w3uii4/01 | claude-fable-5-1 | none | 2d_megasweep (stitched): B 1.00–10.00 T × 111; n(actual) -1.11…+2.88e12 × 141 | 6.62 | 0.799 | 0.799 | 4.59 | 2.37 | 2.37 | 0.71 |  |
| vti02-fan-request-0822-fable51-none/20260929T212521-w3uii4/02 | claude-fable-5-1 | none | 2d_megasweep (stitched): B 1.00–10.00 T × 131; n(actual) -1.10…+2.86e12 × 150 | 8.01 | 0.812 | 0.000 | 4.53 | 2.32 | 2.32 | 0.71 |  |
| vti02-fan-request-0822-fable51-none/20260929T212521-w3uii4/03 | claude-fable-5-1 | none | 2d_megasweep (B): B 1.00–10.00 T × 61; n(actual) -1.06…+2.84e12 × 89 | 3.83 | 0.000 | 0.000 | 3.90 | 0.00 | 0.00 | 0.26 |  |
| vti02-fan-request-0822-fable51-none/20260929T212521-w3uii4/04 | claude-fable-5-1 | none | 2d_megasweep (stitched): B 0.60–10.00 T × 48; n(actual) -1.10…+2.84e12 × 179 | 4.28 | 0.000 | 0.000 | 3.58 | 0.00 | 0.00 | 0.20 |  |
| vti02-fan-request-0822-opus-corpus/20260929T212518-pacxe4/00 | claude-opus-5 | corpus | 2d_megasweep (invB): B 0.60–10.00 T × 157; n(actual) +1.77…+2.84e12 × 44 | 5.42 | 0.993 | 0.993 | 5.07 | 3.79 | 3.79 | 3.40 |  |
| vti02-fan-request-0822-opus-corpus/20260929T212518-pacxe4/02 | claude-opus-5 | corpus | 2d_megasweep (invB): B 0.65–10.00 T × 144; n(actual) +1.95…+2.84e12 × 33 | 4.49 | 0.983 | 0.983 | 4.33 | 3.29 | 3.29 | 3.39 |  |
| vti02-fan-request-0822-opus-corpus/20260929T212518-pacxe4/03 | claude-opus-5 | corpus | 2d_megasweep (invB): B 1.00–10.00 T × 145; n(actual) +1.42…+2.84e12 × 41 | 4.80 | 0.997 | 0.997 | 4.38 | 4.38 | 4.38 | 5.46 |  |
| vti02-fan-request-0822-opus-none/20260929T212518-7hk80x/00 | claude-opus-5 | none | 2d_megasweep (stitched): B 0.20–10.00 T × 149; n(actual) -1.06…+2.84e12 × 111 | 4.83 | 0.943 | 0.943 | 5.56 | 4.43 | 4.43 | 5.45 |  |
| vti02-fan-request-0822-opus-none/20260929T212518-7hk80x/01 | claude-opus-5 | none | 2d_megasweep (B): B 0.25–10.00 T × 40; n(actual) -1.11…+2.88e12 × 113 | 2.86 | 0.000 | 0.000 | 2.72 | 0.00 | 0.00 | 0.17 |  |
| vti02-fan-request-0822-opus-none/20260929T212518-7hk80x/02 | claude-opus-5 | none | 2d_megasweep (invB): B 1.00–10.00 T × 109; n(actual) -1.11…+2.87e12 × 113 | 4.82 | 0.949 | 0.949 | 4.55 | 4.55 | 4.55 | 4.04 |  |
| vti02-fan-request-0822-opus-none/20260929T212518-7hk80x/03 | claude-opus-5 | none | 2d_megasweep (B): B 1.00–10.00 T × 91; n(actual) -1.06…+2.84e12 × 141 | 4.56 | 0.077 | 0.077 | 4.44 | 0.40 | 0.40 | 0.38 |  |
| vti02-fan-request-0822-opus-none/20260929T212518-7hk80x/04 | claude-opus-5 | none | 2d_megasweep (invB): B 1.00–10.00 T × 71; n(actual) -1.06…+2.84e12 × 177 | 5.48 | 0.997 | 0.997 | 4.46 | 4.46 | 4.46 | 2.65 |  |
| vti02-fan-request-0822-opus55-corpus/20260929T212519-xn4twg/00 | claude-opus-5-5 | corpus | 2d_megasweep (stitched): B 0.70–10.00 T × 92; n(actual) +1.77…+2.84e12 × 25 | 3.05 | 0.977 | 0.977 | 5.01 | 3.39 | 3.39 | 1.14 |  |
| vti02-fan-request-0822-opus55-corpus/20260929T212519-xn4twg/01 | claude-opus-5-5 | corpus | 2d_megasweep (invB): B 0.80–5.00 T × 78; n(actual) +1.77…+2.88e12 × 36 | 2.29 | 0.960 | 0.960 | 4.59 | 3.28 | 3.28 | 2.46 |  |
| vti02-fan-request-0822-opus55-corpus/20260929T212519-xn4twg/02 | claude-opus-5-5 | corpus | 2d_megasweep (invB): B 1.00–10.00 T × 103; n(actual) +1.59…+2.85e12 × 31 | 3.42 | 0.997 | 0.997 | 4.22 | 4.22 | 4.22 | 3.84 |  |
| vti02-fan-request-0822-opus55-none/20260929T212519-ci0plf/00 | claude-opus-5-5 | none | 2d_megasweep (invB): B 1.00–10.00 T × 82; n(actual) -1.11…+2.88e12 × 151 | 5.45 | 0.999 | 0.999 | 4.59 | 4.59 | 4.59 | 3.02 |  |
| vti02-fan-request-0822-opus55-none/20260929T212519-ci0plf/01 | claude-opus-5-5 | none | 2d_megasweep (stitched): B 1.00–10.00 T × 138; n(actual) -1.11…+2.88e12 × 181 | 7.03 | 0.951 | 0.951 | 4.60 | 4.60 | 4.60 | 3.34 |  |
| vti02-fan-request-0822-opus55-none/20260929T212519-ci0plf/02 | claude-opus-5-5 | none | 2d_megasweep (stitched): B 0.70–10.00 T × 144; n(actual) -1.11…+2.86e12 × 151 | 7.78 | 0.946 | 0.946 | 6.89 | 4.47 | 4.47 | 2.92 |  |
| vti02-fan-request-0822-opus55-none/20260929T212519-ci0plf/03 | claude-opus-5-5 | none | 2d_megasweep (stitched): B 1.00–10.00 T × 122; n(actual) -1.11…+2.88e12 × 91 | 5.13 | 0.997 | 0.997 | 4.56 | 4.56 | 4.56 | 4.00 |  |
| vti02-fan-request-0822-opus55-none/20260929T212519-ci0plf/04 | claude-opus-5-5 | none | 2d_megasweep (stitched): B 0.60–10.00 T × 138; n(actual) -1.11…+2.84e12 × 90 | 5.67 | 0.983 | 0.983 | 6.61 | 3.66 | 3.66 | 1.14 |  |
| vti02-fan-request-0822-astra-corpus/20260929T212521-qy46wv/01 | gpt-6-astra | corpus | 2d_megasweep (invB): B 1.02–6.50 T × 239; n(actual) +2.48…+2.84e12 × 11 | 3.53 | 0.658 | 0.658 | 1.54 | 1.54 | 1.54 | 9.80 |  |
| vti02-fan-request-0822-astra-corpus/20260929T212521-qy46wv/02 | gpt-6-astra | corpus | 2d_megasweep (invB): B 1.02–6.50 T × 151; n(actual) +2.48…+2.84e12 × 11 | 2.48 | 0.658 | 0.658 | 1.54 | 1.54 | 1.54 | 6.17 |  |
| vti02-fan-request-0822-astra-corpus/20260929T212521-qy46wv/03 | gpt-6-astra | corpus | 2d_megasweep (invB): B 1.03–7.05 T × 238; n(actual) +2.48…+2.84e12 × 10 | 1.39 | 0.262 | 0.262 | 1.54 | 1.54 | 1.54 | 9.76 |  |
| vti02-fan-request-0822-astra-none/20260929T212522-w72phb/00 | gpt-6-astra | none | 2d_megasweep (stitched): B 2.00–10.00 T × 65; n(actual) -1.06…+2.84e12 × 111 | 7.91 | 0.223 | 0.223 | 0.81 | 0.81 | 0.81 | 5.46 |  |
| vti02-fan-request-0822-astra-none/20260929T212522-w72phb/01 | gpt-6-astra | none | 2d_megasweep (stitched): B 1.50–10.00 T × 101; n(actual) -1.06…+2.84e12 × 111 | 11.56 | 0.708 | 0.000 | 2.05 | 2.05 | 2.05 | 6.02 |  |
| vti02-fan-request-0822-astra-none/20260929T212522-w72phb/02 | gpt-6-astra | none | 2d_megasweep (stitched): B 0.50–6.00 T × 106; n(actual) -1.06…+2.84e12 × 89 | 9.49 | 0.963 | 0.000 | 4.22 | 3.16 | 3.16 | 0.17 |  |
| vti02-fan-request-0822-astra-none/20260929T212522-w72phb/03 | gpt-6-astra | none | 2d_megasweep (stitched): B 2.00–10.00 T × 75; n(actual) -1.06…+2.84e12 × 111 | 8.93 | 0.223 | 0.000 | 0.81 | 0.81 | 0.81 | 5.52 |  |
| vti02-fan-request-0822-astra-none/20260929T212522-w72phb/04 | gpt-6-astra | none | 2d_megasweep (stitched): B 0.50–10.00 T × 89; n(actual) -1.06…+2.84e12 × 111 | 10.35 | 0.918 | 0.000 | 3.88 | 2.96 | 2.96 | 0.10 |  |
| vti02-fan-request-0822-gpt6sol-corpus/20260929T212522-3qbrb9/00 | gpt-6-sol | corpus | 2d_megasweep (invB): B 0.70–10.00 T × 134; n(actual) +1.95…+2.84e12 × 46 | 5.88 | 0.983 | 0.983 | 4.33 | 3.30 | 3.30 | 3.42 |  |
| vti02-fan-request-0822-gpt6sol-corpus/20260929T212522-3qbrb9/01 | gpt-6-sol | corpus | 2d_megasweep (B): B 1.00–10.00 T × 901; n(actual) +2.39…+2.84e12 × 12 | 10.66 | 0.658 | 0.000 | 1.91 | 1.91 | 1.91 | 3.45 |  |
| vti02-fan-request-0822-gpt6sol-corpus/20260929T212522-3qbrb9/02 | gpt-6-sol | corpus | 2d_megasweep (invB): B 0.85–10.00 T × 110; n(actual) +2.13…+2.84e12 × 24 | 3.67 | 0.854 | 0.854 | 3.19 | 2.75 | 2.75 | 3.45 |  |
| vti02-fan-request-0822-gpt6sol-corpus/20260929T212522-3qbrb9/03 | gpt-6-sol | corpus | 2d_megasweep (invB): B 0.70–10.00 T × 133; n(actual) +2.13…+2.84e12 × 25 | 3.27 | 0.948 | 0.948 | 3.57 | 2.74 | 2.74 | 3.39 |  |
| vti02-fan-request-0822-gpt6sol-corpus/20260929T212522-3qbrb9/04 | gpt-6-sol | corpus | 2d_megasweep (invB): B 0.90–10.00 T × 102; n(actual) +2.13…+2.84e12 × 20 | 2.61 | 0.854 | 0.854 | 3.03 | 2.73 | 2.73 | 3.41 |  |
| vti02-fan-request-0822-gpt6sol-none/20260929T212522-3t9imq/00 | gpt-6-sol | none | 2d_megasweep (B): B 1.00–10.00 T × 46; n(actual) -0.89…+2.84e12 × 85 | 4.01 | 0.000 | 0.000 | 2.81 | 0.00 | 0.00 | 0.20 |  |
| vti02-fan-request-0822-gpt6sol-none/20260929T212522-3t9imq/01 | gpt-6-sol | none | 2d_megasweep (stitched): B 0.10–10.00 T × 70; n(actual) +0.71…+2.84e12 × 49 | 3.87 | 0.100 | 0.100 | 6.10 | 0.39 | 0.39 | 0.38 |  |
| vti02-fan-request-0822-gpt6sol-none/20260929T212522-3t9imq/02 | gpt-6-sol | none | 2d_megasweep (B): B 0.25–10.00 T × 40; n(actual) -1.06…+2.84e12 × 111 | 4.47 | 0.000 | 0.000 | 2.59 | 0.00 | 0.00 | 0.17 |  |
| vti02-fan-request-0822-gpt6sol-none/20260929T212522-3t9imq/03 | gpt-6-sol | none | 2d_megasweep (stitched): B 0.50–10.00 T × 47; n(actual) -1.06…+2.84e12 × 111 | 3.09 | 0.000 | 0.000 | 2.82 | 0.00 | 0.00 | 0.20 |  |
| vti02-fan-request-0822-gpt6sol-none/20260929T212522-3t9imq/04 | gpt-6-sol | none | 2d_megasweep (B): B 2.00–10.00 T × 41; n(actual) +0.35…+2.84e12 × 71 | 3.16 | 0.000 | 0.000 | 0.81 | 0.00 | 0.00 | 0.75 |  |

## Censored

- spot_check: vti02-fan-request-0822-astra-corpus/20260929T212521-qy46wv/00 (model gpt-6-astra): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-astra-corpus/20260929T212521-qy46wv/04 (model gpt-6-astra): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-fable51-corpus/20260929T212520-paekuu/02 (model claude-fable-5-1): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-fable51-corpus/20260929T212520-paekuu/03 (model claude-fable-5-1): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-fable-corpus/20260929T212520-bdyomi/01 (model claude-fable-5): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-fable-corpus/20260929T212520-bdyomi/03 (model claude-fable-5): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-opus55-corpus/20260929T212519-xn4twg/03 (model claude-opus-5-5): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-opus55-corpus/20260929T212519-xn4twg/04 (model claude-opus-5-5): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-opus-corpus/20260929T212518-pacxe4/01 (model claude-opus-5): landed field_probe, form probe_only
- spot_check: vti02-fan-request-0822-opus-corpus/20260929T212518-pacxe4/04 (model claude-opus-5): landed field_probe, form probe_only

## Excluded

none

## Needs re-extraction or grader error

none
