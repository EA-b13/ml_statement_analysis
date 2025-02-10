import React from 'react';
import Plot from 'react-plotly.js';

const VisualizationChart = ({ insights }) => {
  // Extract months (sorted) and corresponding values from monthly_summary
  const months = Object.keys(insights.monthly_summary).sort();
  const deposits = months.map(m => insights.monthly_summary[m].total_deposits);
  const withdrawals = months.map(m => insights.monthly_summary[m].total_withdrawals);
  const net = months.map(m => insights.monthly_summary[m].net);

  return (
    <div className="visualization-chart">
      <h3>Monthly Financial Summary</h3>
      <Plot
        data={[
          {
            x: months,
            y: deposits,
            type: 'bar',
            name: 'Deposits',
            marker: { color: 'green' }
          },
          {
            x: months,
            y: withdrawals,
            type: 'bar',
            name: 'Withdrawals',
            marker: { color: 'red' }
          },
          {
            x: months,
            y: net,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Net Balance',
            line: { color: 'blue' }
          }
        ]}
        layout={{
          title: 'Monthly Deposits, Withdrawals, and Net Balance',
          barmode: 'group'
        }}
        style={{ width: '100%', height: '400px' }}
      />
    </div>
  );
};

export default VisualizationChart;