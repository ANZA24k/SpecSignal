# Security model

## Boundaries

The deployer locks one complete specification and its canonical public source URL. No method edits the specification, commitments, prior findings or deployed code. The owner can only close once all existing submissions have terminal decisions. Evaluation is permissionless; submission attribution is the actual transaction sender. Constructor and writes are nonpayable. There is no settlement or accounting.

Public evidence is adversarial data. Prompts separate fixed instructions from JSON-encoded specification/evidence and explicitly prohibit embedded instruction following, extra browsing, code execution and assuming that supplied tests ran. Model schema is strict and all output categories are bounded. Prompt separation reduces injection risk but cannot eliminate model errors. Validators independently re-fetch/hash both documents and independently interpret the complete package. They compare every normalized finding; matching outcome alone is insufficient. Validator errors disagree; malformed model output aborts/rotates rather than becoming an accepted verdict.

## Integrity and failure semantics

HTTP non-200, hash or length mismatch, invalid UTF-8, invalid/duplicate-key JSON and invalid package fields yield explicit conservative error assessments, hence INCONCLUSIVE. Each validator must reproduce the same error classification to agree. A validator who can retrieve valid evidence disagrees with a leader claiming retrieval failure. Hash checking happens on raw response bytes before decode/parse. No model can override a byte-integrity failure. The raw transport is supplied by GenVM; the application checks response bytes after download, not a streaming network limit. Commit pinning and exact hashes bind bytes even if transport follows a redirect. The GitHub source policy does not establish author identity or truthfulness.

Submission hashes cannot be reused within a contract. Nonces cannot be reused by the same sender. Submission and decision IDs domain-bind the contract/version and specification; decisions also commit sequence, timestamp and predecessor. A final evaluation cannot be replayed or replaced, including INCONCLUSIVE. New evidence is a separate immutable submission. Closed contracts reject all writes.

## Known limits and availability

- Validators perform static semantic inspection, not sandboxed program execution. Supplied logs can be fabricated; internal consistency is weaker than authenticated execution. Require appropriate provenance in the locked evidence rules for higher assurance.
- Identical category vectors can conceal shared model mistakes. Fine-grained comparison improves scrutiny but does not prove correctness. Ambiguous specifications can prevent consensus and leave state unchanged.
- Commit-pinned GitHub data may become unavailable. A hash binds content, not availability. New evidence cannot repair an old terminal record.
- Open submissions and the fixed cap permit griefing and can delay closure. This is an intentionally permissionless bounded primitive; deploy a new instance for a new specification/cohort. There is no administrative deletion or emergency override.
- Exact categorical agreement may reduce liveness on subjective cases. Never silently weaken consensus to force a demonstration outcome.
- Reports retain categorical findings and commitments, not explanatory prose or source excerpts. Reviewers can map indices to locked IDs and inspect the immutable files.
- No secrets, personal data or proprietary artifacts belong in public evidence.

Report a vulnerability privately to the repository maintainer through their GitHub profile before publishing an exploit. Do not post credentials or private evidence in issues.
