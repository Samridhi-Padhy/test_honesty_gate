"""Gate service: aggregate mutation results into the locked contract JSON.

The contract shape is shared across the team and must not change
unilaterally. The verdict is fail-closed: any survived mutant, timeout, or
unexpected error produces a ``fail`` verdict.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from llm_explainer.service import explain_surviving_mutants
from mutation_engine.runner import RunSummary, run_all_mutants

from gate_service.thresholds import load_thresholds


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

    thresholds_config = load_thresholds()
    default_kill = thresholds_config["default_kill_threshold"]
    file_thresholds = thresholds_config["file_thresholds"]

    # Group results by file
    file_stats: dict[str, dict[str, int]] = {}
    for r in summary.results:
        # format is "path:line", split on the last ":"
        file_path = r.location.rsplit(":", 1)[0]
        if file_path not in file_stats:
            file_stats[file_path] = {"tested": 0, "caught": 0}
        file_stats[file_path]["tested"] += 1
        if r.caught:
            file_stats[file_path]["caught"] += 1

    per_file = []
    any_file_failed = False
    for file_path, stats in file_stats.items():
        tested = stats["tested"]
        caught = stats["caught"]
        kill_rate = caught / tested if tested > 0 else 0.0
        threshold = file_thresholds.get(file_path, default_kill)
        passed = kill_rate >= threshold
        if not passed:
            any_file_failed = True

        per_file.append(
            {
                "file": file_path,
                "mutants_tested": tested,
                "mutants_caught": caught,
                "kill_rate": kill_rate,
                "threshold": threshold,
                "passed": passed,
            }
        )

    verdict = "fail" if (summary.mutants_survived > 0 or any_file_failed) else "pass"
    return {
        "pr_id": pr_id,
        "verdict": verdict,
        "mutants_tested": summary.mutants_tested,
        "mutants_caught": summary.mutants_caught,
        "mutants_survived": summary.mutants_survived,
        "results": results,
        "per_file": per_file,
        "duration_ms": summary.duration_ms,
    }


def run_gate(pr_id: str) -> dict[str, Any]:
    """Run all mutants and return the contract JSON."""
    summary = run_all_mutants()
    return build_contract(pr_id, summary)


def render_markdown_summary(contract: dict[str, Any]) -> str:
    """Render the contract as a human-readable markdown report.

    This is the product promise made visible where it matters most: the CI
    check itself shows a plain-English reason, not a raw log dump.
    """
    verdict = contract["verdict"]
    header = (
        "## Test Honesty Gate - PASSED"
        if verdict == "pass"
        else "## Test Honesty Gate - BLOCKED"
    )
    lines = [
        header,
        "",
        f"- Mutants tested: {contract['mutants_tested']}",
        f"- Caught by your tests: {contract['mutants_caught']}",
        f"- Survived (not caught): {contract['mutants_survived']}",
        f"- Duration: {contract['duration_ms']} ms",
        "",
    ]
    survivors = [r for r in contract["results"] if not r["caught"]]
    if not survivors:
        lines.append(
            "Every mutation was caught by the test suite. The tests are "
            "genuinely asserting behaviour, not just executing lines."
        )
    else:
        lines.append("### Merge blocked - these mutations survived your tests")
        lines.append("")
        for record in survivors:
            lines.append(
                f"- **{record['location']}** (`{record['operator']}`): "
                f"{record['explanation']}"
            )

    lines.append("")
    lines.append("### Per-file risk thresholds")
    lines.append("")
    for pf in contract.get("per_file", []):
        status = "PASS" if pf["passed"] else "FAIL"
        rate_pct = int(pf["kill_rate"] * 100)
        thresh_pct = int(pf["threshold"] * 100)
        lines.append(
            f"- **{pf['file']}**: {rate_pct}% kill rate (needs {thresh_pct}%) - **{status}**"
        )

    return "\n".join(lines) + "\n"


def _write_step_summary(markdown: str) -> None:
    """Append the markdown report to the GitHub Actions step summary."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(markdown)
    except OSError:
        # Never let reporting break the gate.
        pass


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
        # Fill in the plain-English reasons before reporting. The explainer
        # is fail-safe: it falls back to templated text and never raises.
        contract = explain_surviving_mutants(contract)
    except Exception as exc:  # noqa: BLE001 - fail closed on any error
        print(f"gate error: {exc!r}", file=sys.stderr)
        return 1

    markdown = render_markdown_summary(contract)
    _write_step_summary(markdown)
    print(markdown, file=sys.stderr)
    print(json.dumps(contract, indent=2))
    return 0 if contract["verdict"] == "pass" else 1
