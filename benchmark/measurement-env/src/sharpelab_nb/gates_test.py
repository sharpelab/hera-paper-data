import unittest

import numpy as np

from sharpelab_nb.gates import (
    calc_gate_voltages,
    calc_nD,
    calculate_gate_voltages,
    calculate_n_D,
    comment_to_gates,
    pcolorize_nD,
    stack_capacitance,
    triangulate_nD,
)

_EPS0 = 8.8541878128e-12


class TestStackCapacitance(unittest.TestCase):
    def test_single_layer(self) -> None:
        c = stack_capacitance([(12, 3)])
        self.assertAlmostEqual(c, _EPS0 * 3 / 12e-9, delta=1e-9)

    def test_series_layers(self) -> None:
        """Two layers in series add reciprocally."""
        c = stack_capacitance([(12, 3), (285, 3.9)])
        expected = _EPS0 / (12e-9 / 3 + 285e-9 / 3.9)
        self.assertAlmostEqual(c, expected, delta=1e-12)

    def test_zero_thickness_layer_is_noop(self) -> None:
        self.assertAlmostEqual(
            stack_capacitance([(12, 3), (0, 3.9)]),
            stack_capacitance([(12, 3)]),
        )


class TestCapacitanceConversions(unittest.TestCase):
    C_TG = stack_capacitance([(15.6, 3)])
    C_BG = stack_capacitance([(12, 3)])

    def test_roundtrip_with_offsets(self) -> None:
        n_in = np.array([-2.0, 0.0, 1.5])
        D_in = np.array([0.25, -1.0, 0.0])
        Vtg, Vbg = calc_gate_voltages(
            n_in, D_in, self.C_TG, self.C_BG, n_offset=0.3, D_offset=-0.05
        )
        n_out, D_out = calc_nD(
            Vtg, Vbg, self.C_TG, self.C_BG, n_offset=0.3, D_offset=-0.05
        )
        np.testing.assert_allclose(n_out, n_in, atol=1e-12)
        np.testing.assert_allclose(D_out, D_in, atol=1e-12)

    def test_offsets_shift_zero(self) -> None:
        n, D = calc_nD(0.0, 0.0, self.C_TG, self.C_BG, n_offset=0.7, D_offset=0.1)
        self.assertAlmostEqual(float(n), 0.7)
        self.assertAlmostEqual(float(D), 0.1)

    def test_cnp_line_slope_is_capacitance_ratio(self) -> None:
        """Along the n = 0 line, dVtg/dVbg = -c_bg/c_tg — the QC0426
        geometry (t_tg = 1.3 t_bg, same kappa) gives the campaign's
        fitted CNP slope of -1.3."""
        self.assertAlmostEqual(self.C_BG / self.C_TG, 1.3, places=10)
        Vbg = np.linspace(-4, 4, 9)
        Vtg = -1.3 * Vbg
        n, _ = calc_nD(Vtg, Vbg, self.C_TG, self.C_BG)
        np.testing.assert_allclose(n, 0.0, atol=1e-12)

    def test_thickness_form_is_special_case(self) -> None:
        """The legacy dtg/dbg functions must agree with the capacitance
        form for a single hBN dielectric (rtol bounded by the old
        hand-rolled eps0/e constant's precision)."""
        c_tg = stack_capacitance([(16, 3)])
        c_bg = stack_capacitance([(25.5, 3)])
        Vtg = np.linspace(-6, 6, 13)
        Vbg = np.linspace(-5, 5, 13)
        n_new, D_new = calc_nD(Vtg, Vbg, c_tg, c_bg)
        n_old, D_old = calculate_n_D(Vtg, Vbg, dtg=16, dbg=25.5, ep=3)
        np.testing.assert_allclose(n_old, n_new, rtol=1e-7)
        np.testing.assert_allclose(D_old, D_new, rtol=1e-7)
        n = np.array([-2.0, 0.5, 3.0])
        D = np.array([1.0, 0.0, -0.5])
        Vtg_new, Vbg_new = calc_gate_voltages(n, D, c_tg, c_bg)
        Vtg_old, Vbg_old = calculate_gate_voltages(n, D, dtg=16, dbg=25.5, ep=3)
        np.testing.assert_allclose(Vtg_old, Vtg_new, rtol=1e-7)
        np.testing.assert_allclose(Vbg_old, Vbg_new, rtol=1e-7)

    def test_scalar_in_float_out(self) -> None:
        """Point-check case: scalar args return Python floats (float() works)."""
        Vtg, Vbg = calc_gate_voltages(1.0, 0.2, self.C_TG, self.C_BG)
        self.assertIsInstance(Vtg, float)
        self.assertIsInstance(Vbg, float)

    def test_list_args_accepted(self) -> None:
        """List args must not crash (np.asarray coercion)."""
        Vtg, Vbg = calc_gate_voltages([1.0], [0.2], self.C_TG, self.C_BG)
        self.assertEqual(Vtg.shape, (1,))


class TestGateConversions(unittest.TestCase):
    def test_roundtrip(self) -> None:
        """(n, D) -> (Vtg, Vbg) -> (n, D) should be identity."""
        n_in, D_in = 1e12, 0.5
        Vtg, Vbg = calculate_gate_voltages(n_in, D_in)
        n_out, D_out = calculate_n_D(Vtg, Vbg)
        self.assertAlmostEqual(float(n_out), n_in, places=3)
        self.assertAlmostEqual(float(D_out), D_in, places=3)

    def test_zero(self) -> None:
        Vtg, Vbg = calculate_gate_voltages(0, 0)
        self.assertAlmostEqual(float(Vtg), 0)
        self.assertAlmostEqual(float(Vbg), 0)

    def test_arrays(self) -> None:
        n = np.array([0, 1e12, 2e12])
        D = np.array([0, 0.5, 1.0])
        Vtg, Vbg = calculate_gate_voltages(n, D)
        n_out, D_out = calculate_n_D(Vtg, Vbg)
        np.testing.assert_allclose(n_out, n, rtol=1e-5)
        np.testing.assert_allclose(D_out, D, rtol=1e-5)

    def test_custom_geometry(self) -> None:
        """Different dielectric thicknesses should change the result."""
        Vtg1, Vbg1 = calculate_gate_voltages(1e12, 0.5, dtg=16, dbg=25.5)
        Vtg2, Vbg2 = calculate_gate_voltages(1e12, 0.5, dtg=30, dbg=300)
        self.assertNotAlmostEqual(float(Vtg1), float(Vtg2))
        self.assertNotAlmostEqual(float(Vbg1), float(Vbg2))


class TestCommentToGates(unittest.TestCase):
    def test_basic(self) -> None:
        Vtg, Vbg = comment_to_gates("nD point: (3.5, -2.1)")
        self.assertAlmostEqual(Vtg, 3.5)
        self.assertAlmostEqual(Vbg, -2.1)

    def test_no_key(self) -> None:
        Vtg, Vbg = comment_to_gates("(1.0, 2.0)", delim=":")
        self.assertAlmostEqual(Vtg, 1.0)
        self.assertAlmostEqual(Vbg, 2.0)


_UNIT_SQUARE_ND = np.array(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
    ]
)


class TestPcolorizeND(unittest.TestCase):
    def test_shape(self) -> None:
        nx, ny = 12, 9
        n_pts, _, _, _ = triangulate_nD(_UNIT_SQUARE_ND, nx, ny)
        zs = np.arange(len(n_pts), dtype=float)
        n_mat, D_mat, zs_mat = pcolorize_nD(zs, _UNIT_SQUARE_ND, nx, ny)
        self.assertEqual(n_mat.shape, (ny, nx))
        self.assertEqual(D_mat.shape, (ny, nx))
        self.assertEqual(zs_mat.shape, (ny, nx))

    def test_inside_polygon_finite(self) -> None:
        nx, ny = 12, 9
        n_pts, _, _, _ = triangulate_nD(_UNIT_SQUARE_ND, nx, ny)
        m = len(n_pts)
        zs = np.ones(m)
        _, _, zs_mat = pcolorize_nD(zs, _UNIT_SQUARE_ND, nx, ny)
        finite_mask = np.isfinite(zs_mat)
        self.assertEqual(int(finite_mask.sum()), m)
        np.testing.assert_array_equal(zs_mat[finite_mask], 1.0)
        nan_mask = ~finite_mask
        if nan_mask.any():
            self.assertTrue(np.all(np.isnan(zs_mat[nan_mask])))

    def test_geometry_dependence(self) -> None:
        """Geometry params must actually flow through to the gate-space mesh.
        n_mat/D_mat themselves are mathematically invariant under dtg/dbg/ep
        scaling (the symmetric forward/reverse affine map cancels), so we
        verify dependence via triangulate_nD's exposed (Vtg, Vbg)."""
        nx, ny = 10, 8
        _, _, Vtg_a, Vbg_a = triangulate_nD(_UNIT_SQUARE_ND, nx, ny, dtg=16, dbg=25.5)
        _, _, Vtg_b, Vbg_b = triangulate_nD(_UNIT_SQUARE_ND, nx, ny, dtg=30, dbg=25.5)
        _, _, Vtg_c, Vbg_c = triangulate_nD(_UNIT_SQUARE_ND, nx, ny, dtg=16, dbg=300.0)
        self.assertFalse(np.allclose(Vtg_a, Vtg_b))
        self.assertFalse(np.allclose(Vbg_a, Vbg_c))


class TestTriangulateND(unittest.TestCase):
    def test_lengths_match(self) -> None:
        nx, ny = 10, 7
        n_pts, D_pts, Vtg_pts, Vbg_pts = triangulate_nD(_UNIT_SQUARE_ND, nx, ny)
        m = len(n_pts)
        self.assertEqual(len(D_pts), m)
        self.assertEqual(len(Vtg_pts), m)
        self.assertEqual(len(Vbg_pts), m)
        self.assertGreater(m, 0)

    def test_inside_polygon(self) -> None:
        nx, ny = 20, 15
        n_pts, D_pts, _, _ = triangulate_nD(_UNIT_SQUARE_ND, nx, ny)
        eps = 1e-9
        self.assertTrue(np.all(n_pts >= -eps))
        self.assertTrue(np.all(n_pts <= 1.0 + eps))
        self.assertTrue(np.all(D_pts >= -eps))
        self.assertTrue(np.all(D_pts <= 1.0 + eps))

    def test_gate_round_trip(self) -> None:
        nx, ny = 10, 7
        n_pts, D_pts, Vtg_pts, Vbg_pts = triangulate_nD(_UNIT_SQUARE_ND, nx, ny)
        n_check, D_check = calculate_n_D(Vtg_pts, Vbg_pts)
        np.testing.assert_allclose(n_check, n_pts, rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(D_check, D_pts, rtol=1e-10, atol=1e-12)
        Vtg_check, Vbg_check = calculate_gate_voltages(n_pts, D_pts)
        np.testing.assert_allclose(Vtg_check, Vtg_pts, rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(Vbg_check, Vbg_pts, rtol=1e-10, atol=1e-12)

    def test_matches_pcolorize_count(self) -> None:
        """Same vertices/grid: triangulate_nD point count should equal
        pcolorize_nD non-NaN cell count. Catches drift if sweep.raster
        internals change asymmetrically between the two functions."""
        nx, ny = 13, 11
        verts = np.array([[0.0, 0.0], [1.5, 0.2], [1.2, 1.1], [-0.1, 0.8]])
        n_pts, _, _, _ = triangulate_nD(verts, nx, ny)
        m = len(n_pts)
        zs = np.arange(m, dtype=float)
        _, _, zs_mat = pcolorize_nD(zs, verts, nx, ny)
        finite_count = int(np.isfinite(zs_mat).sum())
        self.assertEqual(finite_count, m)


if __name__ == "__main__":
    unittest.main()
