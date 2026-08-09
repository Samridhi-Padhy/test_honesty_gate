# Data Contracts

The JSON contract defined below represents the exact shape returned by `gate_service` via the API, which the frontend consumes.

**Important:** This shape is strictly locked. Any changes to this schema require cross-team sign-off.

```json
{
  "pr_id": "string",
  "verdict": "pass | fail",
  "mutants_tested": 5,
  "mutants_caught": 4,
  "mutants_survived": 1,
  "results": [
    {
      "mutant_id": "string",
      "operator": "string",
      "location": "string",
      "caught": true,
      "explanation": "string"
    }
  ],
  "per_file": [
    {
      "file": "string",
      "mutants_tested": 2,
      "mutants_caught": 1,
      "kill_rate": 0.5,
      "threshold": 0.75,
      "passed": false
    }
  ],
  "duration_ms": 1234
}
```

*Note: The `per_file` array is an additive v1.1 change. Consumers reading only the original fields are entirely unaffected by this addition.*
