from django.urls import path
from django.views.generic import RedirectView
from .views import contact_view
from .views_auth import register_view
from .views_profile import profile

urlpatterns = [
    path('contact/', contact_view, name='contact'),
    path('register/', register_view, name='register'),

    # Canonical profile URL
    path('profile/', profile, name='profile'),

    # Backward compat: redirect /accounts/profile/ -> /profile/
    path('accounts/profile/', RedirectView.as_view(pattern_name='profile', permanent=True)),

]
