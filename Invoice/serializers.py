from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'user_id', 'case_id', 'amount', 'due_date', 'status', 'created_at', 'payment_date']
