from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ["name", "secret_code", "balance", "date_and", "is_active"]
    list_display_links = ["name"]
    list_per_page = 10


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        "user_name",
        "telegram_id",
        "phone_number",
        "role",
        "secret_code",
        "language",
        "is_active",
    ]
    list_display_links = ["user_name"]
    list_per_page = 50


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "gym",
        "client",
        "balanse",
        "price",
        "is_trainer",
        "is_active",
    ]
    list_display_links = ["gym", "client"]
    list_per_page = 50


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "gym",
        "client",
        "is_trainer",
        "payment",
    ]
    list_display_links = ["gym", "client"]
    list_per_page = 50


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = [
        "user_name",
        "telegram_id",
    ]
    list_display_links = ["user_name"]
