import numpy as np
import numpy.typing as npt


def b_field_symmetrize(
    z_pos: npt.NDArray[np.floating],
    z_neg: npt.NDArray[np.floating],
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """Decompose a pair of +/-B measurements into B-symmetric and B-antisymmetric components.

    The standard textbook decomposition for separating Rxx-like (longitudinal,
    even in B) and Rxy-like / anomalous-Hall (transverse, odd in B) parts of a
    measurement taken at +B and -B.

    Sign convention: ``z_sym = (z_pos + z_neg) / 2`` and
    ``z_asym = (z_pos - z_neg) / 2``. NaNs propagate through arithmetic.

    Args:
        z_pos: Data measured at +B. Any shape.
        z_neg: Data measured at -B. Same shape as ``z_pos``.

    Returns:
        ``(z_sym, z_asym)`` where ``z_sym`` is the B-symmetric (Rxx-like)
        component and ``z_asym`` is the B-antisymmetric (Rxy-like / AH)
        component. Both have the same shape as the inputs.
    """
    z_sym = (z_pos + z_neg) / 2
    z_asym = (z_pos - z_neg) / 2
    return z_sym, z_asym
