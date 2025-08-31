from .models import Order, OrderItem

def merge_session_cart_into_user(request, user):
    sk = request.session.session_key
    if not sk:
        return
    try:
        session_cart = Order.objects.get(status="cart", session_key=sk, user__isnull=True)
    except Order.DoesNotExist:
        return

    user_cart, _ = Order.objects.get_or_create(status="cart", user=user)
    for it in session_cart.items.all():
        target, created = OrderItem.objects.get_or_create(
            order=user_cart, ticket_type=it.ticket_type, event=it.event,
            defaults={"qty": it.qty, "unit_price": it.unit_price}
        )
        if not created:
            target.qty += it.qty
            target.save()
    session_cart.delete()
