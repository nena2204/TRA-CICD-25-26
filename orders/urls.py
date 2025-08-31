from django.urls import path
from . import views
from events.views import event_list

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("cart/mini/", views.cart_mini, name="cart_mini"),
    path('events/', event_list, name='events'),

]
