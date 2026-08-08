function StatsCard({ tested, caught, survived, duration }) {
  return (
    <div className="stats">
      <p>
        <span className="stat-label">Mutants Tested</span>
        <span className="stat-value">{tested}</span>
      </p>
      <p>
        <span className="stat-label">Mutants Caught</span>
        <span className="stat-value">{caught}</span>
      </p>
      <p>
        <span className="stat-label">Mutants Survived</span>
        <span className="stat-value">{survived}</span>
      </p>
      <p>
        <span className="stat-label">Duration</span>
        <span className="stat-value">{duration} ms</span>
      </p>
    </div>
  );
}

export default StatsCard;