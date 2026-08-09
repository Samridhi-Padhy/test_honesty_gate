"""Unit tests for the FastAPI layer.

Covers both the permanent mock-mode fallback and the real end-to-end
chain (mutation_engine -> gate_service -> llm_explainer) that now runs by
default. The real-chain tests stub only the LLM call so they are fast and
deterministic; the mutation runner and gate aggregation run for real against
demo-repo.
"""

from api.app import _mock_mode_enabled, app
from fastapi.testclient import TestClient
from llm_explainer import service as llm_service

client = TestClient(app)


class TestMockModeEndpoint:
    def test_mock_mode_returns_valid_contract(self) -> None:
        resp = client.get("/gate", params={"mock": True})
        assert resp.status_code == 200
        contract = resp.json()
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
        assert contract["verdict"] == "fail"
        assert contract["mutants_tested"] == 7
        for record in contract["results"]:
            assert set(record.keys()) == {
                "mutant_id",
                "operator",
                "location",
                "caught",
                "explanation",
            }

    def test_mock_mode_empty_explanations(self) -> None:
        resp = client.get("/gate", params={"mock": True})
        contract = resp.json()
        for record in contract["results"]:
            assert record["explanation"] == ""

    def test_health_endpoint(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestMockModeFlag:
    def test_query_param_overrides_env(self, monkeypatch) -> None:
        monkeypatch.setenv("MOCK_MODE", "false")
        assert _mock_mode_enabled(True) is True
        assert _mock_mode_enabled(False) is False

    def test_env_var_enables_mock(self, monkeypatch) -> None:
        monkeypatch.setenv("MOCK_MODE", "true")
        assert _mock_mode_enabled(None) is True

    def test_default_is_not_mock(self, monkeypatch) -> None:
        monkeypatch.delenv("MOCK_MODE", raising=False)
        assert _mock_mode_enabled(None) is False


class TestRealChainEndpoint:
    """The default (non-mock) path runs the real end-to-end chain.

    Only the LLM call is stubbed (for speed and determinism); the mutation
    runner and gate aggregation run for real against demo-repo.
    """

    def test_real_chain_returns_locked_contract_shape(self, monkeypatch) -> None:
        monkeypatch.setattr(llm_service, "_call_llm", lambda prompt: "LLM explanation")
        resp = client.get("/gate")
        assert resp.status_code == 200
        contract = resp.json()
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
        assert contract["mutants_tested"] == 7
        for record in contract["results"]:
            assert set(record.keys()) == {
                "mutant_id",
                "operator",
                "location",
                "caught",
                "explanation",
            }

    def test_real_chain_fills_explanations_for_survivors(self, monkeypatch) -> None:
        monkeypatch.setattr(llm_service, "_call_llm", lambda prompt: "LLM explanation")
        resp = client.get("/gate")
        contract = resp.json()
        for record in contract["results"]:
            if record["caught"]:
                assert record["explanation"] == ""
            else:
                assert record["explanation"] != ""

    def test_real_chain_all_mutants_caught(self, monkeypatch) -> None:
        """The strengthened test suite means all mutants are caught."""
        monkeypatch.setattr(llm_service, "_call_llm", lambda prompt: "LLM explanation")
        resp = client.get("/gate")
        contract = resp.json()
        survivors = [r["mutant_id"] for r in contract["results"] if not r["caught"]]
        assert survivors == []
        assert contract["verdict"] == "pass"
        assert contract["mutants_survived"] == 0
        assert contract["mutants_caught"] == 7
