from django import forms
from .models import Crop, Plot, HarvestSchedule, HarvestRecord


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs["class"] = (existing + " form-check-input").strip()
            else:
                field.widget.attrs["class"] = (existing + " form-control").strip()


class CropForm(BootstrapModelForm):
    class Meta:
        model = Crop
        fields = ["name", "variety", "typical_days_to_maturity", "maturity_tolerance_days",
                  "expected_yield_per_hectare", "notes"]


class PlotForm(BootstrapModelForm):
    class Meta:
        model = Plot
        fields = ["name", "location", "size_hectares", "current_crop", "planting_date"]
        widgets = {"planting_date": forms.DateInput(attrs={"type": "date"})}


class HarvestScheduleForm(BootstrapModelForm):
    class Meta:
        model = HarvestSchedule
        fields = ["plot", "scheduled_date", "labour_needed", "equipment_needed", "transport_arranged", "notes"]
        widgets = {"scheduled_date": forms.DateInput(attrs={"type": "date"})}


class HarvestRecordForm(BootstrapModelForm):
    class Meta:
        model = HarvestRecord
        fields = ["plot", "crop", "planting_date", "harvest_date", "quantity_kg", "quality",
                  "weather_conditions", "notes"]
        widgets = {
            "planting_date": forms.DateInput(attrs={"type": "date"}),
            "harvest_date": forms.DateInput(attrs={"type": "date"}),
        }
