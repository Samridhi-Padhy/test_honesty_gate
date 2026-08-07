---
name: generate_mutation_operator
description: Generates a new mutation operator for the Test-Honesty Gate mutation engine.
---

# generate_mutation_operator

This skill helps scaffold a new mutation operator for the `test-honesty-gate` project. The mutation engine works by parsing Python ASTs (Abstract Syntax Trees) and injecting subtle bugs to test the robustness of our unit tests.

## Instructions
When invoked to generate a new mutation operator, follow these steps exactly:

1. **Ask for Operator Details**: 
   If not already provided, ask the user for the name of the new operator and a brief description of what it mutates (e.g., "change + to -", "remove return statements").
2. **Implement in `operators.py`**:
   - Open `backend/mutation_engine/operators.py`.
   - Create a new function annotated with `@register_operator("your_operator_name")`.
   - The function must take a single `ast.AST` node and return the mutated node, or return `None` if the node doesn't match the criteria for this mutation.
   - Example template:
     ```python
     @register_operator("your_operator_name")
     def your_operator_name(node: ast.AST) -> ast.AST | None:
         # Match condition
         if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
             # Mutate logic
             new_node = copy.deepcopy(node)
             new_node.op = ast.Sub()
             return new_node
         return None
     ```
3. **Write Unit Tests**:
   - Open `backend/tests/test_operators.py`.
   - Add a new test method testing your operator against valid and invalid AST nodes.
   - Ensure the test asserts that the AST node was mutated correctly.

4. **Verify**:
   - Run `pytest backend/tests/test_operators.py` to ensure the new operator compiles and passes its tests.
