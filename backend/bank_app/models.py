from django.db import models

# Create your models here.

class Statement(models.Model):
    file = models.FileField(upload_to='statements/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10)  # e.g., 'deposit', 'withdrawal'
    description = models.CharField(max_length=255)
