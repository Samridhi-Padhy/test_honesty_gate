const mockData = {
  pr_id: "PR-101",
  verdict: "fail",
  mutants_tested: 5,
  mutants_caught: 4,
  mutants_survived: 1,
  results: [
    {
      mutant_id: "m3",
      operator: "boundary_shift",
      location: "src/pricing.py:42",
      caught: false,
      explanation:
        "The AI test suite did not catch this off-by-one error. Add an assertion for the boundary case where x == 0."
    }
  ],
  per_file: [
    {
      file: "src/pricing.py",
      mutants_tested: 5,
      mutants_caught: 4,
      kill_rate: 0.8,
      threshold: 1.0,
      passed: false
    }
  ],
  duration_ms: 1830
};

export default mockData;