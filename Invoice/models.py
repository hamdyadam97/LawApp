from django.db import models
from django.utils import timezone

from User.models import  User


class Invoice(models.Model):
    user = models.ForeignKey('User.User', on_delete=models.SET_NULL, related_name='invoices_user',null=True)
    case = models.ForeignKey('Office.Case', on_delete=models.SET_NULL, null=True, related_name='invoices_case',)
    amount = models.FloatField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, default="Unpaid")
    created_at = models.DateTimeField(default=timezone.now)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_card = models.ForeignKey('PaymentCard', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices_payment_card')

    def __str__(self):
        return f"Invoice {self.id} for user {self.user.id}"

    class Meta:
        ordering = ['due_date']

class PaymentCard(models.Model):
    card_number = models.CharField(max_length=16)
    card_type = models.CharField(max_length=50)
    expiry_date = models.CharField(max_length=10)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='payment_cards_user')

    def __str__(self):
        return f"Payment Card {self.card_number} for user {self.user.id}"

    class Meta:
        ordering = ['expiry_date']



class Event(models.Model):
    message = models.CharField(max_length=255)
    date = models.CharField(max_length=20)
    time = models.CharField(max_length=10)
    lawyer = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name="events_lawyer")
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name="events_user")

    def __str__(self):
        return f"Event: {self.message} on {self.date} at {self.time}"
