"""
URL configuration for TicketRecommend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from events.views import home, event_list, nena, contact_view, event_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', home, name='home'),
                  path('events/', event_list, name='events'),
                  path('nena/', nena, name='nena'),
                  path('contact/', contact_view, name='contact'),
                  path("events/<int:pk>/", event_detail, name="event_detail"),
                  path("", home, name="home"),
                  path("events/", event_list, name="events"),
                  path("events/<int:pk>/", event_detail, name="event_detail"),
                  path("", include("orders.urls")),
                  path("accounts/", include("django.contrib.auth.urls")),  # 👈 login/logout/password views

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
