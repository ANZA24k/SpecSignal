# SpecSignal live verification

## Deployment identity

- Network: hosted GenLayer Studio / Studionet, built-in Studio account, Normal (Full Consensus).
- Contract: [0xE60523cF6F556F591a78651cbe51c50066aE30B9](https://explorer-studio.genlayer.com/address/0xE60523cF6F556F591a78651cbe51c50066aE30B9).
- Deployed source/fixture commit: [`12ddcf12e200775319fd9df1276c754ffcdfab21`](https://github.com/ANZA24k/SpecSignal/commit/12ddcf12e200775319fd9df1276c754ffcdfab21).
- Canonical source: `contracts/specsignal.py`, 14,879 bytes.
- Source SHA-256: `371eda70e8e8229e4ff55688fd83786b08a24eae111056dd63603ba288d14f70`.
- Complete Explorer source readback matches repository bytes exactly. No code changes or redeployments followed this deployment.
- The later documentation commit is the repository HEAD containing this record; its SHA is reported separately, avoiding a self-referential Git hash.

## Finalized transactions

| Action | Transaction | GenVM | Consensus | Status |
| --- | --- | --- | --- | --- |
| deploy | [0xa8050eb36de809ecaab11f11abd8f48dacf7b221ad60b64e09fd44138386de07](https://explorer-studio.genlayer.com/tx/0xa8050eb36de809ecaab11f11abd8f48dacf7b221ad60b64e09fd44138386de07) | SUCCESS | MAJORITY_AGREE | FINALIZED |
| submit | [0xa7bf9e2a2538c882bced36e73258f60043fec7e81775f695e469601526b524ac](https://explorer-studio.genlayer.com/tx/0xa7bf9e2a2538c882bced36e73258f60043fec7e81775f695e469601526b524ac) | SUCCESS | MAJORITY_AGREE | FINALIZED |
| evaluate | [0xd897195c48bdfeda171ccfe04ca2769bc5afff6e14fa5abd81a92c0037812637](https://explorer-studio.genlayer.com/tx/0xd897195c48bdfeda171ccfe04ca2769bc5afff6e14fa5abd81a92c0037812637) | SUCCESS | MAJORITY_AGREE | FINALIZED |
| close | [0x096ec68f1d4c3eea970d271670effbaa7b8e7d82505c0a7efec96a2abdcea571](https://explorer-studio.genlayer.com/tx/0x096ec68f1d4c3eea970d271670effbaa7b8e7d82505c0a7efec96a2abdcea571) | SUCCESS | MAJORITY_AGREE | FINALIZED |

Explorer independently lists all four calls as FINALIZED / SUCCESS. The evaluation used real web retrieval and model interpretation, not simulation or Leader Only mode. Three validators agreed; Studio cancelled the other two executions after quorum (displayed ERROR / Idle, not disagreeing votes). This is a majority consensus demonstration, not a claim of five completed agreeing executions.

## Immutable public inputs

- [fixtures/specification.json](https://raw.githubusercontent.com/ANZA24k/SpecSignal/12ddcf12e200775319fd9df1276c754ffcdfab21/fixtures/specification.json): 1414 bytes, SHA-256 `46a747a4a0bd3ace19d5e20efb62d72e956fce869e0c0f130ad4e446c29c3302`.
- [fixtures/evidence.json](https://raw.githubusercontent.com/ANZA24k/SpecSignal/12ddcf12e200775319fd9df1276c754ffcdfab21/fixtures/evidence.json): 1344 bytes, SHA-256 `cda96514a3793f15419a54e41bdb90e6b8ec1a16206294662c3c0997cbe9a729`.

Both raw URLs were fetched and compared against local fixture bytes before deployment. Specification and submission views were read back and verified. Fixture JSON omits a trailing newline to preserve exact bytes through Studio's single-line input.

## Stored decision

Submission ID: `a7c55146285149dbeb84efc46b823d61f27f79b33b7f2980a5c48b49d9697197`.

Decision hash: `8f2984d6235a2e61fe50bd3fa09db664f5fb3f9ddfc3c5471692844b7656877a`.

| Locked item | Finding |
| --- | --- |
| R_BOUNDS | SATISFIED |
| R_INVALID | SATISFIED |
| R_PURE | SATISFIED |
| E_SOURCE | SUPPORTED |
| E_TESTS | SUPPORTED |
| Allowed min/max deviation | PRESENT |
| Forbidden bounds-swapping deviation | ABSENT |
| Unlisted deviation | NONE |
| Test/results support | SUPPORTED |
| Final result | PASS |

Evaluation time: `2026-10-19T10:57:08.028815+00:00`. Sequence: 1. Previous decision hash: empty (first entry). `get_history(0)` exactly matches `get_decision(submission_id)`. The offline verifier recomputes submission and decision hashes and checks all commitment links.

## Final application state

```json
{
  "closed": true,
  "closed_at": "2026-10-19T10:59:02.760625+00:00",
  "created_at": "2026-10-19T10:54:40.109565+00:00",
  "evaluated": 1,
  "owner": "0xe74B0C822c1af78046ca0304b2aa69160c6cc3b8",
  "specification_hash": "46a747a4a0bd3ace19d5e20efb62d72e956fce869e0c0f130ad4e446c29c3302",
  "specification_length": 1414,
  "specification_url": "https://raw.githubusercontent.com/ANZA24k/SpecSignal/12ddcf12e200775319fd9df1276c754ffcdfab21/fixtures/specification.json",
  "submitted": 1,
  "version": "specsignal-v1"
}
```

All mutations are disabled by `closed: true`. Reviewers can inspect the frozen demonstration or deploy a new instance for another specification. No balances were escrowed or paid.

## Validation

- GenVM lint: passed, 3 checks; SDK validation passed, 8 methods (5 view, 3 write).
- Direct Mode: 38 passed, including separate validator callbacks, differing findings, independent re-fetch, inaccessible/malformed evidence, UTF-8 commitments, hash-chain verification, authority, cap, replay and terminal guards.
- Safe fixture: five actual local unittest methods passed. Bundled source/tests/output are public; validators inspect rather than execute the package.
- [Implementation CI](https://github.com/ANZA24k/SpecSignal/actions/runs/39240743671): success.
- `python scripts/verify_live.py`: passed; verifies the recorded source, files, submission, decision, history, receipt summaries and final state offline. It does not claim fresh RPC finality.
- Readback: Explorer Contract / Read Contract after all four transactions finalized. RPC was accessible during the original run; a later runtime received HTTP 403 / 1010, so final readback was completed through Explorer. No further deployment was needed.

See [machine-readable record](live.json), [Explorer proof](explorer-finalized.jpg), [security model](../SECURITY.md) and [deployment guide](../DEPLOYMENT.md).

## Submission text

Recommended tags: Intelligent Contracts, Developer Tools, Verification, AI Consensus (choose the nearest available portal labels).

Notes / Description (969 characters):

SpecSignal verifies technical artifact conformance against an immutable specification. Creators lock mandatory requirements, allowed/forbidden deviations, evidence requirements and evaluation rules. Leaders and validators independently retrieve commit-pinned implementation/test/results packages and the locked specification, verify exact SHA-256 and byte lengths, then assess requirements, deviations and test support. Deterministic rules derive PASS, PARTIAL, FAIL or INCONCLUSIVE. Safeguards include canonical HTTPS sources, evidence limits, strict JSON, replay protection, append-only hash-linked history and terminal immutability. The Studionet fixture achieved PASS in real Full Consensus. Deployment, submission, evaluation and closure all finalized successfully; deployed source matches GitHub byte for byte. Includes 38 passing Direct Mode tests, five fixture tests, GenVM lint/validation and CI. Validators inspect evidence rather than execute submitted code.
