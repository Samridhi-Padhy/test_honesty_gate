"""Unit tests for the gate service contract aggregation and CLI."""

import json
import subprocess
import sys
from pathlib import Path

from gate_service.gate import build_contract, gate_check_cli
from mutation_engine.runner import MutantResult, RunSummary

REPO_ROOT = Path(__file__).resolve().parents[2]


def _sample_summary() -> RunSummary:
    return RunSummary(
        results=[
            MutantResult("m1", "equality_flip", "src/pricing.py:28", caught=False),
            MutantResult("m2", "boundary_shift", "src/pricing.py:15", caught=True),
            MutantResult("m3", "off_by_one", "src/pricing.py:37", caught=True),
            MutantResult("m4", "negate_boolean", "src/pricing.py:48", caught=True),
            MutantResult("m5", "drop_null_guard", "src/pricing.py:56", caught=True),
            MutantResult("m6", "negate_boolean", "src/notifications.py:2", caught=True),
            MutantResult(
                "m7", "drop_null_guard", "src/notifications.py:6", caught=True
            ),
        ],
        duration_ms=1830,
    )


class TestBuildContract:
    def test_contract_shape_is_locked(self) -> None:
        contract = build_contract("pr-42", _sample_summary())
        assert set(contract.keys()) == {
            "pr_id",
            "verdict",
            "mutants_tested",
            "mutants_caught",
            "mutants_survived",
            "results",
            "per_file",
            "duration_ms",
        }
        assert contract["pr_id"] == "pr-42"
        assert contract["mutants_tested"] == 7
        assert contract["mutants_caught"] == 6
        assert contract["mutants_survived"] == 1
        assert contract["duration_ms"] == 1830

    def test_verdict_fails_when_mutant_survives(self) -> None:
        contract = build_contract("pr-42", _sample_summary())
        assert contract["verdict"] == "fail"

    def test_verdict_passes_when_all_caught(self) -> None:
        summary = RunSummary(
            results=[MutantResult("m1", "equality_flip", "src/pricing.py:28", True)],
            duration_ms=10,
        )
        contract = build_contract("pr-1", summary)
        assert contract["verdict"] == "pass"

    def test_result_entry_shape(self) -> None:
        contract = build_contract("pr-42", _sample_summary())
        entry = contract["results"][0]
        assert set(entry.keys()) == {
            "mutant_id",
            "operator",
            "location",
            "caught",
            "explanation",
        }
        assert entry["explanation"] == ""
        assert entry["mutant_id"] == "m1"
        assert entry["caught"] is False

    def test_timeout_counts_as_survived_and_fails_closed(self) -> None:
        summary = RunSummary(
            results=[
                MutantResult(
                    "m1",
                    "equality_flip",
                    "src/pricing.py:28",
                    caught=False,
                    timed_out=True,
                    error="pytest timed out",
                )
            ],
            duration_ms=1500,
        )
        contract = build_contract("pr-1", summary)
        assert contract["verdict"] == "fail"
        assert contract["mutants_survived"] == 1


class TestGateCheckCli:
    def test_cli_returns_pass_exit_code_when_gate_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "gate"), "check"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=False,
        )
        assert proc.returncode == 0
        contract = json.loads(proc.stdout)
        assert contract["verdict"] == "pass"
        assert contract["mutants_survived"] == 0

    def test_cli_stdout_is_clean_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "gate"), "check"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=False,
        )
        json.loads(proc.stdout)

    def test_gate_check_cli_function_returns_int(self) -> None:
        assert isinstance(gate_check_cli(["check", "pr-1"]), int)


class TestPerFileThresholds:
    def test_file_at_or_above_threshold_passes(self, monkeypatch) -> None:
        # Mock load_thresholds to require 1.0 (100%) for pricing.py
        monkeypatch.setattr(
            "gate_service.gate.load_thresholds",
            lambda: {
                "default_kill_threshold": 0.75,
                "file_thresholds": {"src/pricing.py": 1.0},
            },
        )

        # summary has 1 mutant in pricing.py, caught=True -> 100% kill rate
        summary = RunSummary(
            results=[MutantResult("m1", "equality_flip", "src/pricing.py:28", True)],
            duration_ms=10,
        )
        contract = build_contract("pr-1", summary)
        assert contract["verdict"] == "pass"
        assert len(contract["per_file"]) == 1
        assert contract["per_file"][0]["file"] == "src/pricing.py"
        assert contract["per_file"][0]["passed"] is True

    def test_file_below_threshold_fails_overall(self, monkeypatch) -> None:
        # Mock load_thresholds to require 1.0 (100%) for pricing.py
        monkeypatch.setattr(
            "gate_service.gate.load_thresholds",
            lambda: {
                "default_kill_threshold": 0.75,
                "file_thresholds": {"src/pricing.py": 1.0},
            },
        )

        # summary has 2 mutants in pricing.py, 1 caught, 1 missed -> 50% kill rate
        summary = RunSummary(
            results=[
                MutantResult("m1", "equality_flip", "src/pricing.py:28", True),
                MutantResult("m2", "boundary_shift", "src/pricing.py:15", False),
            ],
            duration_ms=10,
        )
        contract = build_contract("pr-1", summary)
        assert contract["verdict"] == "fail"
        assert contract["per_file"][0]["passed"] is False

    def test_missing_config_falls_back_to_defaults(self, monkeypatch, tmp_path) -> None:
        from gate_service.thresholds import load_thresholds

        # Force the config file to seem non-existent
        monkeypatch.setattr(
            "gate_service.thresholds.CONFIG_PATH", tmp_path / "does_not_exist.json"
        )

        thresholds = load_thresholds()
        assert thresholds["default_kill_threshold"] == 0.75
        assert thresholds["file_thresholds"] == {}
