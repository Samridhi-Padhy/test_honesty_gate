function VerdictCard({ verdict, survived, prId }) {
  const blocked = verdict === "fail";

  return (
    <div
      className={blocked ? "verdict verdict-blocked" : "verdict verdict-passed"}
      data-testid="verdict"
      role="status"
    >
      <h2>{blocked ? "Merge blocked" : "Merge allowed"}</h2>

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