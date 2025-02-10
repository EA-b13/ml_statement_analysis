import React from 'react';

const TransactionExplorer = ({ transactions }) => {
  return (
    <div className="transaction-explorer">
      <h3>Transaction Explorer</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, index) => {
            // Convert the amount to a float
            const amount = parseFloat(tx.amount);
            // If parseFloat returns NaN, fallback to displaying tx.amount as is
            const displayAmount = isNaN(amount) ? tx.amount : amount.toFixed(2);
            return (
              <tr key={index}>
                <td>{tx.date}</td>
                <td>{tx.description}</td>
                <td>{displayAmount}</td>
                <td>{tx.type}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default TransactionExplorer;