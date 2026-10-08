from django.conf import settings
from django.db import models
from django.urls import reverse


class Crop(models.Model):
    """Crop Profile — works for ANY crop, per project scope."""
    name = models.CharField(max_length=100, unique=True)
    variety = models.CharField(max_length=100, blank=True)
    typical_days_to_maturity = models.PositiveIntegerField(
        help_text="Typical days from planting to harvest readiness")
    maturity_tolerance_days = models.PositiveIntegerField(
        default=7, help_text="± days window around the typical maturity date")
    expected_yield_per_hectare = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Expected yield in kilograms per hectare (starting estimate)")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}{(' - ' + self.variety) if self.variety else ''}"

    def get_absolute_url(self):
        return reverse("farms:crop_detail", args=[self.pk])


class Plot(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150, blank=True)
    size_hectares = models.DecimalField(max_digits=8, decimal_places=2)
    current_crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True, related_name="plots")
    planting_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("farms:plot_detail", args=[self.pk])


class HarvestSchedule(models.Model):
    """A planned harvest event for a plot, optionally based on an AI prediction."""

    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name="schedules")
    scheduled_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    based_on_prediction = models.BooleanField(default=False)
    labour_needed = models.PositiveIntegerField(default=0, help_text="Number of workers needed")
    equipment_needed = models.CharField(max_length=200, blank=True)
    transport_arranged = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["scheduled_date"]

    def __str__(self):
        return f"{self.plot.name} — {self.scheduled_date} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("farms:schedule_detail", args=[self.pk])


class HarvestRecord(models.Model):
    """Actual harvest result — this is the data that feeds the AI module."""

    class Quality(models.TextChoices):
        POOR = "POOR", "Poor"
        FAIR = "FAIR", "Fair"
        GOOD = "GOOD", "Good"
        EXCELLENT = "EXCELLENT", "Excellent"

    schedule = models.OneToOneField(HarvestSchedule, on_delete=models.CASCADE, related_name="record", null=True, blank=True)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name="harvest_records")
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="harvest_records")
    planting_date = models.DateField()
    harvest_date = models.DateField()
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    quality = models.CharField(max_length=20, choices=Quality.choices, default=Quality.GOOD)
    weather_conditions = models.CharField(max_length=150, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-harvest_date"]

    @property
    def actual_days_to_maturity(self):
        return (self.harvest_date - self.planting_date).days

    @property
    def yield_per_hectare(self):
        if self.plot.size_hectares:
            return round(float(self.quantity_kg) / float(self.plot.size_hectares), 2)
        return None

    def __str__(self):
        return f"{self.crop.name} harvested at {self.plot.name} on {self.harvest_date}"
