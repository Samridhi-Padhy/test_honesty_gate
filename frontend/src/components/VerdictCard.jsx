function VerdictCard({ verdict }) {
  return (
    <div className="verdict">
      <h2>Verdict</h2>
      <h1>{verdict.toUpperCase()}</h1>
    </div>
  );
}

export default VerdictCard;