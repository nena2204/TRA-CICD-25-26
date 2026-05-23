from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from events.models import TicketType
from .models import Order, OrderItem


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
    return render(request, "orders/checkout.html", {"order": cart})


def cart_mini(request):
    cart = _get_or_create_cart(request)
    html = render_to_string("orders/_mini_cart.html",
                            {"cart": cart}, request=request)
    count = sum(i.qty for i in cart.items.all()) if cart else 0
    total = float(cart.total()) if cart else 0.0
    return JsonResponse({"html": html, "count": count, "total": total})


# orders/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
# from xhtml2pdf import pisa
from orders.forms import CheckoutForm, ContactForm
from orders.models import TicketOrder


def _cart_from_session(request):
    # очекуваме да имаш session cart. Ако ја имаш својата структура, само мапирај.
    # пример структура:
    # request.session["cart"] = [{"event":"Bioderma Atoderm SO...","ticket":"General","qty":1,"price":1336}]
    return request.session.get("cart", [])




def _attach_pdf_to_order(order, request):
    import io, os
    ticket_url = request.build_absolute_uri(f"/ticket/{order.id}.pdf")

    # QR во меморија (остава исто како што го правиш)
    qr_io = io.BytesIO()
    qrcode.make(ticket_url).save(qr_io, format="PNG")
    qr_png_bytes = qr_io.getvalue()

    html = render_to_string("orders/ticket_pdf.html", {
        "order": order,
        "qr_png_bytes": qr_png_bytes,
        "logo_url": request.build_absolute_uri("/static/img/ticketo-logo.png"),
    })

    path = f"{settings.MEDIA_ROOT}/tickets/{order.id}.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        # xhtml2pdf конверзија
        pisa_status = pisa.CreatePDF(src=html, dest=f, link_callback=None)
        if pisa_status.err:
            # ако сакаш логика за fallback/raise:
            raise RuntimeError("PDF generation failed")

    order.pdf.name = f"tickets/{order.id}.pdf"
    order.save(update_fields=["pdf"])


def ticket_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.pdf:
        with open(order.pdf.path, "rb") as f:
            data = f.read()
        return HttpResponse(data, content_type="application/pdf")
    # fallback: (ре)генерирај ако недостига
    _attach_pdf_to_order(order, request)
    with open(order.pdf.path, "rb") as f:
        return HttpResponse(f.read(), content_type="application/pdf")


def checkout_success(request, order_id=None):
    order = None
    if order_id is not None:
        order = get_object_or_404(Order, pk=order_id)
    else:
        last_id = request.session.get('last_order_id')
        if last_id:
            order = Order.objects.filter(pk=last_id).first()

    # NOTE: app-scoped path
    return render(request, "orders/checkout_success.html", {"order": order})

def contact_submit(request):
    # форма од Contact панелот – праќа на зададениот мејл
    if request.method != "POST":
        return HttpResponse(status=405)
    form = ContactForm(request.POST)
    if not form.is_valid():
        return HttpResponse("Invalid", status=400)
    send_mail(
        subject=f"[Ticketo.mk] Порака од {form.cleaned_data['name']}",
        message=f"Од: {form.cleaned_data['email']}\n\n{form.cleaned_data['message']}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["nikolovanena123@gmail.com"],
    )
    return HttpResponse("OK")


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CheckoutForm
from .utils import generate_qr_png, send_ticket_email
from .models import Order  # ако веќе имаш Order модел

def checkout_view(request):
    cart = request.session.get("cart", {})  # пример, ако користиш session cart
    if not cart:
        messages.error(request, "Вашата кошничка е празна.")
        return redirect("events")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # 1. зачувај нарачка во база
            order = Order.objects.create(
                full_name=data["full_name"],
                phone=data["phone"],
                email=data["email"],
                street=data["street"],
                street_no=data["street_no"],
                zip_code=data["zip_code"],
                city=data["city"],
                items=cart,
                total_price=sum(item["price"]*item["qty"] for item in cart.values())
            )

            # 2. генерирај QR код (наместо лекови → карта)
            payload = f"ORDER={order.id}\nNAME={order.full_name}\nEMAIL={order.email}"
            qr_buf = generate_qr_png(payload)

            # 3. прати мејл со детали
            ctx = {
                "order": order,
                "items": cart.values()
            }
            send_ticket_email(order.email, ctx, qr_buf, f"ticket-{order.id}.png")

            # 4. испразни кошничка
            request.session["cart"] = {}

            return redirect("checkout_success")
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})