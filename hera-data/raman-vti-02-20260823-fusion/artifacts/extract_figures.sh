#!/usr/bin/env bash
# Regenerates the archived evidence figures from the ana notebook (no execution —
# extraction of stored outputs only). Run from the fusion directory.
# nb = ~/sharpelab/sharpelab-shared/tools/nb.py (stdlib-only).
#
# Cells: 20 = run 3 coarse gate map / R_CNP(D) coarse; 24 = run 4 band map
# (R_CNP(D), FWHM, D-symmetry); 28 = run 6 Landau fan at D≈0; 32 = run 7 fan at
# D−D0≈+0.20; 35 = runs 8–18 T ladder / Arrhenius.
nb extract inputs/20260823_ana.ipynb 20,24,28,32,35 --out artifacts
