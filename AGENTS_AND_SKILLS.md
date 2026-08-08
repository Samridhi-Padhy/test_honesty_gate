# Agents and Skills

This document describes the custom agents and skills implemented for the `test-honesty-gate` project. These tools leverage the Antigravity IDE framework to automate workflows and assist human reviewers.

## Skills

### `verify_mutation_targets`
**Location:** `.agents/skills/generate_mutation_operator/SKILL.md`

**Purpose:** 
The mutation engine relies on exactly 5 hardcoded operators (e.g., flipping `==` to `!=`, dropping `is None` guards) that target specific line numbers in `demo-repo/` using plain text spans, as defined in `backend/mutation_engine/operators.py`. This skill provides the IDE agent with exact instructions to verify that the `MUTATION_TARGETS` in `backend/mutation_engine/runner.py` still point to the correct logic in `demo-repo/src/pricing.py` after any edits to that file.

**Why it exists:** 
Because the mutation operators operate on plain text spans rather than an AST, any reflows or edits in `demo-repo/` can shift line numbers and silently break the mutations (causing an `OperatorTargetError`). This skill allows the agent to automatically audit and fix the `MUTATION_TARGETS` line mappings to catch lint-reflow traps safely and consistently.

## Agents

### `gate_reviewer`
**Location:** `.agents/agents/gate_reviewer/AGENT.md`

**Purpose:** 
This agent acts as a specialized assistant for code review. It runs the full mutation testing pipeline (`python gate check local`) against a branch, analyzes the structured JSON output (including the LLM-generated explanations for surviving mutants), and synthesizes a human-readable markdown report.

**Why it exists:** 
The raw JSON output of the gate check is machine-readable and great for CI tools, but difficult for a human developer to parse quickly during a pull request review. The `gate_reviewer` agent bridges this gap by automatically executing the test suite and translating the results into actionable feedback (e.g., explicitly calling out which tests are missing and where the coverage holes exist). This agent can be invoked manually or wired into automated PR workflows in the future.
