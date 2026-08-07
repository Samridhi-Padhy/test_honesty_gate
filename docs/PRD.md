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
