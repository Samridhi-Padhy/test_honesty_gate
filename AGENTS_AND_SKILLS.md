# Agents and Skills

This document describes the custom agents and skills implemented for the `test-honesty-gate` project. These tools leverage Cline (VS Code) and the GitHub Spec Kit to automate workflows and assist human reviewers.

## Skills

### `generate_mutation_operator`
**Location:** `.agents/skills/generate_mutation_operator/SKILL.md`

**Purpose:** 
The mutation engine relies on a library of operators (e.g., flipping `==` to `!=`, dropping `is None` guards) to test the robustness of the unit tests. As the codebase evolves, new operators must be added to simulate different classes of bugs. This skill provides the IDE agent with exact instructions and code templates to rapidly scaffold a new mutation operator in `backend/mutation_engine/operators.py`, write its associated unit tests, and verify its compilation. 

**Why it exists:** 
Writing a new mutation operator requires adhering to the project's specific string-based pattern, where each operator matches exact source text at a target line and returns an `AppliedMutation` object that can be reverted cleanly with no leftover diff. This skill abstracts that boilerplate, allowing developers to simply describe a bug (e.g., "remove return statements") and let the agent generate the safe, string-based manipulation code consistently.

## Agents

### `gate_reviewer`
**Location:** `.agents/agents/gate_reviewer/AGENT.md`

**Purpose:** 
This agent acts as a specialized assistant for code review. It runs the full mutation testing pipeline (`python gate check local`) against a branch, analyzes the structured JSON output (including the LLM-generated explanations for surviving mutants), and synthesizes a human-readable markdown report.

**Why it exists:** 
The raw JSON output of the gate check is machine-readable and great for CI tools, but difficult for a human developer to parse quickly during a pull request review. The `gate_reviewer` agent bridges this gap by automatically executing the test suite and translating the results into actionable feedback (e.g., explicitly calling out which tests are missing and where the coverage holes exist). This agent can be invoked manually or wired into automated PR workflows in the future.

## AI Contributions Log

### Antigravity (Per-File Risk Thresholds)
Antigravity was used in a Plan-and-Act workflow to implement the per-file risk threshold feature end-to-end. A human reviewed and approved each step before commit:
1. **Runner Generalization:** Refactored `backend/mutation_engine/runner.py` to resolve target locations relative to the `demo-repo` root.
2. **Second Demo File:** Added `demo-repo/src/notifications.py` and its tests, wiring up new targets (`m6`, `m7`).
3. **Config Loader & Aggregation:** Created `gate.config.json` and `backend/gate_service/thresholds.py`, updated `gate.py` to aggregate stats per-file, and modified the test suite to verify threshold enforcement.
4. **CI & Formatting Updates:** Fixed frontend `StatsCard.jsx` styling and added a Docker build smoke test to CI.
5. **Documentation:** Updated `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/CONTRACTS.md` with the new feature logic.
