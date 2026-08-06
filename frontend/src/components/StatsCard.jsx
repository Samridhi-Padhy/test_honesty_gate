function StatsCard({ tested, caught, survived, duration }) {
  return (
    <div className="stats">
      <p>Mutants Tested: {tested}</p>
      <p>Mutants Caught: {caught}</p>
      <p>Mutants Survived: {survived}</p>
      <p>Duration: {duration} ms</p>
    </div>
  );
}

export default StatsCard;