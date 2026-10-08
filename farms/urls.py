from django.urls import path
from . import views

app_name = "farms"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("crops/", views.crop_list, name="crop_list"),
    path("crops/new/", views.crop_create, name="crop_create"),
    path("crops/<int:pk>/", views.crop_detail, name="crop_detail"),

    path("plots/", views.plot_list, name="plot_list"),
    path("plots/new/", views.plot_create, name="plot_create"),
    path("plots/<int:pk>/", views.plot_detail, name="plot_detail"),
    path("plots/<int:pk>/predict/", views.plot_predict, name="plot_predict"),

    path("schedules/", views.schedule_list, name="schedule_list"),
    path("schedules/new/", views.schedule_create, name="schedule_create"),
    path("schedules/<int:pk>/", views.schedule_detail, name="schedule_detail"),
    path("schedules/<int:pk>/confirm/", views.schedule_confirm, name="schedule_confirm"),

    path("records/", views.record_list, name="record_list"),
    path("records/new/", views.record_create, name="record_create"),

    path("reports/", views.reports, name="reports"),
]
