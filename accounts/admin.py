from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

UserAdmin.fieldsets += (("Harvest System Role", {"fields": ("role", "phone_number", "unit")}),)
UserAdmin.add_fieldsets += (("Harvest System Role", {"fields": ("role", "phone_number", "unit")}),)

admin.site.register(User, UserAdmin)
