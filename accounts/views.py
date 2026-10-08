from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm


class HMSLoginView(LoginView):
    template_name = "accounts/login.html"


class HMSLogoutView(LogoutView):
    next_page = "accounts:login"


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("farms:dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})
