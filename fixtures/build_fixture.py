"""Rebuild the safe, deterministic fixture; never used inside consensus."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
SPEC = {
    "title": "Bounded integer clamp v1",
    "specification": "A pure Python clamp(value, low, high) returns the nearest boundary for out-of-range integers and preserves in-range integers. It raises ValueError when low exceeds high. This synthetic package is for static conformance review, not execution by validators.",
    "mandatory": [
        {"id": "R_BOUNDS", "text": "Values below low return low; values above high return high; in-range values including both endpoints are unchanged.", "critical": True},
        {"id": "R_INVALID", "text": "If low > high, raise ValueError before returning any value.", "critical": True},
        {"id": "R_PURE", "text": "Function has no network, filesystem, process, or mutable global side effects.", "critical": True},
    ],
    "allowed_deviations": ["Use min/max instead of explicit boundary branches."],
    "forbidden_deviations": ["Silently swap inverted bounds instead of raising ValueError."],
    "evidence_requirements": [
        {"id": "E_SOURCE", "text": "Complete implementation source must be present."},
        {"id": "E_TESTS", "text": "Complete runnable unittest source and its actual captured output covering below/above/interior/endpoints/inverted bounds must be present."},
    ],
    "evaluation_rules": "Review source and test coverage together. Observing bundled results supports only this source and test suite, not universal correctness or proof of execution provenance. The fixture requires ordinary integer inputs only; other input types are outside scope.",
}
SOURCE = '''def clamp(value, low, high):
    if low > high:
        raise ValueError("inverted bounds")
    return min(high, max(low, value))
'''
TESTS = '''import unittest
from clamp import clamp

class ClampTests(unittest.TestCase):
    def test_below(self):
        self.assertEqual(clamp(-8, 0, 5), 0)
    def test_above(self):
        self.assertEqual(clamp(9, 0, 5), 5)
    def test_interior(self):
        self.assertEqual(clamp(3, 0, 5), 3)
    def test_endpoints(self):
        self.assertEqual(clamp(0, 0, 5), 0)
        self.assertEqual(clamp(5, 0, 5), 5)
    def test_inverted(self):
        with self.assertRaises(ValueError):
            clamp(3, 5, 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
'''
if __name__ == "__main__":
    import subprocess
    import sys
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "clamp.py").write_text(SOURCE)
        Path(tmp, "test_clamp.py").write_text(TESTS)
        run = subprocess.run([sys.executable, "test_clamp.py"], cwd=tmp, capture_output=True, text=True, check=True)
    # Omit nondeterministic elapsed time; retain actual individual results + summary.
    output = "\n".join(line for line in (run.stdout + run.stderr).splitlines() if not line.startswith("Ran 5 tests in"))
    package = {"artifact": SOURCE, "tests": TESTS, "results": output, "notes": "Synthetic bounded-clamp fixture. The fixture builder ran these five unittest methods locally. Validators inspect evidence and do not execute it. No universal or independently authenticated test execution claim."}
    for name, data in (("specification.json", SPEC), ("evidence.json", package)):
        ROOT.joinpath(name).write_text(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    print(output)
