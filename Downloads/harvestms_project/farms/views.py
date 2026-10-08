from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from predictions.engine import predict_for_plot
from predictions.models import HarvestPrediction
from .models import Crop, Plot, HarvestSchedule, HarvestRecord
from .forms import CropForm, PlotForm, HarvestScheduleForm, HarvestRecordForm


@login_required
def dashboard(request):
    today = timezone.localdate()
    upcoming = HarvestSchedule.objects.filter(
        scheduled_date__gte=today, status__in=["PLANNED", "CONFIRMED"]
    ).select_related("plot")[:8]
    pending_predictions = HarvestPrediction.objects.filter(
        review_status=HarvestPrediction.ReviewStatus.PENDING
    ).select_related("plot", "crop")[:8]
    context = {
        "crop_count": Crop.objects.count(),
        "plot_count": Plot.objects.count(),
        "record_count": HarvestRecord.objects.count(),
        "upcoming": upcoming,
        "pending_predictions": pending_predictions,
    }
    return render(request, "farms/dashboard.html", context)


# ---------- Crops ----------
@login_required
def crop_list(request):
    crops = Crop.objects.all()
    return render(request, "farms/crop_list.html", {"crops": crops})


@login_required
def crop_create(request):
    form = CropForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Crop profile created.")
        return redirect("farms:crop_list")
    return render(request, "farms/crop_form.html", {"form": form, "title": "Add Crop Profile"})


@login_required
def crop_detail(request, pk):
    crop = get_object_or_404(Crop, pk=pk)
    records = crop.harvest_records.all()[:10]
    return render(request, "farms/crop_detail.html", {"crop": crop, "records": records})


# ---------- Plots ----------
@login_required
def plot_list(request):
    plots = Plot.objects.select_related("current_crop").all()
    return render(request, "farms/plot_list.html", {"plots": plots})


@login_required
def plot_create(request):
    form = PlotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        plot = form.save()
        messages.success(request, "Plot registered.")
        return redirect("farms:plot_detail", pk=plot.pk)
    return render(request, "farms/plot_form.html", {"form": form, "title": "Register Plot"})


@login_required
def plot_detail(request, pk):
    plot = get_object_or_404(Plot, pk=pk)
    schedules = plot.schedules.all()
    records = plot.harvest_records.all()
    latest_prediction = plot.predictions.first()
    return render(request, "farms/plot_detail.html", {
        "plot": plot, "schedules": schedules, "records": records, "prediction": latest_prediction,
    })


@login_required
def plot_predict(request, pk):
    plot = get_object_or_404(Plot, pk=pk)
    prediction = predict_for_plot(plot)
    if prediction is None:
        messages.error(request, "This plot needs a current crop and planting date before it can be predicted.")
        return redirect("farms:plot_detail", pk=plot.pk)
    prediction.save()
    messages.info(request, "New AI prediction generated — please review and confirm.")
    return redirect("predictions:review", pk=prediction.pk)


# ---------- Harvest Schedules ----------
@login_required
def schedule_create(request):
    form = HarvestScheduleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        schedule = form.save(commit=False)
        schedule.created_by = request.user
        schedule.save()
        messages.success(request, "Harvest scheduled.")
        return redirect("farms:schedule_detail", pk=schedule.pk)
    return render(request, "farms/schedule_form.html", {"form": form, "title": "Schedule a Harvest"})


@login_required
def schedule_list(request):
    schedules = HarvestSchedule.objects.select_related("plot").all()
    return render(request, "farms/schedule_list.html", {"schedules": schedules})


@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(HarvestSchedule, pk=pk)
    return render(request, "farms/schedule_detail.html", {"schedule": schedule})


@login_required
def schedule_confirm(request, pk):
    schedule = get_object_or_404(HarvestSchedule, pk=pk)
    schedule.status = HarvestSchedule.Status.CONFIRMED
    schedule.save()
    messages.success(request, "Schedule confirmed. Labour/equipment/transport can now be finalised.")
    return redirect("farms:schedule_detail", pk=schedule.pk)


# ---------- Harvest Records ----------
@login_required
def record_create(request):
    initial = {}
    schedule_id = request.GET.get("schedule")
    schedule = None
    if schedule_id:
        schedule = get_object_or_404(HarvestSchedule, pk=schedule_id)
        initial = {
            "plot": schedule.plot,
            "crop": schedule.plot.current_crop,
            "planting_date": schedule.plot.planting_date,
            "harvest_date": schedule.scheduled_date,
        }
    form = HarvestRecordForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.recorded_by = request.user
        if schedule:
            record.schedule = schedule
        record.save()
        if schedule:
            schedule.status = HarvestSchedule.Status.COMPLETED
            schedule.save()
        messages.success(request, "Harvest record saved. This data will improve future AI predictions for this crop.")
        return redirect("farms:record_list")
    return render(request, "farms/record_form.html", {"form": form, "title": "Record a Harvest"})


@login_required
def record_list(request):
    records = HarvestRecord.objects.select_related("plot", "crop").all()
    return render(request, "farms/record_list.html", {"records": records})


# ---------- Reports ----------
@login_required
def reports(request):
    from django.db.models import Sum, Count, Avg
    by_crop = (HarvestRecord.objects.values("crop__name")
               .annotate(total_kg=Sum("quantity_kg"), harvests=Count("id"))
               .order_by("-total_kg"))
    return render(request, "farms/reports.html", {"by_crop": by_crop})
