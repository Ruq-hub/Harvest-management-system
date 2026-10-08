"""
Harvest prediction engine.

Implements the 3-stage design from Chapter Three (3.8):
  Stage 1 (RULE)  - uses the Crop profile's typical_days_to_maturity.
                     Always available, works for ANY crop from day one.
  Stage 2 (STATS) - once >=3 harvest records exist for a crop, uses the
                     farm's own historical mean/std of actual days-to-maturity
                     and actual yield, which is more accurate than Stage 1's
                     generic default.
  Stage 3 (ML)    - once >=30 harvest records exist for a crop (pooled across
                     plots), trains a simple scikit-learn regression model
                     (Linear Regression) to predict days-to-harvest and yield
                     from plot size and planting month.

All stages return a HarvestPrediction object that is PENDING review --
the system never auto-schedules a harvest from a prediction alone.
"""
import datetime
import statistics

from django.utils import timezone

from farms.models import HarvestRecord
from .models import HarvestPrediction

STAGE2_MIN_RECORDS = 3
STAGE3_MIN_RECORDS = 30


def _records_for_crop(crop):
    return list(HarvestRecord.objects.filter(crop=crop))


def predict_for_plot(plot):
    """Main entry point: returns an unsaved HarvestPrediction for a plot's current crop."""
    crop = plot.current_crop
    if crop is None or plot.planting_date is None:
        return None

    records = _records_for_crop(crop)

    if len(records) >= STAGE3_MIN_RECORDS:
        return _predict_stage3_ml(plot, crop, records)
    elif len(records) >= STAGE2_MIN_RECORDS:
        return _predict_stage2_stats(plot, crop, records)
    else:
        return _predict_stage1_rule(plot, crop)


def _predict_stage1_rule(plot, crop):
    predicted_date = plot.planting_date + datetime.timedelta(days=crop.typical_days_to_maturity)
    tolerance = datetime.timedelta(days=crop.maturity_tolerance_days)
    predicted_yield = float(crop.expected_yield_per_hectare) * float(plot.size_hectares)

    return HarvestPrediction(
        plot=plot,
        crop=crop,
        stage_used=HarvestPrediction.Stage.RULE_BASED,
        predicted_harvest_date=predicted_date,
        predicted_window_start=predicted_date - tolerance,
        predicted_window_end=predicted_date + tolerance,
        predicted_yield_kg=round(predicted_yield, 2),
        confidence_note=(
            f"Based on {crop.name}'s standard profile (no harvest history yet for this crop). "
            f"Accuracy will improve once real harvest records are entered."
        ),
    )


def _predict_stage2_stats(plot, crop, records):
    days_list = [r.actual_days_to_maturity for r in records]
    yield_per_ha_list = [r.yield_per_hectare for r in records if r.yield_per_hectare]

    mean_days = statistics.mean(days_list)
    std_days = statistics.pstdev(days_list) if len(days_list) > 1 else crop.maturity_tolerance_days
    mean_yield_per_ha = statistics.mean(yield_per_ha_list) if yield_per_ha_list else float(crop.expected_yield_per_hectare)

    predicted_date = plot.planting_date + datetime.timedelta(days=round(mean_days))
    tolerance = datetime.timedelta(days=max(1, round(std_days)))
    predicted_yield = mean_yield_per_ha * float(plot.size_hectares)

    return HarvestPrediction(
        plot=plot,
        crop=crop,
        stage_used=HarvestPrediction.Stage.STATISTICAL,
        predicted_harvest_date=predicted_date,
        predicted_window_start=predicted_date - tolerance,
        predicted_window_end=predicted_date + tolerance,
        predicted_yield_kg=round(predicted_yield, 2),
        confidence_note=(
            f"Based on {len(records)} past harvest record(s) of {crop.name} on this farm "
            f"(avg {mean_days:.0f} days to maturity)."
        ),
    )


def _predict_stage3_ml(plot, crop, records):
    try:
        import pandas as pd
        from sklearn.linear_model import LinearRegression
    except ImportError:
        return _predict_stage2_stats(plot, crop, records)

    rows = []
    for r in records:
        rows.append({
            "plot_size": float(r.plot.size_hectares),
            "planting_month": r.planting_date.month,
            "days_to_maturity": r.actual_days_to_maturity,
            "yield_per_ha": r.yield_per_hectare or 0,
        })
    df = pd.DataFrame(rows)

    X = df[["plot_size", "planting_month"]]
    days_model = LinearRegression().fit(X, df["days_to_maturity"])
    yield_model = LinearRegression().fit(X, df["yield_per_ha"])

    x_new = [[float(plot.size_hectares), plot.planting_date.month]]
    predicted_days = max(1, round(days_model.predict(x_new)[0]))
    predicted_yield_per_ha = max(0, yield_model.predict(x_new)[0])

    predicted_date = plot.planting_date + datetime.timedelta(days=int(predicted_days))
    tolerance = datetime.timedelta(days=crop.maturity_tolerance_days // 2 or 3)
    predicted_yield = predicted_yield_per_ha * float(plot.size_hectares)

    return HarvestPrediction(
        plot=plot,
        crop=crop,
        stage_used=HarvestPrediction.Stage.ML,
        predicted_harvest_date=predicted_date,
        predicted_window_start=predicted_date - tolerance,
        predicted_window_end=predicted_date + tolerance,
        predicted_yield_kg=round(predicted_yield, 2),
        confidence_note=(
            f"Machine learning model trained on {len(records)} harvest records of {crop.name}."
        ),
    )
