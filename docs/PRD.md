# Product Requirements Document (PRD)

## Problem Statement
Standard code coverage metrics (e.g., lines covered) are insufficient because they only prove code was executed, not that it was genuinely asserted. We need a way to prove that the test suite actually catches subtle bugs in the business logic.

## User Stories & Acceptance Criteria

**1. Blocking Weak Tests**
*As a PR author, I want the gate to block my pull request if a mutant survives, so that I am prevented from merging code with weak test assertions.*
- **Acceptance Criteria:**
  - Given a pull request with an AI-generated test suite, when the mutation engine runs and 1 out of 5 mutants survives (returncode 0 from pytest), then the gate returns a `fail` verdict (exit code 1).
  - Given a test suite that catches all 5 mutants, when the gate runs, then the verdict is `pass` (exit code 0).

**2. Plain-English Explanations**
*As a PR author, I want the system to provide a plain-English explanation for why a mutant survived, so that I can easily understand what assertion to add without reading raw JSON.*
- **Acceptance Criteria:**
  - Given a surviving mutant, when the gate processes the results, then the LLM explainer generates a 1-2 sentence explanation naming the specific missing assertion.
  - Given the LLM API times out or fails, then the system safely falls back to a templated explanation string rather than hanging.

**3. CI Visibility**
*As a code reviewer, I want to see the test honesty summary directly in the GitHub Actions step summary, so that I can verify the test suite's strength without leaving the PR page.*
- **Acceptance Criteria:**
  - Given a completed gate run, when the results are finalized, then a markdown summary showing the number of mutants tested, caught, and survived is appended to `$GITHUB_STEP_SUMMARY`.
  - If the gate fails, the step summary explicitly lists the surviving mutations and their plain-English explanations.

**4. Visual Mutation Dashboard**
*As a PR author, I want to see a visual dashboard of the mutation results, so that I can quickly identify which files and lines have surviving mutants.*
- **Acceptance Criteria:**
  - Given the frontend loads the contract JSON, when the dashboard renders, then it displays a Verdict Card (Pass/Blocked) and a Stats Card (Tested/Caught/Survived).
  - When mutations survive, the dashboard renders individual Mutant Cards highlighting the file, line number, operator, and explanation.

**5. Protecting Money-Critical Logic**
*As an owner of money-critical code, I want the mutation gate to specifically target edge cases in pricing logic (like discount bounds and off-by-one errors), so that financial errors cannot be merged.*
- **Acceptance Criteria:**
  - Given a PR modifying `demo-repo/src/pricing.py`, when the mutation engine runs, it injects specific logic flaws (e.g., changing `<` to `<=`).
  - If the test suite fails to assert the exact boundary condition, the gate identifies the exact line in `pricing.py` and blocks the merge.

## Traceability Table

| User Story | Implementing file(s) | Test file(s) |
|---|---|---|
| 1. Blocking Weak Tests | `backend/gate_service/gate.py`, `backend/mutation_engine/runner.py` | `backend/tests/test_gate.py`, `backend/tests/test_runner.py` |
| 2. Plain-English Explanations | `backend/llm_explainer/service.py`, `backend/llm_explainer/prompt.py` | `backend/tests/test_service.py`, `backend/tests/test_prompt.py` |
| 3. CI Visibility | `backend/gate_service/gate.py` | `backend/tests/test_gate.py` |
| 4. Visual Mutation Dashboard | `frontend/src/App.jsx`, `frontend/src/components/VerdictCard.jsx`, `frontend/src/components/MutantCard.jsx`, `frontend/src/components/StatsCard.jsx` | N/A (Frontend uses Playwright e2e in CI) |
| 5. Protecting Money-Critical Logic | `backend/mutation_engine/operators.py`, `backend/mutation_engine/runner.py`, `demo-repo/src/pricing.py` | `backend/tests/test_operators.py`, `backend/tests/test_runner.py` |

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
