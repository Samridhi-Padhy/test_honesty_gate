# Architecture — Test Honesty Gate

## Table of Contents

1. Overview
2. Architecture Overview
3. System Components
4. Data Contract
5. Technology Stack
6. Design Decisions
7. Failure Handling
8. CI/CD Pipeline

## 1. What This Is
Purpose

Test Honesty Gate is an independent, merge-blocking Continuous Integration (CI) system designed to evaluate the reliability of AI-generated test suites through mutation testing. Instead of generating or modifying code, it audits whether an existing AI-generated test suite is capable of detecting intentionally injected defects.

If one or more injected mutations survive execution without causing the tests to fail, the system concludes that the test suite lacks sufficient coverage. In such cases, the pull request is blocked, and the developer receives a concise, human-readable explanation describing the uncovered weakness.

This approach helps ensure that AI-generated tests validate software behavior rather than merely increasing code coverage.

Objectives

The primary objectives of Test Honesty Gate are to:

Validate the effectiveness of AI-generated test suites.
Prevent weak or incomplete tests from being merged.
Produce clear and actionable explanations for surviving mutations.
Integrate seamlessly into existing GitHub-based CI/CD workflows.
Maintain predictable execution time suitable for continuous integration.
Scope

The system functions solely as an independent auditing layer.

It does not:

Generate application code.
Generate or modify test cases.
Automatically fix defects.
Recommend implementation changes beyond explaining missing test coverage.

Its only responsibility is to verify whether the existing test suite is capable of detecting intentionally introduced faults.

## 2. High-Level Design

```
                        ┌─────────────────────────┐
                        │      Pull Request        │
                        │   (demo-repo/src + tests)│
                        └────────────┬─────────────┘
                                     │ triggers
                                     ▼
                        ┌─────────────────────────┐
                        │   GitHub Actions CI      │
                        │   .github/workflows/ci.yml│
                        └────────────┬─────────────┘
                                     │ runs
                                     ▼
   ┌──────────────────────────────────────────────────────────┐
   │                        backend/                           │
   │                                                            │
   │  ┌────────────────────┐      ┌──────────────────────┐    │
   │  │  mutation_engine/   │      │   gate_service/       │    │
   │  │  - 5 mutation ops   │─────▶│   - aggregates results│    │
   │  │  - apply/revert     │      │   - pass/fail verdict │    │
   │  │  - runs test suite  │      │   - CLI + CI entrypoint│   │
   │  │    per mutant        │      │   - exit code 0 / 1  │    │
   │  └────────────────────┘      └───────────┬───────────┘    │
   │                                            │                │
   │                                            ▼                │
   │                                ┌──────────────────────┐    │
   │                                │  llm_explainer/       │    │
   │                                │  - raw report in       │    │
   │                                │  - 1-2 sentence, per-  │    │
   │                                │    mutant explanation │    │
   │                                │  - templated fallback │    │
   │                                │    if LLM call fails  │    │
   │                                └───────────┬───────────┘    │
   │                                            │                │
   │                                            ▼                │
   │                                ┌──────────────────────┐    │
   │                                │  api/                 │    │
   │                                │  - REST endpoint      │    │
   │                                │  - serves contract     │    │
   │                                │    JSON (Section 4)   │    │
   │                                │  - mock mode flag     │    │
   │                                └───────────┬───────────┘    │
   └────────────────────────────────────────────┼────────────────┘
                                                 │ HTTP / JSON
                                                 ▼
                        ┌──────────────────────────────────┐
                        │            frontend/               │
                        │  - PR result view                  │
                        │  - blocked-merge banner + reason   │
                        │  - built mock-first, wired to real │
                        │    API at the integration checkpoint│
                        └──────────────────────────────────┘
```
System Workflow

The execution flow consists of the following steps:

1.A developer creates or updates a Pull Request.
2.GitHub Actions automatically triggers the CI workflow.
3.The Mutation Engine injects predefined mutations into the target source code.
4.The modified code is executed against the existing test suite.
5.Results from all mutation runs are collected by the Gate Service.
6.Any surviving mutations are forwarded to the LLM Explainer, which generates concise, human-readable feedback.
7.The REST API exposes the final results in a standardized JSON format.
8.The frontend retrieves and displays the verdict, mutation summary, and explanations.
9.If one or more critical mutations survive, the gate returns a failure status, preventing the pull request from being merged.


## 3. System Components

The Test Honesty Gate system is composed of independent, modular components, each responsible for a specific stage of the mutation-testing workflow. This modular architecture improves maintainability, scalability, and ease of testing. 

---

### 3.1 `demo-repo/`

**Purpose**

The `demo-repo` serves as the target codebase used to demonstrate and validate the functionality of the Test Honesty Gate.

**Responsibilities**

* Contains the application source code (`src/`).
* Contains the AI-generated test suite (`tests/`).
* Acts as the input for mutation testing.
* Provides a lightweight environment for fast execution during demonstrations.

**Design Rationale**

The repository is intentionally kept small to ensure that all mutation tests complete within a short and predictable time frame (target: under 10 seconds), making it suitable for Continuous Integration workflows and live demonstrations.

---

### 3.2 `backend/mutation_engine/`

**Purpose**

The Mutation Engine is the core component responsible for evaluating the effectiveness of the test suite by introducing predefined mutations into the source code.

**Responsibilities**

* Applies five predefined mutation operators.
* Executes the test suite after each mutation.
* Determines whether each mutation is **caught** or **survives**.
* Restores the original source code before processing the next mutation.

**Mutation Operators**

1. Equality Operator (`==` → `!=`)
2. Boundary Shift (`<` → `<=`)
3. Off-by-One Error
4. Boolean Negation
5. Removal of `null`/`None` Guard

**Design Rationale**

A fixed set of mutation operators provides predictable execution time while covering common programming mistakes frequently encountered in real-world software development.

---

### 3.3 `backend/gate_service/`

**Purpose**

The Gate Service acts as the orchestration layer of the system, coordinating mutation testing and generating the final merge decision.

**Responsibilities**

* Collects mutation results.
* Calculates overall statistics.
* Determines the final **Pass** or **Fail** verdict.
* Formats the response according to the system's data contract.
* Provides both CLI and CI entry points.

**Output**

* Pass/Fail verdict
* Mutation statistics
* Structured JSON response
* Appropriate process exit code (`0` for success, `1` for failure)

---

### 3.4 `backend/llm_explainer/`

**Purpose**

The LLM Explainer converts raw mutation results into concise, developer-friendly explanations.

**Responsibilities**

* Identifies surviving mutations.
* Generates actionable explanations for each surviving mutation.
* Suggests which test scenarios are missing.
* Falls back to predefined templates if the LLM service is unavailable.

**Design Rationale**

The LLM is used exclusively for explanation generation. It never writes code, modifies tests, or influences the gate's verdict, preserving the integrity of the auditing process.

---

### 3.5 `backend/api/`

**Purpose**

The API layer exposes the Gate Service results to the frontend through REST endpoints.

**Responsibilities**

* Accepts requests from the frontend.
* Returns standardized JSON responses.
* Supports mock mode for frontend development.
* Provides a clean interface between backend services and the user interface.

---

### 3.6 `frontend/`

**Purpose**

The frontend presents mutation testing results in a clear and user-friendly interface.

**Responsibilities**

* Displays the overall verdict.
* Lists all tested mutations.
* Highlights surviving mutations.
* Shows human-readable explanations generated by the LLM.
* Displays affected files and line numbers.
* Retrieves data from the backend API.

---

### 3.7 Custom Agent and Custom Skill

**Purpose**

The custom agent and associated skill provide specialized functionality that extends the core mutation-testing workflow.

**Responsibilities**

* Execute project-specific automation tasks.
* Integrate with the overall gate workflow.
* Support additional capabilities documented separately.

## 4. Data Model — The Contract

This is the single source of truth for what `gate_service`/`api` returns
and what `frontend` consumes. Backend and frontend are built against this
shape independently.

Please see [docs/CONTRACTS.md](./CONTRACTS.md) for the exact locked JSON schema.

## 5. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Mutation engine / gate service | Python | Fast to write string-level source mutations; simple subprocess control over test runs |
| Demo repo under test | Python + `pytest` | Matches mutation engine language; simplest possible mutation-and-rerun loop |
| LLM explainer | NVIDIA Build / Google AI Studio (Gemini) API | Free tiers, no card required, per the hackathon-provided stack; templated fallback removes hard dependency |
| API layer | FastAPI | Minimal REST surface, easy to mock, easy to wire into CI as a script |
| Frontend | React | Fast to build a single result view; mock-first development against static JSON |
| CI/CD | GitHub Actions | Required by the hackathon; gate runs as a required, merge-blocking check |
| Agent/spec tooling | Cline (VS Code) + GitHub Spec Kit | Human-in-the-loop approval flow; matches recommended hackathon workflow |

## 6. Key Design Decisions & Rationale

- **String-matching mutations instead of AST parsing.** AST parsing often destroys original formatting, comments, and spacing when unparsed back to source code, creating messy diffs. By using exact string-matching and tracking the precise character span, we can apply mutations and then cleanly revert them with a perfect symmetric text replacement, leaving no leftover diffs.
- **Exactly 5 hardcoded mutations, not a general mutation engine.** Traditional mutation testing dynamically discovers targets, which requires re-running the full test suite hundreds of times per run. This is unacceptably slow for real codebases. By strictly scope-locking to 5 hardcoded operators, we keep the total gate runtime predictable (under 10 seconds), ensuring it remains a fast, blocking check in CI without live-stalling the pull request.
- **One small demo repo, not arbitrary repos.** Keeps runtime bounded and
  the demo legible to judges in seconds.
- **LLM does explanation only (never generates code or tests).** The purpose of the gate is to audit the test suite. If the LLM generates or fixes the tests, it would be "grading its own homework," undermining the integrity of the audit. Furthermore, this fail-closed approach keeps the LLM's blast radius small: if the LLM hallucinates or fails, the gate still correctly blocks the PR and falls back to templated text, rather than breaking the source code.
- **Explainer has a non-LLM fallback.** The merge gate must never hang or
  silently pass because a third-party LLM API is down or rate-limited.
- **Mock-mode API.** Lets frontend be developed and debugged in isolation
  before and after integration, not just before it.
- **Per-file risk thresholds.** Instead of a single global kill rate, thresholds can be configured per-file. This is because money-critical logic carries significantly more risk than cosmetic or structural code, and a weak test on financial logic should not be able to hide behind a passing repository average.
- **Additive schema changes.** The `per_file` thresholds were added as new fields on the existing data contract rather than modifying the core `results` schema. This avoids a breaking schema change, allowing consumers reading only the original v1.0 fields to remain entirely unaffected by the v1.1 updates.

## 7. Failure Modes and Handling

| Failure | Handling |
|---|---|
| LLM API times out / errors | `llm_explainer` falls back to a templated message; verdict still returns correctly |
| Mutation run exceeds time budget | Gate treats it as a hard failure (fail-closed, not fail-open) rather than hanging CI |
| API unreachable from frontend | Frontend shows a retry state, not a blank screen |
| Contract JSON shape changes | Treated as a breaking change requiring team sign-off before merge (see `docs/CONTRACTS.md`) |

## 8. CI/CD Flow

1. PR opened/updated against `demo-repo/` (or backend/frontend code).
2. GitHub Actions runs `gate_service`'s CLI as a required check.
3. Gate applies the 5 mutants, aggregates results, calls the explainer,
   returns exit code 0/1.
4. Playwright e2e tests run against the frontend in the same workflow.
5. Branch protection requires both checks green plus one review before
   merge to `main`.
