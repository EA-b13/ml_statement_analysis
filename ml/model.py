import os
import pickle
import numpy as np
from sklearn.linear_model import SGDClassifier

# Path where the model will be saved.
MODEL_FILE = 'ml_model.pkl'
# Define the two classes: 0 means “Rejected”, 1 means “Approved”
CLASSES = np.array([0, 1])

def load_model():
    """Load the ML model from disk; if not found, initialize a new one."""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
    else:
        model = SGDClassifier(loss='log_loss', max_iter=1000, tol=1e-3)
        # Initialize the model with a dummy sample so that classes are set.
        model.partial_fit(np.zeros((1, 6)), [0], classes=CLASSES)
        save_model(model)
    return model

def save_model(model):
    """Save the model to disk."""
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)

def extract_features(insights):
    """
    Given the insights dictionary (as produced by our feature_engineering module),
    build a feature vector. For example, we use:
      1. Total deposits (overall)
      2. Total withdrawals (overall)
      3. Net overall (deposits minus withdrawals)
      4. Transaction count
      5. Average deposit
      6. Average withdrawal (absolute value)
    Returns a NumPy array of shape (1,6).
    """
    overall = insights.get('overall_summary', {})
    additional = insights.get('additional_features', {})

    total_deposits = overall.get('total_deposits', 0)
    total_withdrawals = overall.get('total_withdrawals', 0)
    net = overall.get('net', 0)
    txn_count = overall.get('transaction_count', 0)
    avg_deposit = additional.get('avg_deposit', 0)
    avg_withdrawal = abs(additional.get('avg_withdrawal', 0))
    
    features = np.array([total_deposits, total_withdrawals, net, txn_count, avg_deposit, avg_withdrawal])
    return features.reshape(1, -1)

def predict_loan_approval(insights):
    """
    Given the financial insights, extract features and use the model to predict a recommendation.
    Returns a tuple: (recommendation, probability)
    where recommendation is "Approved" or "Rejected" and probability is the model's confidence.
    """
    model = load_model()
    features = extract_features(insights)
    pred = model.predict(features)[0]
    # If available, get the predicted probability.
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0][pred]
        print(proba)
    else:
        proba = None
    recommendation = "Approved" if pred == 1 else "Rejected"
    return recommendation, proba

def update_model(insights, label):
    """
    Update (i.e. train) the model with a new example.
    :param insights: Financial insights (from feature_engineering) for the statement.
    :param label: 1 if human-approved; 0 if rejected.
    """
    model = load_model()
    features = extract_features(insights)
    # Use partial_fit to update the model incrementally.
    model.partial_fit(features, [label])
    save_model(model)