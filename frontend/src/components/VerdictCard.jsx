function VerdictCard({ verdict }) {
  const isPass = verdict === "pass";
  const verdictClass = isPass ? "verdict-passed" : "verdict-failed";
  const verdictText = isPass ? "Merge allowed" : "Merge blocked";

  return (
    <div className={`verdict ${verdictClass}`} data-testid="verdict">
      <h2>Verdict</h2>
      <h1>{verdictText}</h1>
    </div>
  );
}

export default VerdictCard;