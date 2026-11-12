import unittest

import numpy as np
from scipy.constants import e, h

from sharpelab_nb.qo import (
    delta_R_over_R,
    fft_vs_filling_1d,
    fft_vs_filling_2d,
    find_1d_peaks,
    interp_inv_b,
    remove_polynomial_background,
)

_PHI_0 = h / e


class TestRemovePolynomialBackground(unittest.TestCase):
    def test_kills_polynomial(self) -> None:
        B = np.linspace(0.5, 5.0, 200)
        coeffs = np.array([0.01, -0.1, 0.5, -1.0, 2.0, 3.0])
        Rxx = np.polyval(coeffs, B)
        out = remove_polynomial_background(B, Rxx, degree=5)
        np.testing.assert_allclose(out, 0.0, atol=1e-8)

    def test_preserves_oscillation(self) -> None:
        B = np.linspace(0.5, 5.0, 800)
        bg = np.polyval([0.0, 0.0, 0.5, -1.0, 2.0, 3.0], B)
        amp = 0.05
        osc = amp * np.sin(2 * np.pi * 100.0 / B)
        Rxx = bg + osc
        out = remove_polynomial_background(B, Rxx, degree=5)
        peak = float(np.max(np.abs(out)))
        # ~15% tolerance: high-freq SdH oscillation isn't perfectly orthogonal
        # to the 5th-degree fit basis, so a small leak in either direction
        # is normal and physically expected.
        self.assertGreater(peak, 0.85 * amp)
        self.assertLess(peak, 1.20 * amp)

    def test_2d_dispatch(self) -> None:
        B = np.linspace(0.5, 5.0, 200)
        cols = []
        for i in range(3):
            coeffs = np.array([0.0, 0.0, 0.1 * (i + 1), -0.5, 1.0, 2.0])
            cols.append(np.polyval(coeffs, B))
        Rxx = np.column_stack(cols)
        out = remove_polynomial_background(B, Rxx, degree=5)
        self.assertEqual(out.shape, Rxx.shape)
        np.testing.assert_allclose(out, 0.0, atol=1e-8)


class TestInterpInvB(unittest.TestCase):
    def test_grid_uniform(self) -> None:
        B = np.linspace(0.3, 3.0, 50)
        Rxx = np.sin(2 * np.pi / B)
        inv_b, Rxx_i = interp_inv_b(B, Rxx, nx=400)
        self.assertEqual(inv_b.shape, (400,))
        spacings = np.diff(inv_b)
        np.testing.assert_allclose(spacings, spacings[0], rtol=1e-12)

    def test_2d_shape(self) -> None:
        B = np.linspace(0.3, 3.0, 50)
        Rxx = np.column_stack([np.sin(k / B) for k in (1.0, 2.0, 3.0)])
        inv_b, Rxx_i = interp_inv_b(B, Rxx, nx=128)
        self.assertEqual(inv_b.shape, (128,))
        self.assertEqual(Rxx_i.shape, (128, 3))


class TestFftVsFilling(unittest.TestCase):
    def test_recovers_known_frequency(self) -> None:
        """Synthetic Rxx with a known SdH frequency should peak at the
        expected filling-fraction bin under the 1D normalization (peak at 1
        for the standard SdH frequency BF = phi_0 * n / degeneracy)."""
        n_per_cm2_e12 = 5.0
        n_si = n_per_cm2_e12 * 1e16
        degeneracy = 4
        bf = _PHI_0 * n_si / degeneracy

        B = np.linspace(0.5, 8.0, 1024)
        rxx = np.sin(2 * np.pi * bf / B)
        inv_b, rxx_i = interp_inv_b(B, rxx, nx=2048)
        psd, freq = fft_vs_filling_1d(inv_b, rxx_i, n_per_cm2_e12, degeneracy=degeneracy)

        positive = freq > 0
        peak_idx_local = int(np.argmax(psd[positive]))
        peak_freq = freq[positive][peak_idx_local]
        # Peak should be near 1.0 on the filling-fraction axis (~5% tolerance
        # is comfortable for finite N + Hann window leakage).
        self.assertAlmostEqual(peak_freq, 1.0, delta=0.05)

    def test_normalization(self) -> None:
        rng = np.random.default_rng(seed=1)
        B = np.linspace(0.5, 5.0, 256)
        Rxx = rng.standard_normal(B.shape)
        inv_b, Rxx_i = interp_inv_b(B, Rxx, nx=256)
        psd, _ = fft_vs_filling_1d(inv_b, Rxx_i, 1.0)
        self.assertAlmostEqual(float(psd.max()), 1.0)

        Rxx_2d = rng.standard_normal((256, 3))
        psd_2d, _ = fft_vs_filling_2d(inv_b, Rxx_2d, np.array([1.0, 2.0, 3.0]))
        self.assertAlmostEqual(float(psd_2d.max()), 1.0)

    def test_padding_lengthens_output(self) -> None:
        B = np.linspace(0.5, 5.0, 128)
        Rxx = np.sin(2 * np.pi / B)
        inv_b, Rxx_i = interp_inv_b(B, Rxx, nx=128)
        psd_0, _ = fft_vs_filling_1d(inv_b, Rxx_i, 1.0, padding=0)
        psd_2, _ = fft_vs_filling_1d(inv_b, Rxx_i, 1.0, padding=2)
        n = 128
        padding = 2
        self.assertEqual(psd_0.shape, (n,))
        self.assertEqual(psd_2.shape, (2 * n * padding + n,))

        Rxx_2d = np.column_stack([Rxx, Rxx])
        psd_2d_0, _ = fft_vs_filling_2d(inv_b, Rxx_2d, np.array([1.0, 1.0]), padding=0)
        psd_2d_3, _ = fft_vs_filling_2d(inv_b, Rxx_2d, np.array([1.0, 1.0]), padding=3)
        self.assertEqual(psd_2d_0.shape, (n, 2))
        self.assertEqual(psd_2d_3.shape, (2 * n * 3 + n, 2))

    def test_2d_matches_1d_columnwise(self) -> None:
        """fft_vs_filling_2d on a 2D Rxx should match fft_vs_filling_1d
        column-by-column on the *psd* axis. The frequency axes use different
        (reciprocal) conventions per Aaron's original code, so we only
        compare psd."""
        B = np.linspace(0.5, 5.0, 256)
        Rxx_a = np.sin(2 * np.pi * 50.0 / B)
        Rxx_b = np.sin(2 * np.pi * 30.0 / B)
        inv_b, Rxx_a_i = interp_inv_b(B, Rxx_a, nx=512)
        _, Rxx_b_i = interp_inv_b(B, Rxx_b, nx=512)
        Rxx_2d = np.column_stack([Rxx_a_i, Rxx_b_i])
        n_per = np.array([1.0, 2.0])

        psd_2d, _ = fft_vs_filling_2d(inv_b, Rxx_2d, n_per)
        psd_a_1d, _ = fft_vs_filling_1d(inv_b, Rxx_a_i, n_per[0])
        psd_b_1d, _ = fft_vs_filling_1d(inv_b, Rxx_b_i, n_per[1])

        # 2D psd is normalized by the global max across columns, 1D by its
        # own max — so compare ratios within each column.
        col0 = psd_2d[:, 0] / psd_2d[:, 0].max()
        col1 = psd_2d[:, 1] / psd_2d[:, 1].max()
        np.testing.assert_allclose(col0, psd_a_1d / psd_a_1d.max(), rtol=1e-10)
        np.testing.assert_allclose(col1, psd_b_1d / psd_b_1d.max(), rtol=1e-10)


class TestFind1dPeaks(unittest.TestCase):
    def test_returns_list(self) -> None:
        fv = np.linspace(0, 10, 200)
        signal = np.sin(2 * np.pi * fv)
        peaks = find_1d_peaks(fv, signal, distance=5)
        self.assertIsInstance(peaks, list)
        for item in peaks:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], float)
            self.assertIsInstance(item[1], float)
        self.assertGreater(len(peaks), 0)


class TestDeltaROverR(unittest.TestCase):
    def test_zero_at_norm_b(self) -> None:
        B = np.linspace(0.1, 2.1, 21)
        Rxx = np.tile(np.linspace(1.0, 2.0, 5), (21, 1)) + B[:, None] * 0.1
        dRxx, inv_b = delta_R_over_R(B, Rxx, norm_b=1.0, tol=0.001)
        # B[9] == 1.0 exactly given linspace(0.1, 2.1, 21).
        np.testing.assert_allclose(dRxx[9, :], 0.0, atol=1e-12)
        np.testing.assert_allclose(inv_b, 1.0 / B)


if __name__ == "__main__":
    unittest.main()
