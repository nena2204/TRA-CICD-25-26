from django.urls import path
from .views import buy_view, contact_view

app_name = "tickets_addons"

urlpatterns = [
    path("buy/", buy_view, name="buy"),
    path("contact/", contact_view, name="contact"),
]
