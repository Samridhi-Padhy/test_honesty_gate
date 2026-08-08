function MutantCard({ mutant }) {
  const survived = !mutant.caught;

  return (
    <div className={`mutant-card ${survived ? "survived" : "caught"}`}>
      <h3>{mutant.mutant_id}</h3>

      <p>
        <strong>Operator:</strong> {mutant.operator}
      </p>

      <p>
        <strong>Location:</strong> {mutant.location}
      </p>

      <p className="status">
        Status: <span>{survived ? "Survived" : "Caught"}</span>
      </p>

      <p>
        {mutant.explanation || "Test suite caught this mutant."}
      </p>
    </div>
  );
}

export default MutantCard;