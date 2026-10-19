"""Verify source/fixture commitments and canonical decision readback offline."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
record = json.loads((root / "docs/live.json").read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha((root / "contracts/specsignal.py").read_bytes()) == record["source_sha256"]
for name, info in record["files"].items():
    data = (root / name).read_bytes()
    assert sha(data) == info["sha256"] and len(data) == info["byte_length"]
decision = record["decision"].copy()
claimed = decision.pop("decision_hash")
assert sha(json.dumps(decision, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()) == claimed
assert decision["spec_hash"] == record["files"]["fixtures/specification.json"]["sha256"]
assert decision["evidence_hash"] == record["files"]["fixtures/evidence.json"]["sha256"]
assert decision["contract"].lower() == record["contract_address"].lower()
assert decision["submission_id"] == record["submission_id"]
assert record["history"] == record["decision"]
assert record["state"]["closed"] is True
assert record["state"]["submitted"] == record["state"]["evaluated"] == 1
print("Source, fixtures, decision hash, history and terminal state verified")
