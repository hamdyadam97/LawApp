from django.db import models

from Office.models import Case
from User.models import User


# Create your models here.


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedbacks")
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.name} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"