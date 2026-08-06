import "./App.css";

import Header from "./components/Header";
import VerdictCard from "./components/VerdictCard";
import StatsCard from "./components/StatsCard";
import MutantCard from "./components/MutantCard";

import mockData from "./data/mockData";

function App() {
  return (
    <div className="app">
      <Header />

      <VerdictCard verdict={mockData.verdict} />

      <StatsCard
        tested={mockData.mutants_tested}
        caught={mockData.mutants_caught}
        survived={mockData.mutants_survived}
        duration={mockData.duration_ms}
      />

      <h2>Mutation Results</h2>

      {mockData.results.map((mutant) => (
        <MutantCard
          key={mutant.mutant_id}
          mutant={mutant}
        />
      ))}
    </div>
  );
}

export default App;