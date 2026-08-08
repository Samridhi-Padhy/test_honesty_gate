# backend

[![CI Status](https://github.com/hoursgotviral-dev/test_honesty_gate/actions/workflows/ci.yml/badge.svg)](https://github.com/hoursgotviral-dev/test_honesty_gate/actions/workflows/ci.yml)

## Running the API

To start the server locally, run the following command from the `backend/` directory:

```bash
cd backend
uvicorn api.app:app --reload --port 8000
```

Alternatively, from the repository root:

```bash
PYTHONPATH=backend uvicorn api.app:app --reload --port 8000
```

To run the existing CLI check:

```bash
./gate check local
```
