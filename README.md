# Test Honesty Gate
Keeps test suites honest by proving they actually catch bugs.

Built for Deploy or redacted — HowToAlgo x GDG on Campus KIIT, Track B (Developer Productivity Tools).

🔗 **Live dashboard:** [test-honesty-gate.vercel.app](https://test-honesty-gate.vercel.app/) — no install needed. Click through the live AI Test Validation Dashboard to see real mutations evaluated against a test suite in real-time.

## For reviewers — start here
Fastest path, 2 minutes, no install. Open the live dashboard:

- **Verdict Card** — Tells you instantly if the PR is safe to merge. Notice that if any mutant survives, it says "Merge blocked". The text dynamically reflects the exact number of mutants tested and survived.
- **Stats Card** — High-level summary of mutants tested, caught, survived, and the exact duration of the test pipeline.
- **Per-file thresholds** — This is the core innovation. Tests don't just need a good average score; critical files (like `pricing.py`) are held to a strict 75% kill-rate threshold. A weak test on financial code cannot hide behind a passing average.
- **Mutation results** — The heart of the explainer. If a mutant survives, the AI explains *exactly* what assertion the developer needs to add to catch it.

**Try it live:** The dashboard fetches data directly from the live Render backend (`test-honesty-gate.onrender.com`), which runs 7 actual Pytest subprocesses in real-time. It takes about ~30 seconds to compute the gate. It is not a hardcoded screenshot.

## The 5 non-negotiable gate items
| # | Item | Where |
|---|---|---|
| 1 | Architecture document | `docs/ARCHITECTURE.md` |
| 2 | Agent rules | `AGENTS.md` |
| 3 | Working code | live dashboard, or run it yourself below |
| 4 | Custom agent + custom skill | `AGENTS_AND_SKILLS.md` |
| 5 | Green CI/CD pipeline | Actions tab — most recent run |

## Run it yourself, ~10 minutes
```bash
git clone https://github.com/hoursgotviral-dev/test_honesty_gate.git
cd test_honesty_gate

# Install backend dependencies
pip install -r backend/requirements.txt

# Run the deterministic CLI gate against the demo-repo
python gate check local
```

```bash
# Start the frontend
cd frontend
npm install && npm run dev        # http://localhost:5173
```

## The problem
When a developer writes code, they write tests to prove it works. But who tests the tests? 
1. A developer writes a function.
2. A developer writes a test that executes the function but forgets to assert the output.
3. The CI pipeline goes green (100% coverage!).
4. A critical bug is shipped to production.

What it means: The code is executed, but behavior is not verified. "Green" CI is lying to you.

## What we're building
**Test Honesty Gate** makes test quality mathematically provable.

- It deliberately injects 7 targeted bugs (mutants) into the PR's codebase.
- It runs the PR's own test suite against the mutated code.
- If the tests stay green despite the bugs, the tests are dishonest. The gate blocks the PR.
- To prevent developers from guessing what they missed, an **LLM Agent** analyzes the surviving mutant and drafts a specific explanation of what assertion needs to be added.
- **Per-File Thresholds** ensure that high-risk files (like `pricing.py`) must pass a strict kill-rate, independently of the rest of the repo.

## Architecture

### Design principle
**Determinism where determinism is possible.** Exactly one question in this system needs a language model: *why did the test suite miss this bug?* Everything else — mutating ASTs, running Pytest, aggregating per-file thresholds, evaluating the pass/fail verdict — is ordinary computation and is written as such.

This keeps the unreliable surface small and auditable. It also means the deterministic half (the mutation engine) works with no API key at all. If the LLM goes down or runs out of credits, the gate fails-closed securely and uses fallback explanations rather than crashing.

### Flow
```text
demo-repo codebase ──┐
                     ├──> Pytest subprocesses run
mutant injectors ────┘
                     │
           mutants caught vs survived
                     ▼
         ┌──── test-honesty-gate ────┐
         │ pass? fail? per-file?     │
         └────────────┬──────────────┘
       pass           │        fail (mutants survived)
         │            │              │
   CI turns green,    │      LLM Explainer (Gemini / OpenAI)
   Merge Allowed      │      drafts an explanation for each survivor
         │            │              │
         └────────────┴──────> dashboard: Merge Blocked
```

### The custom agent and skill
| Name | Role |
|---|---|
| **Agent** | `mutation-explainer` | Decides why a test suite missed a mutant. Maps the surviving AST change to the test suite gap. |
| **Skill** | `explain-surviving-mutant` | Drafts a human-readable explanation and assertion suggestion. |
*Both are documented in detail in `AGENTS_AND_SKILLS.md`.*

### Safety properties
Enforced in code and covered by tests — not merely intended:
- **Fail-Closed Design**: If the Pytest subprocess times out, hangs, or crashes, the mutant is marked as *survived* (failed).
- **Graceful API Fallbacks**: If the Gemini/OpenAI API is unreachable, times out, or runs out of credits, the system catches the exception and returns hardcoded fallback explanations (e.g. "Add an assertion that exercises the mutated behavior"). It never 500s.
- **Isolated Mutation**: Every mutation reverts itself cleanly using precise string spans before the next one runs.

## Stack
| Concern | Choice | Why |
|---|---|---|
| **Backend** | Python (FastAPI) | Native AST parsing and Pytest subprocess control. |
| **Dashboard** | React + Vite | Clean, rapid client-side rendering for the dashboard. |
| **Engine** | Pytest | Industry standard; used to run the target repo's tests. |
| **LLM** | Gemini / OpenAI | Used exclusively for the `mutation-explainer` agent. |

## Deployment
- **Frontend (Vercel)**: `https://test-honesty-gate.vercel.app`
- **Backend (Render)**: `https://test-honesty-gate.onrender.com`

Render hosts the FastAPI backend via Docker. It performs real mutation testing on the fly. Vercel hosts the React frontend. We have configured the frontend with a 60-second fetch timeout to comfortably accommodate the 25-35 seconds it takes Render to spin up 7 Pytest subprocesses.

## Project structure
```text
backend/
  api/app.py               FastAPI endpoints
  mutation_engine/
    operators.py           Deterministic AST bug injectors
    runner.py              Subprocess Pytest orchestrator
  gate_service/
    gate.py                Thresholds, verdicts, and per-file logic
    service.py             LLM Explainer agent integration
frontend/
  src/
    components/            VerdictCard, FileRiskCard, MutantCard
    api/client.js          Fetch client with 60s timeout
demo-repo/                 The target repository being tested
  src/                     Code to be mutated
  tests/                   Test suite to evaluate
```

## Demo script
1. **The "Dishonest" Test Suite (Current Main)**
   - View the live dashboard: `test-honesty-gate.vercel.app`
   - Observe that `m1`, `m2`, `m3`, `m4`, `m5`, `m7` all **survive**.
   - Notice the "Merge blocked" verdict.
   - Look at `demo-repo/tests/test_pricing.py` on the `main` branch: the tests are skipped with `@pytest.mark.skip`. The tests run "green" in CI, but verify nothing.

2. **The "Honest" Test Suite (Post-Merge)**
   - Merge the open Pull Request into `main`.
   - Render will automatically rebuild the Docker image with the unskipped test suite.
   - Reload the dashboard.
   - Observe that `m1`, `m2`, `m3`, `m4`, `m6` are now **caught**. The kill-rate shoots up, and the threshold turns green!

## Documents
| Document | Contents |
|---|---|
| `README.md` | This file. Setup, pitch, and demo script. |
| `docs/ARCHITECTURE.md` | Full design, data model, safety properties, and per-file thresholds. |
| `AGENTS.md` | Rules for AI agents working in this repo. |
| `AGENTS_AND_SKILLS.md` | The custom agent and skill in detail. |
| `docs/PRD.md` | Acceptance criteria — the contract. |
