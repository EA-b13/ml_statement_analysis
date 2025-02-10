import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import VisualizationChart from './VisualizationChart';
import InsightsPanel from './InsightsPanel';
import LoanDecision from './LoanDecision';
import TransactionExplorer from './TransactionExplorer';

const Dashboard = () => {
  const { statementId } = useParams();
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await axios.get(`/api/analysis/${statementId}/`);
        setAnalysis(response.data);
      } catch (error) {
        console.error("Error fetching analysis:", error);
      }
    };

    if (statementId) {
      fetchAnalysis();
    }
  }, [statementId]);

  if (!analysis || !analysis.insights) {
    return <p>Loading analysis...</p>;
  }

  // Use the ML values from the response or fallback if not provided.
  const recommendation = analysis.ml_recommendation 
    ? analysis.ml_recommendation 
    : (analysis.insights.overall_summary && analysis.insights.overall_summary.net >= 0 ? "Approve" : "Reject");

  const confidenceScore = analysis.ml_probability ? analysis.ml_probability : 0.85;
  
  const explanation = analysis.ml_explanation 
    ? analysis.ml_explanation 
    : "Based on overall cash flow and computed financial metrics.";

  const handleFinalDecision = (decision, remarks) => {
    console.log("Final decision submitted:", { decision, remarks });
    // Optionally post this feedback to your backend.
  };

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="charts-section">
        <VisualizationChart insights={analysis.insights} />
      </div>
      <div className="insights-panel-section">
        <InsightsPanel insights={analysis.insights} />
      </div>
      <div className="loan-decision-section">
        <LoanDecision 
          recommendation={recommendation}
          confidenceScore={confidenceScore*100}
          // explanation={explanation}
          onFinalDecision={handleFinalDecision}
        />
      </div>
      <div className="transaction-explorer-section">
        <TransactionExplorer transactions={analysis.insights.raw_transactions} />
      </div>
    </div>
  );
};

export default Dashboard;