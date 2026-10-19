# Deployment and verification

Use hosted GenLayer Studio's **GenLayer Studio** network (Studionet), built-in account and **Normal (Full Consensus)** execution. No external wallet or funding is needed for this demonstration. Never change account credentials or export private keys.

1. Install pinned development requirements; run `genvm-lint check contracts/specsignal.py` and `pytest -q`.
2. Run `python fixtures/build_fixture.py`; ensure fixtures are committed. Commit the final contract to main and record its Git SHA and `sha256sum contracts/specsignal.py`. Do not modify contract bytes after deployment.
3. Form raw specification/evidence URLs using that immutable 40-character Git commit. Fetch them and verify byte lengths/hashes against the local files.
4. Import the exact `contracts/specsignal.py` file into Studio. Open Run and Debug and select **Normal (Full Consensus)**. Constructor inputs are the complete exact `fixtures/specification.json` text and its commit-pinned raw URL. Deploy and wait for FINALIZED with GenVM SUCCESS.
5. Call `get_state()` and `get_specification()` and compare commitments/exact text. Call `submit` with raw evidence URL, SHA-256, UTF-8 byte length and a fresh nonce. Wait for finalized success and read the returned submission ID from the transaction.
6. Call `evaluate(submission_id)` in Full Consensus. Inspect leader/validator consensus, wait for finalized success, then read `get_decision(id)` and `get_history(0)`. Independently recompute `decision_hash` after removing its field from parsed JSON (see README).
7. Call owner-only `close()` after every submission has been evaluated. Wait for finality and read `get_state()` again. `closed: true`, submitted/evaluated counters and close timestamp attest application final state. Transaction finality is separate from this application closure.
8. Read deployed source back from Explorer/RPC and compare byte length and SHA-256 with the committed file. Record actual transaction hashes, address, receipts, state, decision and source identity in `docs/LIVE_VERIFICATION.md` and `docs/live.json`.
9. Commit documentation only and push main. Record deployed-source commit separately from the later documentation commit. No self-referential final Git SHA is embedded in its own commit.

## Network/API reference

Official current docs: https://docs.genlayer.com/developers/networks and https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio . Studio UI is https://studio.genlayer.com ; hosted RPC https://studio.genlayer.com/api ; Explorer https://explorer-studio.genlayer.com . Studio accounts are test accounts only. Accepted/pending is not finalized; inspect the GenLayer consensus receipt rather than only the outer EVM transaction.

## Verify a recorded result

```sh
python scripts/verify_live.py
```

The offline verifier checks the canonical contract SHA-256, fixture hashes, decision hash, spec/evidence linkage, chain head and final counters from recorded readback. It does not itself establish network finality; recorded receipt/Explorer links establish that independently. Live verification details are only populated after actual deployment/readback, never fabricated.
