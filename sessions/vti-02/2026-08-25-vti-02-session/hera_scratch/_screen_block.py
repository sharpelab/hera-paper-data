# Harmonic screen FIRST (investigation: "screen harmonics first, Luttinger-aware"),
# THEN test the templates. The naive best-summing-pair search is wrong: with no
# screen it pairs a fundamental with its own 2nd harmonic, and at high field it
# pairs the partner with the breakdown/sum tone.
def screen(f, a, tol=0.10):
    """Drop tones sitting at k>=2 times a STRONGER tone (k integer within tol)."""
    order = np.argsort(a)[::-1]
    keep, kept_f = [], []
    for i in order:
        h = False
        for g in kept_f:
            if g > 1e-9:
                m = f[i] / g
                if m >= 1.8 and abs(m - round(m)) < tol:
                    h = True
                    break
        if not h:
            keep.append(i)
            kept_f.append(f[i])
    keep = np.array(sorted(keep, key=lambda i: -a[i]))
    return f[keep], a[keep]

print("")
print("=== after harmonic screen: template test per column ===")
hdr = f"{'n(e12)':>7} {'F_L':>6} {'tones kept (T)':>26} {'dom/F_L':>8} {'sum/F_L':>9} {'frac_lo':>8}"
print(hdr)
part, nclose, ncols = [], 0, 0
for d in rows:
    if d is None:
        continue
    ncols += 1
    f, a = screen(d["f"], d["a"])
    d["fs"], d["as_"] = f, a
    dom = f[0] / d["F_L"]
    best = None
    for i in range(len(f)):
        for j in range(i + 1, len(f)):
            ssum = f[i] + f[j]
            e = abs(ssum / d["F_L"] - 1.0)
            if best is None or e < best[0]:
                best = (e, min(f[i], f[j]), max(f[i], f[j]), ssum)
    if best is None:
        print(f"{d['n']:>7.2f} {d['F_L']:>6.1f} {str([round(x,1) for x in f]):>26} {dom:>8.3f}")
        continue
    e, lo, hi, ssum = best
    ok = e < 0.08
    nclose += ok
    if ok:
        part.append((d["n"], lo / ssum, hi / ssum))
    print(f"{d['n']:>7.2f} {d['F_L']:>6.1f} {str([round(x,1) for x in f]):>26} {dom:>8.3f} "
          f"{ssum/d['F_L']:>9.3f} {lo/ssum:>8.3f} {'OK' if ok else ''}")
print("")
print(f"Luttinger sum closes (<8%) in {nclose}/{ncols} columns after the harmonic screen")
part = np.array(part) if part else np.zeros((0, 3))
if len(part):
    print(f"partner fraction {part[:,1].min():.3f}..{part[:,1].max():.3f} over n "
          f"{part[:,0].min():.2f}..{part[:,0].max():.2f}")
    print("  ABAB-4L model 0.16-0.22 over this n range; trilayer ML+BL 0.02-0.05")
doms = np.array([d["fs"][0] / d["F_L"] for d in rows if d is not None and len(d.get("fs", []))])
print(f"dominant tone / F_L: median {np.median(doms):.3f}, range {doms.min():.3f}..{doms.max():.3f}")
print("  ABCA singleton template -> 1.00 | ABAB heavy -> 0.72-0.79")
