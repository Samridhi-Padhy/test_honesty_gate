# Agents and Skills

This document describes the custom agents and skills implemented for the `test-honesty-gate` project. These tools leverage Cline (VS Code) and the GitHub Spec Kit to automate workflows and assist human reviewers.

## Skills

### `generate_mutation_operator`
**Location:** `.agents/skills/generate_mutation_operator/SKILL.md`

**Purpose:** 
The mutation engine relies on a library of operators (e.g., flipping `==` to `!=`, dropping `is None` guards) to test the robustness of the unit tests. As the codebase evolves, new operators must be added to simulate different classes of bugs. This skill provides the IDE agent with exact instructions and code templates to rapidly scaffold a new mutation operator in `backend/mutation_engine/operators.py`, write its associated unit tests, and verify its compilation. 

**Why it exists:** 
Writing a new AST (Abstract Syntax Tree) mutation operator requires deep knowledge of Python's `ast` module and the project's `@register_operator` decorator pattern. This skill abstracts that boilerplate, allowing developers to simply describe a bug (e.g., "remove return statements") and let the agent generate the complex AST manipulation code safely and consistently.

## Agents

### `gate_reviewer`
**Location:** `.agents/agents/gate_reviewer/AGENT.md`

**Purpose:** 
This agent acts as a specialized assistant for code review. It runs the full mutation testing pipeline (`python gate check local`) against a branch, analyzes the structured JSON output (including the LLM-generated explanations for surviving mutants), and synthesizes a human-readable markdown report.

**Why it exists:** 
The raw JSON output of the gate check is machine-readable and great for CI tools, but difficult for a human developer to parse quickly during a pull request review. The `gate_reviewer` agent bridges this gap by automatically executing the test suite and translating the results into actionable feedback (e.g., explicitly calling out which tests are missing and where the coverage holes exist). This agent can be invoked manually or wired into automated PR workflows in the future.
