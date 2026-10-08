from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("predictions/", include("predictions.urls")),
    path("", include("farms.urls")),
]
