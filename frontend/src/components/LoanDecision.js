import React, { useState } from 'react';

const LoanDecision = ({ 
  recommendation, 
  confidenceScore, 
  // explanation, 
  onFinalDecision 
}) => {
  const [finalDecision, setFinalDecision] = useState(recommendation);
  const [remarks, setRemarks] = useState('');

  const handleDecisionChange = (e) => {
    setFinalDecision(e.target.value);
  };

  const handleRemarksChange = (e) => {
    setRemarks(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onFinalDecision(finalDecision, remarks);
    alert("Final decision saved!");
  };

  return (
    <div className="loan-decision">
      <h3>Loan Decision Recommendation</h3>
      <p>
        <strong>System Recommendation:</strong> {recommendation}
      </p>
      <p>
        <strong>Confidence Score:</strong> {(confidenceScore).toFixed(1)}%
      </p>
      {/* <p>
        <strong>Explanation:</strong> {explanation}
      </p> */}
      <form onSubmit={handleSubmit}>
        <h4>Finalize Decision</h4>
        <label>
          Decision:
          <select value={finalDecision} onChange={handleDecisionChange}>
            <option value="Approve">Approve</option>
            <option value="Reject">Reject</option>
          </select>
        </label>
        <br />
        <label>
          Remarks (optional):
          <textarea
            value={remarks}
            onChange={handleRemarksChange}
            placeholder="Enter remarks if different from recommendation"
          />
        </label>
        <br />
        <button type="submit">Save Final Decision</button>
      </form>
    </div>
  );
};

export default LoanDecision;