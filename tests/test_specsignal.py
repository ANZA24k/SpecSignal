"""Direct GenVM SDK execution plus independently invoked validator callbacks."""
import hashlib
import json
from pathlib import Path
import pytest
from gltest.direct import VMContext, deploy_contract, create_test_addresses

ROOT = Path(__file__).resolve().parents[1]
URL = "https://raw.githubusercontent.com/ANZA24k/SpecSignal/" + "a" * 40 + "/fixtures/"
SPEC_TEXT = (ROOT / "fixtures/specification.json").read_text()
EVIDENCE = (ROOT / "fixtures/evidence.json").read_text()
PASS = {"requirements": ["SATISFIED"] * 3, "evidence": ["SUPPORTED"] * 2,
        "allowed": ["PRESENT"], "forbidden": ["ABSENT"], "unlisted": "NONE", "test_support": "SUPPORTED"}

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

@pytest.fixture
def env():
    vm = VMContext()
    accounts = create_test_addresses()
    with vm.activate():
        vm.sender = accounts[0]
        vm.warp("2026-10-19T12:00:00Z")
        vm.validate_pickling = True
        contract = deploy_contract(ROOT / "contracts/specsignal.py", vm, SPEC_TEXT, URL + "specification.json", sdk_version="v0.2.16")
        yield vm, contract, accounts

def mocks(vm, report=PASS, evidence=EVIDENCE, spec=SPEC_TEXT, status=200):
    vm.clear_mocks()
    vm.mock_web(r".*/specification.json", {"status": 200, "body": spec})
    vm.mock_web(r".*/evidence.json", {"status": status, "body": evidence})
    vm.mock_llm("SPECSIGNAL_CONFORMANCE_V1", json.dumps(report))

def submit(c, evidence=EVIDENCE, nonce="demo"):
    return c.submit(URL + "evidence.json", sha(evidence), len(evidence.encode()), nonce)

def test_full_lifecycle_hash_readback_and_terminal_guards(env):
    vm, c, accounts = env
    sid = submit(c)
    vm.sender = accounts[1]  # permissionless evaluation, independent caller
    mocks(vm)
    c.evaluate(sid)
    assert vm.run_validator() is True
    decision = json.loads(c.get_decision(sid))
    assert decision["outcome"] == "PASS"
    h = decision.pop("decision_hash")
    assert h == sha(canon(decision))
    assert c.get_history(0) == c.get_decision(sid)
    assert json.loads(c.get_submission(sid))["submitter"]  .lower() == "0x" + accounts[0].hex()
    with vm.expect_revert("Terminal evaluation"):
        c.evaluate(sid)
    with vm.expect_revert("Owner only"):
        c.close()
    vm.sender = accounts[0]
    c.close()
    frozen = c.get_state()
    for action in (lambda: submit(c, nonce="new"), lambda: c.evaluate(sid), c.close):
        with vm.expect_revert("Contract closed"):
            action()
    assert c.get_state() == frozen
    assert json.loads(frozen)["closed"] is True

@pytest.mark.parametrize("change,expected", [
    ({"requirements": ["SATISFIED", "VIOLATED", "SATISFIED"]}, "FAIL"),
    ({"requirements": ["SATISFIED", "UNKNOWN", "SATISFIED"]}, "INCONCLUSIVE"),
    ({"forbidden": ["PRESENT"]}, "FAIL"),
    ({"forbidden": ["UNKNOWN"]}, "INCONCLUSIVE"),
    ({"unlisted": "MATERIAL"}, "FAIL"),
    ({"unlisted": "NONMATERIAL"}, "PARTIAL"),
    ({"evidence": ["SUPPORTED", "MISSING"]}, "INCONCLUSIVE"),
    ({"test_support": "CONTRADICTED"}, "PARTIAL"),
    ({"test_support": "INSUFFICIENT"}, "INCONCLUSIVE"),
])
def test_deterministic_outcomes(env, change, expected):
    vm, c, _ = env
    sid = submit(c)
    mocks(vm, {**PASS, **change})
    c.evaluate(sid)
    assert json.loads(c.get_decision(sid))["outcome"] == expected

@pytest.mark.parametrize("variant,expected", [
    ("changed", "EVIDENCE_INTEGRITY"), ("http", "EVIDENCE_HTTP"),
    ("spec", "SPEC_INTEGRITY"), ("schema", "EVIDENCE_SCHEMA"),
    ("duplicate", "EVIDENCE_UNREADABLE"), ("json", "EVIDENCE_UNREADABLE"),
])
def test_bad_evidence_is_conservative(env, variant, expected):
    vm, c, _ = env
    data = {"schema": '{"hello":"world"}', "duplicate": '{"a":1,"a":2}', "json": '{broken'}.get(variant, EVIDENCE)
    sid = submit(c, data)
    mocks(vm, evidence=data + " " if variant == "changed" else data,
          spec=SPEC_TEXT + " " if variant == "spec" else SPEC_TEXT, status=404 if variant == "http" else 200)
    c.evaluate(sid)
    dec = json.loads(c.get_decision(sid))
    assert dec["outcome"] == "INCONCLUSIVE"
    assert dec["assessment"] == {"error": expected}
    assert vm.run_validator() is True

def test_validator_independence_and_all_fields(env):
    vm, c, _ = env
    sid = submit(c)
    mocks(vm)
    c.evaluate(sid)
    assert vm.run_validator() is True
    for field, value in [("requirements", ["SATISFIED", "UNKNOWN", "SATISFIED"]),
                         ("allowed", ["ABSENT"]), ("test_support", "CONTRADICTED")]:
        forged = {"report": {**PASS, field: value}}
        assert vm.run_validator(leader_result=forged) is False
    assert vm.run_validator(leader_error=ValueError("bad leader")) is False
    mocks(vm, evidence=EVIDENCE + " ")
    assert vm.run_validator() is False  # validator actually re-fetches artifact
    mocks(vm, spec=SPEC_TEXT + " ")
    assert vm.run_validator() is False  # and independently re-fetches specification

@pytest.mark.parametrize("report", [
    {**PASS, "outcome": "PASS"}, {**PASS, "requirements": []},
    {**PASS, "requirements": ["PASS"] * 3}, {**PASS, "unlisted": True},
])
def test_malformed_model_does_not_finalize(env, report):
    vm, c, _ = env
    sid = submit(c)
    mocks(vm, report)
    with pytest.raises(Exception):
        c.evaluate(sid)
    assert json.loads(c.get_state())["evaluated"] == 0
    with vm.expect_revert("No decision"):
        c.get_decision(sid)

@pytest.mark.parametrize("url", [
    "http://raw.githubusercontent.com/a/b/" + "a" * 40 + "/e.json",
    "https://example.org/e.json", URL.replace("a" * 40, "main") + "e.json",
    URL + "../e.json", URL + "e.json?raw=1", URL + "%2e/e.json", URL + "e.json#x",
    URL + "/e.json",
])
def test_noncanonical_urls_rejected(env, url):
    vm, c, _ = env
    with pytest.raises(Exception):
        c.submit(url, sha(EVIDENCE), len(EVIDENCE.encode()), "url")
    assert json.loads(c.get_state())["submitted"] == 0

def test_replay_authority_pending_and_append_only_chain(env):
    vm, c, _ = env
    with vm.expect_revert("Pending or empty"):
        c.close()
    sid = submit(c)
    with vm.expect_revert("Pending or empty"):
        c.close()
    with vm.expect_revert("Nonce replay"):
        submit(c, EVIDENCE + " ")
    with vm.expect_revert("Duplicate evidence"):
        submit(c, nonce="other")
    mocks(vm)
    c.evaluate(sid)
    first = c.get_history(0)
    next_data = EVIDENCE + " "
    second = submit(c, next_data, "revision2")
    mocks(vm, evidence=next_data)
    c.evaluate(second)
    assert c.get_history(0) == first
    assert json.loads(c.get_history(1))["previous_decision_hash"] == json.loads(first)["decision_hash"]
    assert json.loads(c.get_state())["evaluated"] == 2
    with vm.expect_revert("Unknown submission"):
        c.evaluate("f" * 64)

@pytest.mark.parametrize("mutation", [
    lambda s: s.update(extra="x"), lambda s: s.update(mandatory=[]),
    lambda s: s["mandatory"].append(s["mandatory"][0]),
    lambda s: s["mandatory"][0].update(critical="true"),
])
def test_bad_locked_spec_rejected(mutation):
    vm = VMContext()
    s = json.loads(SPEC_TEXT)
    mutation(s)
    with vm.activate(), pytest.raises(Exception):
        deploy_contract(ROOT / "contracts/specsignal.py", vm, canon(s), URL + "specification.json", sdk_version="v0.2.16")

def test_limits(env):
    vm, c, _ = env
    for h, size, nonce in [("f" * 63, 100, "a"), ("f" * 64, 24001, "b"), ("f" * 64, 0, "c"), ("f" * 64, 100, "")]:
        with pytest.raises(Exception):
            c.submit(URL + "evidence.json", h, size, nonce)
    # Exercise the real cap through ordinary submissions, without mutating storage.
    for i in range(128):
        c.submit(URL + "evidence.json", sha(str(i)), 1, str(i))
    with vm.expect_revert("Submission cap"):
        c.submit(URL + "evidence.json", sha("extra"), 1, "extra")


def test_noncritical_partial():
    vm = VMContext()
    spec = json.loads(SPEC_TEXT)
    spec["mandatory"][1]["critical"] = False
    text = canon(spec)
    vm.sender = create_test_addresses()[0]
    with vm.activate():
        c = deploy_contract(ROOT / "contracts/specsignal.py", vm, text, URL + "specification.json", sdk_version="v0.2.16")
        sid = submit(c)
        mocks(vm, {**PASS, "requirements": ["SATISFIED", "VIOLATED", "SATISFIED"]}, spec=text)
        c.evaluate(sid)
        assert json.loads(c.get_decision(sid))["outcome"] == "PARTIAL"


def test_unicode_commitment_uses_utf8_bytes(env):
    vm, c, _ = env
    package = json.loads(EVIDENCE)
    package["notes"] += " café λ"
    data = json.dumps(package, ensure_ascii=False)
    sid = submit(c, data)
    mocks(vm, evidence=data)
    c.evaluate(sid)
    assert json.loads(c.get_decision(sid))["outcome"] == "PASS"


def test_missing_web_response_cannot_pass(env):
    vm, c, _ = env
    sid = submit(c)
    vm.clear_mocks()
    c.evaluate(sid)
    assert json.loads(c.get_decision(sid))["assessment"] == {"error": "SPEC_UNREADABLE"}
