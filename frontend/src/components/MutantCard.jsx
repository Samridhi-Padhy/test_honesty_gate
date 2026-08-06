function MutantCard({ mutant }) {
  return (
    <div className="mutant-card">
      <h3>{mutant.mutant_id}</h3>

      <p>
        <strong>Operator:</strong> {mutant.operator}
      </p>

      <p>
        <strong>Location:</strong> {mutant.location}
      </p>

      <p>
        <strong>Status:</strong>{" "}
        <span className="status">Survived</span>
      </p>

      <p>{mutant.explanation}</p>
    </div>
  );
}

export default MutantCard;