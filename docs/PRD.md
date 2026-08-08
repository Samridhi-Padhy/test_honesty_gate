# Product Requirements Document (PRD)

## Problem Statement
Standard code coverage metrics (e.g., lines covered) are insufficient because they only prove code was executed, not that it was genuinely asserted. We need a way to prove that the test suite actually catches subtle bugs in the business logic.

## MVP Scope Lock
To prove the concept quickly and deterministically, the MVP is strictly limited to 5 hardcoded operators applied to a specific demo project (`demo-repo`):
1. `==` to `!=`
2. `<` to `<=` (boundary shift)
3. Off-by-one loop/index bound
4. Negate boolean return
5. Drop `is None` guard

## Explicit Non-Goals
- **No General Mutation Engine**: We are not building a fully dynamic engine that discovers targets at runtime.
- **No Arbitrary Repos**: The tool is hardcoded to test `demo-repo` only.
- **LLM Does Explanation Only**: The LLM will only explain why a mutant survived. It will **not** attempt to fix the mutant, write new code, or fix the test suite.

## User Stories and Acceptance Criteria

### 1. Developer blocked by weak tests
**Story:** As a developer, I want my PR blocked with a clear reason when I submit code with weak assertions, so I don't merge brittle tests.
**Acceptance Criteria:**
- Running `./gate check local` against a weak test suite exits with code 1.
- The output JSON contract explicitly lists the surviving mutant's `operator` (e.g., `equality_flip`), `location` (e.g., `src/pricing.py:28`), and an `explanation`.
- `backend/gate_service/gate.py` writes a markdown summary detailing surviving mutants to `$GITHUB_STEP_SUMMARY` if the environment variable is present.

### 2. Developer trusting the gate's isolation
**Story:** As a developer, I want to trust that the mutation gate won't permanently break my local codebase, so I can run it safely on my working branch.
**Acceptance Criteria:**
- `backend/mutation_engine/runner.py` contains a `finally:` block in `run_mutant()` that strictly calls `_write_source(original)`, ensuring `demo-repo/src/pricing.py` is always restored even if a pytest subprocess crashes or times out.

### 3. Frontend engineer surviving an LLM outage
**Story:** As a frontend engineer, I want the UI to remain functional even if the LLM backend is down or rate-limited, so my development workflow isn't blocked.
**Acceptance Criteria:**
- Sending a request to `GET /gate?mock=true` (or setting `MOCK_MODE=true` in `.env`) returns a valid static JSON contract directly from `llm_explainer.mock_input.mock_contract()`.
- The mock response bypasses the mutation engine and LLM calls in `backend/api/app.py`.

### 4. New contributor running from a clean clone
**Story:** As a new contributor, I want to run the gate check immediately after cloning, so I don't waste time configuring complex dependencies.
**Acceptance Criteria:**
- Executing `python gate check local` successfully runs the 5 mutations strictly utilizing the dependencies listed in `backend/requirements.txt`, without requiring external databases, Docker, or manual ast-parsing configurations.
