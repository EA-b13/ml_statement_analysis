# Bank Statement Analysis & Loan Decision System

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Business Logic & Use Cases](#business-logic--use-cases)
- [Architecture & Technical Stack](#architecture--technical-stack)
- [Directory Structure](#directory-structure)
- [Data Ingestion, Processing, and Feature Engineering](#data-ingestion-processing-and-feature-engineering)
- [Frontend Dashboard](#frontend-dashboard)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)

## Project Overview

The **Bank Statement Analysis & Loan Decision System** is an MVP designed to automate the review of bank statements for business loan applications. The system:
- Extracts and preprocesses data from bank statements in various formats (PDF, CSV, Excel).
- Computes financial insights such as monthly summaries, recurring transactions, and net cash flow.
- Uses a machine learning (ML) module to generate a loan decision recommendation (Approved/Rejected) along with a confidence score.
- Provides an interactive dashboard for business users to review visualizations, analyze transactions, and, if needed, override the ML recommendation with their final decision and remarks.

## Features

### Multi-format Data Ingestion:
- Supports PDF (using Camelot with a Tesseract OCR fallback), CSV, and Excel bank statements.

### Advanced Data Preprocessing:
- Standardizes date formats.
- Detects and splits combined columns (e.g. a "Date Transaction" column into separate date and description fields).
- Merges rows when a transaction description spans multiple lines.

### Feature Engineering:
- Computes monthly summaries (total deposits, withdrawals, net balance, and transaction count).
- Extracts statement-level values (Opening/Closing Balances, Total Debits/Credits) when available.
- Identifies recurring transactions based on identical descriptions across multiple months.

### Machine Learning Decision Support:
- Uses an ML model (implemented with scikit-learn’s SGDClassifier) that is persisted via pickle.
- The model extracts a 6-feature vector from the financial insights, consisting of:
  1. Total deposits (overall)
  2. Total withdrawals (overall)
  3. Net overall (deposits minus withdrawals)
  4. Transaction count
  5. Average deposit
  6. Average withdrawal (absolute value)
- The ML function `predict_loan_approval()` returns a loan decision recommendation (“Approved” or “Rejected”) and a confidence score (probability).
- There is also an `update_model()` function that incrementally retrains the model using new examples via `partial_fit()`.

### Interactive Frontend Dashboard:
- **File Upload Interface:** Users can upload bank statements in supported formats.
- **Data Visualization:** Interactive charts (via Plotly) display monthly financial summaries, including net balance values drawn from statement-level balances (if available).
- **Insights Panel:** Highlights key metrics and recurring transactions.
- **Loan Decision Indicator:** Dynamically displays the ML-generated loan recommendation with its confidence score, plus an option for human override.
- **Transaction Explorer:** Provides a detailed table of individual transactions.

## Business Logic & Use Cases

### Business Logic:
- **Automated Data Extraction & Processing:**
  - The system extracts transaction details from various bank statement formats and cleans the data. It handles common formatting challenges—such as combined columns or multi-row descriptions—ensuring accurate financial data extraction.
- **Financial Analysis:**
  - Using the extracted data, the system computes financial insights. When available, it uses statement-level data (like opening/closing balances and total debits/credits) for more accurate analysis. Otherwise, it falls back on aggregating transaction data.
- **Loan Decision via ML:**
  - A machine learning model processes the financial insights to generate a loan decision recommendation. The model extracts a feature vector (6 key financial metrics) and returns:
    - A recommendation (“Approved” or “Rejected”)
    - A confidence score (e.g., 85%)
    - (Optionally) An explanation of the decision.
  - The model is incrementally updatable with new labeled examples.
- **User Override:**
  - The dashboard enables a human reviewer to override the ML recommendation with their own final decision and remarks.

### Use Cases:
- **Loan Application Review:**
  - A loan officer uploads a bank statement, and the system automatically processes it, generates insights, and provides a loan recommendation. The officer can review visualizations, inspect detailed transactions, and record a final decision.
- **Operational Efficiency:**
  - By automating manual bank statement reviews, the system reduces time, ensures consistency, and enhances decision accuracy.

## Architecture & Technical Stack

### Backend:
- **Django Framework:** Uses Django REST Framework (DRF) for API endpoints.
- **ML & Data Processing Modules (Python):**
  - `ml/data_processing.py`: Extracts and cleans data from bank statements.
  - `ml/feature_engineering.py`: Computes financial insights.
  - `ml/model.py`: Implements the ML model using scikit-learn’s SGDClassifier and persists it using pickle.
  - **Key functions:**
    - `load_model()`: Loads or initializes the model.
    - `save_model()`: Persists the model to disk.
    - `extract_features(insights)`: Constructs a 6-feature vector from insights.
    - `predict_loan_approval(insights)`: Returns a tuple with the recommendation and confidence score.
    - `update_model(insights, label)`: Incrementally retrains the model with new examples.

### Frontend:
- **React.js:** Provides a responsive single-page application.
- **Visualization:** Uses Plotly for interactive charts.
- **Communication:** Uses Axios for API calls to the Django backend.

## Directory Structure
```
ml_statement_analysis_mvp/
├── backend/
│   ├── bank_analysis/
│   ├── bank_app/
│   ├── manage.py
│   ├── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
└── ml/
    ├── data_processing.py
    ├── feature_engineering.py
    ├── model.py
    ├── utils.py
```

## Data Ingestion, Processing, and Feature Engineering

1. **Data Ingestion:**
   - Supports PDF (Camelot with Tesseract OCR fallback), CSV, and Excel.
2. **Data Cleaning & Preprocessing:**
   - Standardizes date formats.
   - Identifies and splits combined columns.
   - Merges split rows.
3. **Feature Engineering:**
   - Computes monthly summaries.
   - Detects statement-level values.
   - Identifies recurring transactions.
  
## Frontend Dashboard

Provides:
- **File Upload Interface**
- **Visualization** with Plotly
- **Insights Panel**
- **Loan Decision Indicator**
- **Transaction Explorer**

## API Endpoints

- **`POST /api/upload/`**: Uploads and processes a bank statement.
- **`GET /api/analysis/<statement_id>/`**: Retrieves insights and ML decisions.
- **`POST /api/feedback/`**: Allows users to submit final decision feedback.

## Installation & Setup

### Prerequisites:
- Python 3.7+, Node.js, Tesseract OCR, Poppler.

### Backend Setup:
```sh
cd ml_statement_analysis_mvp/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup:
```sh
cd ../frontend
npm install
npm start
```

## Running the Application

1. Upload a bank statement in the React app.
2. View the dashboard at `/dashboard/<statement_id>`.
3. Submit final decision feedback.

