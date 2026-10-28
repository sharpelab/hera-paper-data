import unittest
import warnings

import numpy as np

from sharpelab_nb.symmetry import b_field_symmetrize


class TestBFieldSymmetrize(unittest.TestCase):
    def test_pure_sym(self) -> None:
        z = np.ones((4, 4))
        z_sym, z_asym = b_field_symmetrize(z, z)
        np.testing.assert_array_equal(z_sym, z)
        np.testing.assert_array_equal(z_asym, np.zeros_like(z))

    def test_pure_asym(self) -> None:
        z_pos = np.array([[1.0, -2.0], [3.5, 0.0]])
        z_neg = -z_pos
        z_sym, z_asym = b_field_symmetrize(z_pos, z_neg)
        np.testing.assert_array_equal(z_sym, np.zeros_like(z_pos))
        np.testing.assert_array_equal(z_asym, z_pos)

    def test_known_decomposition(self) -> None:
        rng = np.random.default_rng(seed=0)
        z_pos = rng.standard_normal((5, 7))
        z_neg = rng.standard_normal((5, 7))
        z_sym, z_asym = b_field_symmetrize(z_pos, z_neg)
        np.testing.assert_allclose(z_sym + z_asym, z_pos)
        np.testing.assert_allclose(z_sym - z_asym, z_neg)

    def test_shape_preserved(self) -> None:
        for shape in [(4,), (3, 5), (2, 3, 4)]:
            with self.subTest(shape=shape):
                rng = np.random.default_rng(seed=hash(shape) & 0xFFFF)
                z_pos = rng.standard_normal(shape)
                z_neg = rng.standard_normal(shape)
                z_sym, z_asym = b_field_symmetrize(z_pos, z_neg)
                self.assertEqual(z_sym.shape, shape)
                self.assertEqual(z_asym.shape, shape)

    def test_with_nans(self) -> None:
        z_pos = np.array([1.0, np.nan, 3.0, 4.0])
        z_neg = np.array([1.0, 2.0, np.nan, -4.0])
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            z_sym, z_asym = b_field_symmetrize(z_pos, z_neg)
        self.assertEqual(z_sym[0], 1.0)
        self.assertEqual(z_asym[0], 0.0)
        self.assertTrue(np.isnan(z_sym[1]))
        self.assertTrue(np.isnan(z_asym[1]))
        self.assertTrue(np.isnan(z_sym[2]))
        self.assertTrue(np.isnan(z_asym[2]))
        self.assertEqual(z_sym[3], 0.0)
        self.assertEqual(z_asym[3], 4.0)


if __name__ == "__main__":
    unittest.main()
