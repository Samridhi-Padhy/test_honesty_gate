# Test Honesty Gate

[![CI Status](https://github.com/Samridhi-Padhy/test_honesty_gate/actions/workflows/ci.yml/badge.svg)](https://github.com/Samridhi-Padhy/test_honesty_gate/actions/workflows/ci.yml)

A mutation-testing gate that enforces high-quality test suites by injecting deliberate bugs and ensuring tests catch them. It includes a backend Python API, a React frontend, and a CLI.

## Prerequisites
- Python 3.10+
- Node.js 18+

## Setup & Installation

### 1. Environment Variables
Copy the `.env.example` file to create your local `.env`:
```bash
cp .env.example .env
```
Add your `GEMINI_API_KEY` (and `NVIDIA_API_KEY` if using the fallback provider) to the `.env` file to enable the LLM Explainer service.

### 2. Backend Dependencies
Install the required Python packages for the backend and the mutation engine:
```bash
pip install -r backend/requirements.txt
```

### 3. Frontend Dependencies
Install the Node.js packages for the React frontend:
```bash
cd frontend
npm install
cd ..
```

## Running the Project

### Gate CLI
To run the mutation gate manually against the `demo-repo` and output a JSON contract report:
```bash
python gate check local
```

### Backend API
Start the FastAPI server locally on port 8000:
```bash
# From the repository root
PYTHONPATH=backend uvicorn api.app:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### Frontend
Start the Vite development server for the React UI:
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## Running the Demo (Good PR vs Bad PR)
The gate evaluates the test suite located in the `demo-repo/` folder.

- **Good PR Simulation:** By default, the tests in `demo-repo/tests/test_pricing.py` are robust and catch all 5 mutations. Running the gate (via CLI or API) will result in a **Pass** verdict because all bugs injected by the mutation engine are caught by the tests.
- **Bad PR Simulation:** To simulate a weak test suite, open `demo-repo/tests/test_pricing.py` and comment out one of the assertions (e.g., the assertion in `test_none_returns_anonymous`). Running the gate again will result in a **Fail / Blocked** verdict. The surviving mutant will be passed to the LLM explainer, which will generate a specific, actionable explanation of what test assertion is missing.
