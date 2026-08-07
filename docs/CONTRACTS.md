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
  "duration_ms": 1234
}
```
