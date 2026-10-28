"""Guard against re-introducing banned dependencies.

`qcodes-contrib-drivers` was dropped in favour of the vendored
`drivers.QDAC2` (see README.md, "QDAC2 driver"). It pulled in an `autobahn`
subtree (`msgpack`, `ujson`, `cbor2`, ...) that carried a stream of
Dependabot alerts on a package nothing imported. This test fails if either
package creeps back into `pyproject.toml` or the resolved `uv.lock`.
"""
import unittest
from pathlib import Path

# Re-vendor the single QDAC2 file instead of re-adding either of these.
BANNED = ("qcodes-contrib-drivers", "autobahn")


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "uv.lock").is_file():
            return parent
    raise AssertionError("could not locate repo root (no uv.lock found)")


class BannedDepsTest(unittest.TestCase):
    def test_not_in_pyproject(self):
        text = (_repo_root() / "pyproject.toml").read_text()
        for pkg in BANNED:
            self.assertNotIn(
                f'"{pkg}"', text, f"{pkg} is banned; re-vendor instead"
            )

    def test_not_in_lock(self):
        text = (_repo_root() / "uv.lock").read_text()
        for pkg in BANNED:
            self.assertNotIn(
                f'name = "{pkg}"', text, f"{pkg} is banned; re-vendor instead"
            )


if __name__ == "__main__":
    unittest.main()
