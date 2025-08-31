def cart_count(request):
    from .models import Order
    try:
        if request.user.is_authenticated:
            cart = Order.objects.filter(status="cart", user=request.user).first()
        else:
            sk = request.session.session_key or ""
            cart = Order.objects.filter(status="cart", session_key=sk, user__isnull=True).first()
        count = sum(i.qty for i in cart.items.all()) if cart else 0
    except Exception:
        count = 0
    return {"CART_COUNT": count}
