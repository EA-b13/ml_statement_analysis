import React from 'react';

const InsightsPanel = ({ insights }) => {
  const overall = insights.overall_summary;
  const additional = insights.additional_features;
  const recurring = insights.recurring_transactions;

  return (
    <div className="insights-panel">
      <h3>Key Financial Insights</h3>
      <div className="overall-summary">
        <p><strong>Total Deposits:</strong> {overall.total_deposits.toFixed(2)}</p>
        <p><strong>Total Withdrawals:</strong> {overall.total_withdrawals.toFixed(2)}</p>
        <p><strong>Net Balance:</strong> {overall.net.toFixed(2)}</p>
        <p><strong>Transaction Count:</strong> {overall.transaction_count}</p>
      </div>
      <div className="financial-ratios">
        <p><strong>Average Deposit:</strong> {additional.avg_deposit ? additional.avg_deposit.toFixed(2) : 'N/A'}</p>
        <p><strong>Average Withdrawal:</strong> {additional.avg_withdrawal ? additional.avg_withdrawal.toFixed(2) : 'N/A'}</p>
        <p>
          <strong>Deposit/Withdrawal Ratio:</strong>{" "}
          {additional.deposit_withdrawal_ratio ? additional.deposit_withdrawal_ratio.toFixed(2) : 'N/A'}
        </p>
      </div>
      <div className="recurring-transactions">
        <h4>Recurring Transactions</h4>
        {Object.keys(recurring).length > 0 ? (
          <ul>
            {Object.keys(recurring).map((desc, index) => (
              <li key={index}>
                {desc}: {recurring[desc].occurrences} occurrences in {recurring[desc].unique_months} months, Avg Amount: {recurring[desc].average_amount.toFixed(2)}
              </li>
            ))}
          </ul>
        ) : (
          <p>No recurring transactions detected.</p>
        )}
      </div>
    </div>
  );
};

export default InsightsPanel;