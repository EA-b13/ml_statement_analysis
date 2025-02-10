from django.urls import path
from .views import StatementUploadView, AnalysisResultsView, FeedbackView

urlpatterns = [
    path('upload/', StatementUploadView.as_view(), name='statement-upload'),
    path('analysis/<int:statement_id>/', AnalysisResultsView.as_view(), name='analysis-results'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
]