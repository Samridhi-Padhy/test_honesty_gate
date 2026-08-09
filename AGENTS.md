# AGENTS.md — Test Honesty Gate

These are the standing rules every AI agent (Cline, or any other agent used
on this repo) must follow on every task, in every session. Read this file
before starting work. If a request conflicts with this file, follow this
file and flag the conflict to a human.

## 1. What we are building (context for the agent)

An independent, merge-blocking CI gate that mutation-tests AI-generated
code against its own AI-generated tests, and explains any gap in plain
English. Full design: `docs/ARCHITECTURE.md`. Data contract between
services: `docs/CONTRACTS.md`.

## 2. Scope lock — do not expand this without a human saying so

- Exactly **5** hardcoded mutation operators. Do not add a 6th, do not
  generalize into a configurable mutation engine, even if it seems easy.
- One small demo repository under `demo-repo/`. Do not point the engine at
  arbitrary or external repositories.
- The LLM explainer only explains. It must never generate tests, generate
  fixes, or modify source/test files.
- If a task seems to require expanding this scope to be "done properly,"
  stop and ask a human instead of expanding it yourself.

## 3. Human-in-the-loop is mandatory

- Use Plan mode before Act mode for anything that creates or modifies more
  than one file, or touches `backend/gate_service/`, CI config, or the
  contract shape in `docs/CONTRACTS.md`.
- Never auto-approve destructive actions (deleting files, force-pushing,
  rewriting git history, changing branch protection).
- Blind, unreviewed auto-generation scores poorly against this hackathon's
  judging criteria — a human must read and approve non-trivial diffs
  before they're committed.

## 4. Folder ownership — stay inside your lane

| Folder | Owner | Agent may edit freely | Needs sign-off first |
|---|---|---|---|
| `backend/mutation_engine/` | Tanmay | Yes | Changes to mutation operator list |
| `backend/gate_service/` | Tanmay | Yes | Changes to pass/fail logic, CI exit codes |
| `backend/llm_explainer/` | Sikruti | Yes | Changes to fallback behavior |
| `backend/api/` | Sikruti | Yes | Changes to response shape (see `docs/CONTRACTS.md`) |
| `frontend/` | Ashwika | Yes | — |
| `docs/`, repo root, `.github/workflows/` | Samriddhi | No — propose via PR only | Everything |
| `demo-repo/` | Tanmay + Sikruti | Yes | Adding new files unrelated to the 5 mutations |

If a task requires touching a file outside your section's folder, stop and
say so instead of doing it silently.

## 5. The contract is the source of truth

The JSON shape in `docs/CONTRACTS.md` (`pr_id`, `verdict`, `mutants_tested`,
`mutants_caught`, `mutants_survived`, `results[]`, `duration_ms`) must not
be changed by an agent unilaterally. If a task seems to require changing
this shape, stop and flag it — this breaks the other side of the
integration silently.

## 6. Testing requirements

- Every new function gets a unit test in the same PR, in the matching
  `tests/` folder for that component. No exceptions, no "I'll add tests
  later."
- The mutation engine's own correctness must be proven with tests that
  apply and then revert each mutation, checked against a known-good file.
- The LLM explainer must have a test proving its non-LLM fallback path
  works when the LLM call is unavailable or errors.

## 7. Failure-mode rules

- The gate must **fail closed**, not open. If anything in the pipeline
  errors unexpectedly (mutation engine crash, LLM timeout, malformed
  input), the default verdict is `fail`, never a silent `pass`.
- The LLM explainer must never let the gate hang. If the LLM call doesn't
  return within a defined timeout, fall back to a templated message
  immediately.

## 8. Commit hygiene

- Small, frequent, working commits. No end-of-day dumps — a single giant
  commit at the end of the day scores worse than a clean progressive
  history under this hackathon's judging criteria.
- Every commit should leave the repo in a state that builds and runs.
- Write commit messages that describe what changed and why, not just
  "update files."

## 9. Tooling in use on this project

- Primary build agent: **Cline** (VS Code extension), Plan-and-Act flow.
- Models: NVIDIA Build for the heavy implementation loop, Google AI Studio
  (Gemini) for planning and quality-sensitive steps.
- Antigravity was initially used as an independent reviewer, but for round-2 feature work (per-file risk thresholds), we used a Plan-and-Act workflow: Antigravity proposed diffs in Plan mode, and a human explicitly reviewed and approved each diff before it was committed to the codebase.
- Any time Antigravity is used for feature work, log it in `AGENTS_AND_SKILLS.md` with a summary of what was reviewed and approved.

## 10. Style and quality

- Python: follow PEP 8, type-hint function signatures, keep functions
  small and single-purpose (a mutation operator does one mutation).
- No secrets, API keys, or personal data in code, commit messages, or
  prompts sent to any AI tool. Keys live in a local `.env`, never
  committed.
- Prefer explicit, readable code over clever code — a judge and a
  teammate both need to be able to read this fast.

## 11. When in doubt

Ask a human. This file cannot anticipate every situation. If a task is
ambiguous, under-specified, or seems to require breaking one of the rules
above, stop and ask rather than guessing.