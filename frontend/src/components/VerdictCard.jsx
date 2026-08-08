function VerdictCard({ verdict, survived, prId }) {
  const isPass = verdict === "pass";
  const blocked = !isPass;
  const verdictClass = isPass ? "verdict-passed" : "verdict-failed";
  const verdictText = isPass ? "Merge allowed" : "Merge blocked";

  return (
    <div
      className={`verdict ${verdictClass}`}
      data-testid="verdict"
      role="status"
    >
      <h2>{verdictText}</h2>

      <p className="verdict-reason">
        {blocked
          ? `${survived} of the 5 seeded bugs were not caught by this pull request's tests. The tests run green, but they are not verifying behaviour.`
          : "All 5 seeded bugs were caught. These tests are genuinely verifying behaviour, not just executing lines."}
      </p>

      {prId && <p className="verdict-pr">Pull request: {prId}</p>}
    </div>
  );
}

export default VerdictCard;