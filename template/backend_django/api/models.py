from django.db import models


class PredictionLog(models.Model):
    """Saves every prediction so you can show a history page.
    TODO: add your own models here (e.g. User profile, Book, Customer ...)."""
    created_at = models.DateTimeField(auto_now_add=True)
    input_data = models.JSONField()
    prediction = models.CharField(max_length=100)
    probabilities = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} → {self.prediction}"
