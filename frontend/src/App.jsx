import { useCallback, useEffect, useState } from "react";

import "./App.css";

import Header from "./components/Header";
import VerdictCard from "./components/VerdictCard";
import StatsCard from "./components/StatsCard";
import FileRiskCard from "./components/FileRiskCard";
import MutantCard from "./components/MutantCard";

import { fetchGateResult } from "./api/client";

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchGateResult());
    } catch (err) {
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="app">
        <Header />
        <p data-testid="loading" className="loading">
          Running the gate against this pull request. This takes a few seconds.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <Header />
        <div data-testid="error" className="error-panel">
          <h2>Could not reach the gate</h2>
          <p>{error}</p>
          <button type="button" onClick={load} data-testid="retry">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Header />

      <VerdictCard
        verdict={data.verdict}
        survived={data.mutants_survived}
        prId={data.pr_id}
      />

      <StatsCard
        tested={data.mutants_tested}
        caught={data.mutants_caught}
        survived={data.mutants_survived}
        duration={data.duration_ms}
      />

      <FileRiskCard perFile={data.per_file} />

      <h2>Mutation results</h2>

      {data.results.map((mutant) => (
        <MutantCard key={mutant.mutant_id} mutant={mutant} />
      ))}
    </div>
  );
}

export default App;