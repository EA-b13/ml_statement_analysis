import React from 'react';

const TransactionTable = ({ insights }) => {
  const transactions = insights.transactions || [];
  
  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Amount</th>
          <th>Type</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        {transactions.map((tx, index) => (
          <tr key={index}>
            <td>{tx.date}</td>
            <td>{tx.amount}</td>
            <td>{tx.type}</td>
            <td>{tx.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TransactionTable;