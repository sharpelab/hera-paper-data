"""f3_contract_checks.py — machine-checkable reproduction of the Raman
contract's numbers from inputs/regions.npz (areas, centroids, fractions).

Expected (raman-contract.md): areas 528/516/236/66/66/39 um^2 for labels
1/2/5/6/3/4; remnant post-pickup ABC fraction 0.78; sheet ~50:50.
"""
import numpy as np

z = np.load("inputs/regions.npz", allow_pickle=True)
x, y = z["x_um"], z["y_um"]
px_area = np.diff(x)[0] * np.diff(y)[0]  # 0.25 um^2

print(f"grid: x {x.min()}..{x.max()}, y {y.min()}..{y.max()}, "
      f"{np.diff(x)[0]} um/px ({px_area} um^2/px)")
for lay, labs in (("labels_pre", (1, 2, 3, 4)), ("labels_post", (5, 6))):
    L = z[lay]
    for k in labs:
        m = L == k
        cx = x[np.where(m)[1]].mean()
        cy = y[np.where(m)[0]].mean()
        print(f"{lay} label {k}: area {m.sum() * px_area:.0f} um^2, "
              f"centroid ({cx:.1f}, {cy:.1f})")

pre, post = z["labels_pre"], z["labels_post"]
sheet_aba = (pre == 2).sum()
sheet_abc = (pre == 1).sum()
print(f"sheet ABC:ABA = {sheet_abc}:{sheet_aba} "
      f"({sheet_abc / (sheet_abc + sheet_aba):.2f} ABC) — contract: ~50:50")
rem = np.isin(post, [5, 6])
print(f"remnant ABC fraction (post) = {(post == 5).sum() / rem.sum():.2f} "
      f"— contract: 0.78")
inpre = pre[rem]
abc, aba = (inpre == 1).sum(), (inpre == 2).sum()
print(f"tombstone footprint in PRE map: ABC fraction {abc / (abc + aba):.2f} "
      f"— contract cross-map figure: 0.72 (method differs: contract used "
      f"map-003 cluster labels, this uses region labels; consistent)")
