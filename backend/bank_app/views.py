from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Statement, Transaction
from .serializers import StatementSerializer, TransactionSerializer
from ml import data_processing, feature_engineering, model as ml_model

class StatementUploadView(APIView):
    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the uploaded file via the Statement model.
        statement = Statement.objects.create(file=file_obj)
        file_path = statement.file.path

        # Use the data_processing module to extract transactions.
        transactions = data_processing.extract_transactions(file_path)
        
        # Save extracted transactions to the database (optional for audit).
        for tx in transactions:
            Transaction.objects.create(
                statement=statement,
                date=tx['date'],
                amount=tx['amount'],
                type=tx['type'],
                description=tx['description']
            )
        
        # Compute financial insights (monthly summaries, recurring transactions, etc.).
        insights = feature_engineering.generate_insights(transactions)
        
        # Use the ML model to get a loan recommendation.
        recommendation, probability = ml_model.predict_loan_approval(insights)
        
        response_data = {
            "message": "File processed successfully.",
            "statement_id": statement.id,
            "insights": insights,
            "ml_recommendation": recommendation,
            "ml_probability": probability,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
class AnalysisResultsView(APIView):
    """
    Retrieve analysis insights for a given statement and return ML loan decision details.
    """
    def get(self, request, statement_id, format=None):
        try:
            statement = Statement.objects.get(pk=statement_id)
        except Statement.DoesNotExist:
            return Response({"error": "Statement not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Retrieve all transactions associated with this statement.
        transactions = Transaction.objects.filter(statement=statement)
        transactions_data = TransactionSerializer(transactions, many=True).data
        
        # Generate insights from these transactions.
        insights = feature_engineering.generate_insights(transactions_data)
        
        # Use the ML model to obtain a loan recommendation, probability, and explanation.
        try:
            recommendation, probability = ml_model.predict_loan_approval(insights)
        except Exception as e:
            # In case of error, set fallback values.
            recommendation, probability = None, None
        
        return Response({
            "insights": insights,
            "ml_recommendation": recommendation,
            "ml_probability": probability
        }, status=status.HTTP_200_OK)

class FeedbackView(APIView):
    """
    Endpoint to update the ML model based on manual feedback.
    Expected payload (JSON):
        {
            "approved": true   // true if the human operator approves the loan decision; false otherwise.
        }
    """
    def post(self, request, statement_id, format=None):
        feedback = request.data.get('approved')
        if feedback is None:
            return Response({"error": "Feedback (approved: true/false) not provided."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            statement = Statement.objects.get(id=statement_id)
        except Statement.DoesNotExist:
            return Response({"error": "Statement not found."},
                            status=status.HTTP_404_NOT_FOUND)
        
        # Retrieve all transactions for this statement and re-generate insights.
        tx_queryset = Transaction.objects.filter(statement=statement)
        tx_list = []
        for tx in tx_queryset:
            tx_list.append({
                'date': tx.date.strftime('%Y-%m-%d'),
                'amount': float(tx.amount),
                'description': tx.description,
                'type': tx.type
            })
        insights = feature_engineering.generate_insights(tx_list)
        
        # Map the boolean feedback into a label: 1 (Approved) or 0 (Rejected)
        label = 1 if feedback else 0
        
        # Update the ML model with the new labeled data.
        ml_model.update_model(insights, label)
        
        return Response({"message": "Feedback recorded and model updated."},
                        status=status.HTTP_200_OK)