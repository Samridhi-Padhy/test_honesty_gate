"""Gate service: aggregate mutation results into the locked contract JSON.

The contract shape is shared with Sikruti and Ashwika and must not change
unilaterally. The verdict is fail-closed: any survived mutant, timeout, or
unexpected error produces a ``fail`` verdict.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from mutation_engine.runner import RunSummary, run_all_mutants


def build_contract(pr_id: str, summary: RunSummary) -> dict[str, Any]:
    """Build the locked contract JSON from a run summary.

    The verdict is ``fail`` if any mutant survived (including timeouts and
    errors, which are recorded as not caught). Otherwise it is ``pass``.
    """
    results = [
        {
            "mutant_id": r.mutant_id,
            "operator": r.operator,
            "location": r.location,
            "caught": r.caught,
            "explanation": "",  # llm_explainer fills this in later
        }
        for r in summary.results
    ]
    verdict = "fail" if summary.mutants_survived > 0 else "pass"
    return {
        "pr_id": pr_id,
        "verdict": verdict,
        "mutants_tested": summary.mutants_tested,
        "mutants_caught": summary.mutants_caught,
        "mutants_survived": summary.mutants_survived,
        "results": results,
        "duration_ms": summary.duration_ms,
    }


def run_gate(pr_id: str) -> dict[str, Any]:
    """Run all mutants and return the contract JSON."""
    summary = run_all_mutants()
    return build_contract(pr_id, summary)


def gate_check_cli(argv: list[str] | None = None) -> int:
    """Entry point for ``./gate check``.

    Prints the contract JSON to stdout and returns exit code 0 (pass) or
    1 (fail). All diagnostics go to stderr so stdout stays clean JSON for
    CI consumption.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    pr_id = "local"
    if argv and argv[0] == "check":
        argv = argv[1:]
    if argv:
        pr_id = argv[0]

    try:
        contract = run_gate(pr_id)
        from llm_explainer.service import explain_surviving_mutants
        contract = explain_surviving_mutants(contract)
    except Exception as exc:  # noqa: BLE001 - fail closed on any error
        print(f"gate error: {exc!r}", file=sys.stderr)
        return 1

    print(json.dumps(contract, indent=2))

    if contract["verdict"] == "fail":
        step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if step_summary:
            with open(step_summary, "a") as f:
                f.write(f"## Gate Check Failed\n\n")
                f.write(f"- **Mutants Tested:** {contract['mutants_tested']}\n")
                f.write(f"- **Mutants Caught:** {contract['mutants_caught']}\n")
                f.write(f"- **Mutants Survived:** {contract['mutants_survived']}\n\n")
                f.write("### Surviving Mutants\n\n")
                for r in contract["results"]:
                    if not r["caught"]:
                        f.write(f"**Operator:** `{r['operator']}`\n")
                        f.write(f"**Location:** `{r['location']}`\n")
                        f.write(f"**Explanation:** {r['explanation']}\n\n")

    return 0 if contract["verdict"] == "pass" else 1
