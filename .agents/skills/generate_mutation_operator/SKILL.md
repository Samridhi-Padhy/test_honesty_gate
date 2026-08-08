---
name: verify_mutation_targets
description: Verifies that MUTATION_TARGETS in runner.py point to the correct line numbers in demo-repo/src/pricing.py.
---

# verify_mutation_targets

This skill verifies that the hardcoded line numbers in `backend/mutation_engine/runner.py`'s `MUTATION_TARGETS` dict still correctly point to the expected logic in `demo-repo/src/pricing.py`. The mutation engine relies on exact text spans rather than AST parsing, so any reflows or edits in `demo-repo/` can silently break the mutations (causing an `OperatorTargetError` if the expected text is not found on that line).

## Instructions
When invoked to verify mutation targets, follow these steps exactly:

1. **Read `MUTATION_TARGETS`**:
   Parse the `MUTATION_TARGETS` dictionary in `backend/mutation_engine/runner.py` to get the target line numbers for `m1` through `m5`.

2. **Verify Line Contents in `demo-repo/src/pricing.py`**:
   Check the specified lines in `demo-repo/src/pricing.py` for the following expected markers, based on the plain-text operator logic in `backend/mutation_engine/operators.py`:
   - **m1 (equality_flip)**: Target line must contain `==`
   - **m2 (boundary_shift)**: Target line must contain `<`
   - **m3 (off_by_one)**: Target line must contain `range(`
   - **m4 (negate_boolean)**: Target line must contain `return `
   - **m5 (drop_null_guard)**: Target line must contain `is None`

3. **Report and Fix**:
   If any line number does not contain its expected marker, it means `demo-repo/src/pricing.py` was edited or reformatted. You must manually find where that logic moved to in `demo-repo/src/pricing.py` and update the line numbers in `backend/mutation_engine/runner.py` to restore the mutations.
