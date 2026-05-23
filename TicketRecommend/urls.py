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
from events.views import home, event_list, nena, contact_view, event_detail, HowToBuyView
from django.conf import settings
from django.conf.urls.static import static
from orders.views import checkout_view, checkout_success, ticket_pdf, contact_submit
from tickets_addons.views import checkout_api

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', home, name='home'),
                  path('events/', event_list, name='events'),
                  path('nena/', nena, name='nena'),
                  path('contact/', contact_view, name='contact'),
                  path("events/<int:pk>/", event_detail, name="event_detail"),
                  path("", include("orders.urls")),
                  path("accounts/", include("django.contrib.auth.urls")),
                  path("", include("events.urls")),  # Include events URLs
                  path("how-to-buy/", HowToBuyView.as_view(), name="how-to-buy"),
                  path("checkout/", checkout_view, name="checkout"),
                  path("checkout/success/<uuid:order_id>/", checkout_success, name="checkout_success"),
                  path("ticket/<uuid:order_id>.pdf", ticket_pdf, name="ticket_pdf"),
                  path("contact/submit/", contact_submit, name="contact_submit"),
                  path("", include(("tickets_addons.urls", "tickets_addons"), namespace="tickets_addons")),
                  path("api/checkout/", checkout_api, name="checkout_api"),
                  path('checkout/', include('orders.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
