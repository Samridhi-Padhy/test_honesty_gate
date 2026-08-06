# Test-Honesty Gate

Test-Honesty Gate is an automated mutation testing and LLM-explanation pipeline designed to ensure your unit tests genuinely catch bugs rather than just achieving high line coverage.

## Running the Gate
Run the entire gate pipeline locally in one command:
```bash
python gate check local
```

## Repository Layout
- `backend/`: Core logic (mutation engine, gate service, API, LLM explainer).
- `demo-repo/`: The target repository tested by the gate.
- `frontend/`: (Optional) UI for displaying gate results.
- `docs/`: Technical specifications and changelogs.

## CI Integration
In CI environments, the gate is invoked automatically via `.github/workflows/ci.yml`. It will block PRs if the test suite fails to catch the known MVP mutations.
