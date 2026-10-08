from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.HMSLoginView.as_view(), name="login"),
    path("logout/", views.HMSLogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
]
