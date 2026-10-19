# SpecSignal

A standalone GenLayer Intelligent Contract that adjudicates technical artifact conformance against an immutable specification and committed public evidence.

Creators deploy a contract with a complete specification: mandatory requirements, critical flags, allowed and forbidden deviations, required evidence, and interpretation rules. Anyone can commit a bounded implementation/test/results package and anyone can evaluate it. GenLayer leaders and validators independently retrieve **both** commit-pinned files, check their exact UTF-8 bytes, and inspect source, test coverage and claimed results together. Every normalized finding must agree before deterministic code derives `PASS`, `PARTIAL`, `FAIL`, or `INCONCLUSIVE`.

## Why GenLayer is central

Natural-language requirements, materiality, allowed deviations and the strength of test evidence require interpretation. GenLayer performs that interpretation inside consensus; there is no off-chain verdict server or administrator choosing outcomes. Hashes, ownership, timestamps, limits, replay protection, lifecycle and decision hashes are ordinary deterministic code. The custom Equivalence Principle callback re-fetches both documents and repeats the complete assessment, comparing every categorical finding rather than accepting a leader's verdict or merely its schema.

## State and lifecycle

One contract = one immutable specification. `submit(url, sha256, byte_length, nonce)` creates an immutable package commitment. `evaluate(submission_id)` appends exactly one terminal decision. A new package with different bytes and a fresh nonce is required for a revision; earlier decisions never change. Even an `INCONCLUSIVE` decision is terminal for its submission. Each decision commits the previous decision hash. `close()` is owner-only, requires at least one evaluation and no pending submissions, and permanently disables all writes. No escrow, token, upgrade function, wallet-connect or frontend.

| Precedence | Deterministic result |
| --- | --- |
| Critical requirement violated; all requirements violated; forbidden deviation present; or material unlisted deviation | FAIL |
| Otherwise, unknown requirement/deviation; missing/unsupported required evidence; or insufficient test support | INCONCLUSIVE |
| Otherwise, noncritical violation; nonmaterial unlisted deviation; or contradicted test claim | PARTIAL |
| All remaining cases | PASS |

Requirements are mapped by locked array order to stable IDs. Reports expose each requirement's `SATISFIED`/`VIOLATED`/`UNKNOWN`, required evidence support, presence of every allowed/forbidden deviation, unlisted deviation materiality and test support. There is deliberately no free-form model rationale in the committed result, so validators compare the entire normalized report without prose variation. Allowed deviations never excuse a mandatory violation. Definitive serious failure takes precedence over uncertainty elsewhere.

## Evidence format and limits

Only canonical `https://raw.githubusercontent.com/<owner>/<repo>/<40 lowercase hex commit>/<safe path>` is accepted. Branches, queries, fragments, percent escapes, credentials and dot/empty path segments are rejected. This is a narrow source policy, not a general-purpose crawler. Exact SHA-256 and declared byte length are checked before parsing. Specification content fetched during evaluation must also match the locked specification. JSON duplicate keys are rejected. Both specification and package are limited to 24,000 UTF-8 bytes; packages contain exactly four nonempty strings (`artifact`, `tests`, `results`, `notes`), each at most 12,000 characters. There are 1–12 mandatory and 1–12 evidence requirements, at most eight entries per deviation list, and at most 128 submissions. See source for text/ID/nonce bounds.

## Reproduce checks

Python 3.12+:

```sh
pip install -r requirements-dev.txt
genvm-lint check contracts/specsignal.py
pytest -q
python fixtures/build_fixture.py
```

The fixture builder really runs five safe clamp tests, then bundles the source, test code and captured output. Only the variable elapsed-time line is removed. GenLayer validators **inspect** this package; they do not execute arbitrary submitted code. Direct tests pin the stable v0.2.16 SDK artifacts (the upstream latest tag can be a release candidate without universal test artifacts) and use the official SDK and mocked web/model responses; explicitly invoked validator callbacks test independent re-fetch and disagreement. They do not replace the recorded live Full Consensus demonstration.

## Interface

- Constructor: `specification_json`, `specification_url`. Preserve exact file bytes. The bundled fixture JSON has no trailing newline so Studio text inputs preserve it exactly.
- Writes: `submit(evidence_url, sha256, byte_length, nonce) -> submission_id`; `evaluate(submission_id)`; `close()`.
- Views: `get_specification()`, `get_submission(id)`, `get_decision(id)`, `get_history(index)`, `get_state()`. JSON strings keep the ABI simple. History is zero-indexed.
- Decision hash: SHA-256 of sorted-key, compact, ASCII-escaped JSON of the complete decision **without** `decision_hash`. UTF-8 encoding; no trailing newline. This includes contract address, spec/evidence commitments, submission, transaction timestamp, sequence and predecessor.

See [SECURITY.md](SECURITY.md), [DEPLOYMENT.md](DEPLOYMENT.md) and [live verification](docs/LIVE_VERIFICATION.md).

## Current official references

Reviewed 2026-10-19: [development setup](https://docs.genlayer.com/developers/intelligent-contracts/tooling-setup), [non-determinism](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism), [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [web access](https://docs.genlayer.com/developers/intelligent-contracts/features/web-access), [transaction context](https://docs.genlayer.com/developers/intelligent-contracts/features/transaction-context), [linter](https://docs.genlayer.com/api-references/genlayer-linter), [Direct Mode](https://docs.genlayer.com/api-references/genlayer-test/direct), [networks](https://docs.genlayer.com/developers/networks).

The dependency header pins the supported runner used in official examples. SDK validation and direct execution establish the exact API: `gl.nondet.web.get(...).status` and `.body`, `gl.nondet.exec_prompt`, `gl.vm.run_nondet_unsafe`, `gl.vm.Return`, `TreeMap`/`DynArray` and sized storage integers. Some docs snippets use `status_code`/`gl.UserError`; those are not exported by this pinned SDK and are intentionally not used. Transaction timestamps use GenVM's deterministic `datetime.now(timezone.utc)`, never a web clock.

MIT licensed. Synthetic demonstration; verdicts assess committed evidence under the locked specification, not universal correctness, security certification or independently authenticated test execution.
