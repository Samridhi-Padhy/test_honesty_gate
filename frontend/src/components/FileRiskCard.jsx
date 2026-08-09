
import React from "react";

function FileRiskCard({ perFile }) {
  if (!perFile || perFile.length === 0) {
    return null;
  }

  return (
    <div className="file-risks">
      <h2 className="section-heading">Per-file thresholds</h2>
      
      {perFile.map((file) => {
        const ratePct = Math.round(file.kill_rate * 100);
        const threshPct = Math.round(file.threshold * 100);
        const cardClass = file.passed ? "verdict-passed" : "verdict-blocked";
        
        return (
          <div
            key={file.file}
            className={`verdict ${cardClass}`}
            data-testid={`file-risk-${file.file}`}
          >
            <p style={{ margin: "0 0 10px 0", fontWeight: "bold", fontSize: "1.2rem" }}>
              {file.file}
            </p>
            <p className="verdict-reason" style={{ margin: 0 }}>
              Kill rate: {ratePct}% (Threshold: {threshPct}%) -{" "}
              <strong>{file.passed ? "PASS" : "FAIL"}</strong>
            </p>
          </div>
        );
      })}
    </div>
  );
}

export default FileRiskCard;
