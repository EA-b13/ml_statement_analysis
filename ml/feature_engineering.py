import pandas as pd
import numpy as np
import math

def sanitize_data(data):
    """
    Recursively traverse the data structure and replace any float NaN with None.
    """
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, float):
        if math.isnan(data):
            return None
        return data
    else:
        return data

def generate_insights(transactions):
    """
    Generate insights from the list of transaction dictionaries.
    Computes:
      - Monthly summary: total deposits, total withdrawals, net balance, transaction count per month.
      - Overall summary.
      - Additional features: average, median, maximum deposit/withdrawal, deposit-to-withdrawal ratio, and standard deviations.
      - Recurring transactions (appear in at least 3 distinct months).
    Returns a sanitized dictionary of insights.
    """
    if not transactions:
        return {}

    # Create DataFrame from transactions
    df = pd.DataFrame(transactions)
    
    # Convert the 'date' column to datetime (drop rows that fail)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Extract month in "YYYY-MM" format
    df['month'] = df['date'].dt.to_period('M').astype(str)

    df['amount'] = pd.to_numeric(df['amount'])
    
    # Compute deposits and withdrawals
    df['deposit'] = df['amount'].apply(lambda x: x if x > 0 else 0)
    df['withdrawal'] = df['amount'].apply(lambda x: -x if x < 0 else 0)
    
    # Compute monthly summary
    monthly_summary = {}
    for month, group in df.groupby('month'):
        total_deposits = group['deposit'].sum()
        total_withdrawals = group['withdrawal'].sum()
        net = total_deposits - total_withdrawals
        count = group.shape[0]
        monthly_summary[month] = {
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'net': net,
            'transaction_count': count
        }
    
    # Compute overall summary
    overall_deposits = df['deposit'].sum()
    overall_withdrawals = df['withdrawal'].sum()
    overall_net = overall_deposits - overall_withdrawals
    overall_count = df.shape[0]
    overall_summary = {
        'total_deposits': overall_deposits,
        'total_withdrawals': overall_withdrawals,
        'net': overall_net,
        'transaction_count': overall_count,
        'max_deposit': df['deposit'].max(),
        'max_withdrawal': df['withdrawal'].max(),
        'median_transaction': df['amount'].median()
    }
    
    # Additional features
    avg_deposit = df[df['deposit'] > 0]['deposit'].mean() if not df[df['deposit'] > 0].empty else 0
    avg_withdrawal = df[df['withdrawal'] > 0]['withdrawal'].mean() if not df[df['withdrawal'] > 0].empty else 0
    deposit_withdrawal_ratio = overall_deposits / overall_withdrawals if overall_withdrawals != 0 else None
    std_deposit = df[df['deposit'] > 0]['deposit'].std()
    std_withdrawal = df[df['withdrawal'] > 0]['withdrawal'].std()
    
    additional_features = {
        'avg_deposit': avg_deposit,
        'avg_withdrawal': avg_withdrawal,
        'deposit_withdrawal_ratio': deposit_withdrawal_ratio,
        'std_deposit': std_deposit,
        'std_withdrawal': std_withdrawal
    }
    
    # Identify recurring transactions: transactions with the same description appearing in >= 3 distinct months
    recurring = {}
    for desc, group in df.groupby('description'):
        if desc and group['month'].nunique() >= 3:
            recurring[desc] = {
                'occurrences': group.shape[0],
                'unique_months': group['month'].nunique(),
                'average_amount': group['amount'].mean()
            }
    
    insights = {
        'monthly_summary': monthly_summary,
        'overall_summary': overall_summary,
        'additional_features': additional_features,
        'recurring_transactions': recurring,
        'raw_transactions': transactions  # For reference
    }
    
    # Sanitize the insights to replace any NaN with None
    return sanitize_data(insights)