from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import HarvestPrediction


@login_required
def review(request, pk):
    prediction = get_object_or_404(HarvestPrediction, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        prediction.reviewed_by = request.user
        prediction.reviewed_at = timezone.now()

        if action == "confirm":
            prediction.review_status = HarvestPrediction.ReviewStatus.CONFIRMED
            messages.success(request, "Prediction confirmed as-is.")
        elif action == "adjust":
            new_date = request.POST.get("adjusted_date")
            if new_date:
                prediction.user_adjusted_date = new_date
            prediction.review_status = HarvestPrediction.ReviewStatus.ADJUSTED
            messages.success(request, "Prediction adjusted and saved with your date.")
        elif action == "reject":
            prediction.review_status = HarvestPrediction.ReviewStatus.REJECTED
            messages.info(request, "Prediction rejected. No schedule was created.")

        prediction.save()

        if prediction.review_status in (HarvestPrediction.ReviewStatus.CONFIRMED, HarvestPrediction.ReviewStatus.ADJUSTED):
            from farms.models import HarvestSchedule
            HarvestSchedule.objects.create(
                plot=prediction.plot,
                scheduled_date=prediction.final_date,
                based_on_prediction=True,
                created_by=request.user,
                notes=f"Auto-created from {prediction.get_stage_used_display()} prediction (reviewed by {request.user}).",
            )
            messages.success(request, "A harvest schedule has been created from this prediction.")

        return redirect("farms:plot_detail", pk=prediction.plot.pk)

    return render(request, "predictions/review.html", {"prediction": prediction})


@login_required
def prediction_list(request):
    predictions = HarvestPrediction.objects.select_related("plot", "crop").all()
    return render(request, "predictions/list.html", {"predictions": predictions})
