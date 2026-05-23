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

# orders/utils.py
# import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def generate_qr_png(data: str) -> BytesIO:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def send_ticket_email(to_email: str, context: dict, qr_bytes: BytesIO, filename: str):
    subject = f"Вашата карта е успешна – #{context['order'].id}"
    html_body = render_to_string("orders/email_order.html", context)
    email = EmailMessage(subject=subject, body=html_body, to=[to_email])
    email.content_subtype = "html"
    email.attach(filename=filename, content=qr_bytes.read(), mimetype="image/png")
    email.send(fail_silently=False)
