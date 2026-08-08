function MutantCard({ mutant }) {
  const survived = !mutant.caught;

  return (
    <div
      className={survived ? "mutant-card survived" : "mutant-card caught"}
      data-testid={`mutant-${mutant.mutant_id}`}
    >
      <h3>{mutant.mutant_id}</h3>

      <p>
        <strong>Operator:</strong> {mutant.operator}
      </p>

      <p>
        <strong>Location:</strong> {mutant.location}
      </p>

      <p className="status">
        <strong>Status:</strong>{" "}
        <span className={survived ? "status-survived" : "status-caught"}>
          {survived ? "Survived" : "Caught"}
        </span>
      </p>

      {survived && mutant.explanation && (
        <p className="explanation">{mutant.explanation}</p>
      )}

      {!survived && (
        <p className="explanation muted">
          Your tests detected this change. No action needed.
        </p>
      )}
    </div>
  );
}

export default MutantCard;