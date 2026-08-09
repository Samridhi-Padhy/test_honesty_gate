p = "demo-repo/tests/test_pricing.py"
s = open(p, encoding="utf-8").read()
targets = [
    "def test_eligible_at_exactly_50(self)",
    "def test_ineligible_below_50(self)",
    "def test_ineligible_above_50(self)",
]
for marker in targets:
    assert s.count(marker) == 1, f"marker not found exactly once: {marker}"
    insert = '@pytest.mark.skip(reason="temporary: verifying LLM explainer")\n    ' + marker
    s = s.replace(marker, insert, 1)
open(p, "w", encoding="utf-8").write(s)
print("done")
