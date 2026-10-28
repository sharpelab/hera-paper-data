# LK fit: per-branch m* with shared electron-temperature floor T_e0.
# A(T) = A0 * X/sinh(X), X = 14.694 * (m*/m_e) * T_eff / B_eff,
# T_eff = sqrt(T_rung^2 + T_e0^2); B_eff from <1/B> over the fixed FFT window.
import numpy as np
from scipy.optimize import curve_fit, minimize

T = np.array([1.251, 6.130, 10.135, 14.156, 19.148, 25.084])
A11 = np.array([2.10, 2.02, 1.96, 1.90, 1.68, 1.49])
A55 = np.array([1.44, 1.16, 0.761, 0.502, 0.258, 0.0979])
A66 = np.array([1.14, 0.961, 0.521, 0.236, 0.116, 0.0896])
B_EFF = 2.0 / (1 / 3.2 + 1 / 8.0)  # harmonic mean of window edges = 4.571 T

def lk(T, A0, m, Te0):
    x = 14.694 * m * np.sqrt(T**2 + Te0**2) / B_EFF
    return A0 * x / np.sinh(x)

# joint fit: shared Te0, per-branch (A0, m) for the two fundamentals
def resid(p):
    Te0, a1, m1, a2, m2 = p
    r1 = np.log(lk(T, a1, m1, Te0)) - np.log(A11)
    r2 = np.log(lk(T, a2, m2, Te0)) - np.log(A55)
    return np.sum(r1**2) + np.sum(r2**2)

from scipy.optimize import differential_evolution
bounds = [(0.1, 15), (1, 4), (0.005, 0.06), (1, 4), (0.02, 0.2)]
sol = differential_evolution(resid, bounds, seed=1, tol=1e-10)
Te0, a1, m1, a2, m2 = sol.x
print(f"joint fit: T_e0 = {Te0:.2f} K")
print(f"  f_ML 11.1 T: m* = {m1:.4f} m_e (A0 {a1:.2f})")
print(f"  f_BL 55.3 T: m* = {m2:.4f} m_e (A0 {a2:.2f})")
print(f"  mass ratio m_BL/m_ML = {m2/m1:.2f}")
# sum tone with Te0 fixed
p66, _ = curve_fit(lambda TT, A0, m: lk(TT, A0, m, Te0), T, A66,
                   p0=[2.5, m1 + m2], maxfev=20000)
print(f"  sum 66.4 T: m* = {p66[1]:.4f} m_e vs m_ML+m_BL = {m1+m2:.4f}")
# beat exclusion: is the 11 T component lighter than the main branch?
print(f"  beat exclusion: m(11.1)={m1:.4f} < m(55.3)={m2:.4f} -> {'PASS (cannot be a beat)' if m1 < m2 else 'FAIL'}")
# residuals
for lbl, A, a0, m in (("A11", A11, a1, m1), ("A55", A55, a2, m2)):
    pred = lk(T, a0, m, Te0)
    print(f"  {lbl} fit residuals (%): {np.round((A/pred-1)*100, 1)}")
