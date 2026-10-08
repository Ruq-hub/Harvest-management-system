from django.conf import settings
from django.db import models


class HarvestPrediction(models.Model):
    """
    An AI-generated recommendation for a plot's harvest date and expected yield.
    Implements the 3-stage design from Chapter Three:
      Stage 1 - Rule-based (crop profile defaults)
      Stage 2 - Statistical (farm's own historical averages)
      Stage 3 - Machine Learning (regression model)
    Always requires human confirmation before being acted upon.
    """

    class Stage(models.TextChoices):
        RULE_BASED = "RULE", "Stage 1 - Rule-based"
        STATISTICAL = "STATS", "Stage 2 - Statistical"
        ML = "ML", "Stage 3 - Machine Learning"

    class ReviewStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        CONFIRMED = "CONFIRMED", "Confirmed"
        ADJUSTED = "ADJUSTED", "Adjusted by user"
        REJECTED = "REJECTED", "Rejected"

    plot = models.ForeignKey("farms.Plot", on_delete=models.CASCADE, related_name="predictions")
    crop = models.ForeignKey("farms.Crop", on_delete=models.CASCADE, related_name="predictions")
    stage_used = models.CharField(max_length=10, choices=Stage.choices)
    predicted_harvest_date = models.DateField()
    predicted_window_start = models.DateField()
    predicted_window_end = models.DateField()
    predicted_yield_kg = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_note = models.CharField(max_length=255, blank=True)

    # Human-in-the-loop fields
    review_status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    user_adjusted_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prediction for {self.plot.name} ({self.crop.name}) — {self.predicted_harvest_date} [{self.get_stage_used_display()}]"

    @property
    def final_date(self):
        """The date actually acted upon: user's adjustment if given, else the prediction."""
        return self.user_adjusted_date or self.predicted_harvest_date
