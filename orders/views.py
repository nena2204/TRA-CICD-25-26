from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from events.models import TicketType
from .models import Order, OrderItem
from django.template.loader import render_to_string

def _get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    if request.user.is_authenticated:
        cart, _ = Order.objects.get_or_create(status="cart", user=request.user)
    else:
        cart, _ = Order.objects.get_or_create(status="cart", session_key=request.session.session_key, user=None)
    return cart


def cart_detail(request):
    cart = _get_or_create_cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


def cart_add(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    tt_id = request.POST.get("ticket_type_id")
    qty = int(request.POST.get("qty", "1"))
    tt = get_object_or_404(TicketType, pk=tt_id)
    cart = _get_or_create_cart(request)

    item, created = OrderItem.objects.get_or_create(
        order=cart, ticket_type=tt, event=tt.event,
        defaults={"qty": qty, "unit_price": tt.price}
    )
    if not created:
        item.qty += qty
        item.save()

    return JsonResponse({
        "ok": True,
        "count": sum(i.qty for i in cart.items.all()),
        "total": float(cart.total()),
    })


def cart_update(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    item_id = request.POST.get("item_id")
    qty = int(request.POST.get("qty", "1"))
    cart = _get_or_create_cart(request)
    item = get_object_or_404(OrderItem, pk=item_id, order=cart)
    item.qty = max(1, qty)
    item.save()
    return redirect("cart_detail")


def cart_remove(request, item_id):
    cart = _get_or_create_cart(request)
    get_object_or_404(OrderItem, pk=item_id, order=cart).delete()
    return redirect("cart_detail")


@login_required
def checkout(request):
    cart = _get_or_create_cart(request)
    cart.status = "placed"
    cart.save()
    return render(request, "orders/checkout_success.html", {"order": cart})


def cart_mini(request):
    cart = _get_or_create_cart(request)
    html = render_to_string("orders/_mini_cart.html",
                            {"cart": cart}, request=request)
    count = sum(i.qty for i in cart.items.all()) if cart else 0
    total = float(cart.total()) if cart else 0.0
    return JsonResponse({"html": html, "count": count, "total": total})