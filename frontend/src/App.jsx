import { useState, useEffect } from "react";
import "./App.css";

import Header from "./components/Header";
import VerdictCard from "./components/VerdictCard";
import StatsCard from "./components/StatsCard";
import MutantCard from "./components/MutantCard";

import { fetchGateResult } from "./api/client";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchGateResult();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="app">
        <Header />
        <div>Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <Header />
        <div data-testid="error">Error: {error}</div>
        <button data-testid="retry" onClick={loadData}>
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="app">
      <Header />

      <VerdictCard verdict={data.verdict} />

      <StatsCard
        tested={data.mutants_tested}
        caught={data.mutants_caught}
        survived={data.mutants_survived}
        duration={data.duration_ms}
      />

      <h2>Mutation Results</h2>

      {data.results.map((mutant) => (
        <MutantCard
          key={mutant.mutant_id}
          mutant={mutant}
        />
      ))}
    </div>
  );
}

export default App;