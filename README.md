# Bank Statement Analysis & Loan Decision System

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Business Logic & Use Cases](#business-logic--use-cases)
- [Architecture & Technical Stack](#architecture--technical-stack)
- [Directory Structure](#directory-structure)
- [Data Ingestion, Processing, and Feature Engineering](#data-ingestion-processing-and-feature-engineering)
- [Machine Learning Model](#machine-learning-model)
- [Frontend Dashboard](#frontend-dashboard)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)

## Project Overview

The **Bank Statement Analysis & Loan Decision System** is an MVP designed to automate the review of bank statements for business loan applications. The system:
- Extracts and preprocesses data from various bank statement formats (PDF, CSV, Excel).
- Computes financial insights such as monthly summaries, recurring transactions, and net cash flow.
- Uses a machine-learning module to generate a loan decision recommendation with a confidence score and explanation.
- Provides an interactive dashboard for business users to review insights, view visualizations, explore transaction details, and override the ML recommendation with feedback.

This project automates a previously manual process, saving time, reducing human error, and ensuring data-backed decision-making.

## Features

### Multi-format Data Ingestion:
- Supports PDF (using Camelot with Tesseract OCR fallback), CSV, and Excel bank statements.

### Advanced Data Preprocessing:
- Standardizes date formats.
- Detects and splits combined columns (e.g., "Date Transaction").
- Merges rows when transaction details span multiple lines.

### Feature Engineering:
- Computes monthly summaries (total deposits, total withdrawals, net balance, transaction count).
- Identifies recurring transactions.
- Extracts statement-level data (Opening/Closing Balances, Total Debit/Credit) when available.

### Machine Learning Decision Support:
- Uses a stub ML model (e.g., based on net cash flow) to provide a loan decision recommendation.
- Returns a confidence score and explanation along with the recommendation.
- Designed to be extended with a trained model in the future.

### Interactive Frontend Dashboard:
- **File Upload Interface:** Users can upload bank statements.
- **Data Visualization:** Interactive charts (using Plotly) display financial summaries and net balances.
- **Insights Panel:** Highlights key metrics and recurring transactions.
- **Loan Decision Indicator:** Displays the ML-generated recommendation, confidence score, and explanation.
- **Transaction Explorer:** Provides a drill-down table of individual transactions.
- **Final Decision Override:** Allows users to submit a final decision and remarks.

## Business Logic & Use Cases

### Business Logic:
- **Automated Data Extraction:** Extracts transaction details from bank statements regardless of format.
- **Financial Analysis:** Computes financial metrics such as monthly deposits, withdrawals, and net balances.
- **Loan Decision:** Evaluates financial insights and provides a recommendation, confidence score, and explanation.
- **User Override:** Allows human reviewers to submit a final decision.

### Use Cases:
- **Business Loan Assessment:** Automates the review of bank statements for loan applications.
- **Operational Efficiency:** Reduces manual effort and speeds up decision-making.

## Architecture & Technical Stack

### Backend:
- **Django Framework:** Uses Django REST Framework (DRF) for API endpoints.
- **ML & Data Processing Modules (Python):**
  - `ml/data_processing.py`: Extracts and preprocesses data.
  - `ml/feature_engineering.py`: Computes financial insights.
  - `ml/model.py`: Stub ML model generating loan decisions.

### Frontend:
- **React.js:** Provides a responsive UI.
- **Visualization:** Uses Plotly for interactive charts.
- **API Communication:** Uses Axios for API interaction.

## Directory Structure
```
ml_statement_analysis/
├── backend/
│   ├── statement_analysis/
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

## Machine Learning Model

- **Function:**
  ```python
  def predict_loan_approval(features):
      net = features.get('overall_summary', {}).get('net', 0)
      if net >= 0:
          return "Approved", 0.85, "Positive net cash flow and recurring income indicate low risk."
      else:
          return "Rejected", 0.85, "Negative net cash flow indicates high risk."
  ```
- **Extensibility:** Can be replaced by a trained model.

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
