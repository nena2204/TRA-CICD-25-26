from django.urls import path
from .views import contact_view
from .views_auth import register_view
from .views_profile import profile

urlpatterns = [
    path('contact/', contact_view, name='contact'),
    path('accounts/register/', register_view, name='register'),
    path('accounts/profile/', profile, name='profile'),  # Added profile URL pattern
]
