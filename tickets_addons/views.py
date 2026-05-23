from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from .forms import BuyForm, ContactForm
from .models import BuyOrder
from .utils import generate_qr_png, send_ticket_email, send_contact_email_to_admin

def buy_view(request):
    """
    Независна buy рута (не ја допира постоечката). Креира BuyOrder и праќа мејл со QR.
    """
    if request.method == "POST":
        form = BuyForm(request.POST)
        if form.is_valid():
            order: BuyOrder = form.save()
            qr_payload = (
                f"TICKET_ID={order.id}\n"
                f"EVENT={order.event_title}\n"
                f"NAME={order.first_name} {order.last_name}\n"
                f"EMAIL={order.email}"
            )
            qr_buf = generate_qr_png(qr_payload)
            ctx = {
                "event_title": order.event_title,
                "first_name": order.first_name,
                "last_name": order.last_name,
                "address": order.address,
            }
            send_ticket_email(order.email, ctx, qr_buf, f"ticket-{order.id}.png")
            messages.success(request, "Успешно купивте билет! Ви испративме е-пошта со QR код.")
            return redirect(reverse("tickets_addons:buy"))
    else:
        form = BuyForm()
    return render(request, "tickets_addons/buy.html", {"form": form})

def contact_view(request):
    """
    Контакт форма што праќа е-пошта до дадената адреса (без да менува ништо друго).
    """
    admin_email = getattr(settings, "CONTACT_ADMIN_EMAIL", "nikolovanena123@gmail.com")
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            send_contact_email_to_admin(
                {
                    "name": form.cleaned_data["name"],
                    "email": form.cleaned_data["email"],
                    "message": form.cleaned_data["message"],
                },
                admin_email,
            )
            messages.success(request, "Пораката е испратена. Ви благодариме!")
            return redirect(reverse("tickets_addons:contact"))
    else:
        form = ContactForm()
    return render(request, "tickets_addons/contact.html", {"form": form})

# tickets_addons/views.py
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from .utils import generate_qr_png, send_ticket_email

@require_POST
def checkout_api(request):
    """
    Прима JSON или form-encoded: full_name, phone, email, street, street_no, zip_code, city
    + чита кошничка од session (ако ја користиш), креира нарачка (опц), праќа мејл со QR,
    па враќа JSON со redirect URL (твојата постоечка success страница /checkout/).
    """
    data = request.POST or request.JSON if hasattr(request, "JSON") else {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    street = data.get("street", "").strip()
    street_no = data.get("street_no", "").strip()
    zip_code = data.get("zip_code", "").strip()
    city = data.get("city", "").strip()

    if not (full_name and email and street and city):
        return JsonResponse({"ok": False, "error": "Недостасуваат задолжителни полиња."}, status=400)

    # 1) земи кошничка (пример од session)
    cart = request.session.get("cart", {})  # приспособи ако твојот cart е поинаков
    if not cart:
        return JsonResponse({"ok": False, "error": "Кошничката е празна."}, status=400)

    # 2) пресметај тотал
    try:
        total = sum(item["price"] * item["qty"] for item in cart.values())
    except Exception:
        total = 0

    # 3) генерирај QR payload (ID можеш да ставиш timestamp ако немаш Order)
    order_id = timezone.now().strftime("ORD-%Y%m%d-%H%M%S")
    payload = f"ORDER={order_id}\nNAME={full_name}\nEMAIL={email}\nTOTAL={total}"
    qr_buf = generate_qr_png(payload)

    # 4) испрати мејл со детали + QR (картите наместо „лекови“)
    ctx = {
        "order_id": order_id,
        "full_name": full_name,
        "phone": phone,
        "street": street, "street_no": street_no,
        "zip_code": zip_code, "city": city,
        "items": cart.values(),
        "total": total,
        "created_at": timezone.now(),
    }
    from django.template.loader import render_to_string
    html_body = render_to_string("tickets_addons/email_order.html", ctx)

    from django.core.mail import EmailMessage
    subject = f"Вашата нарачка е примена – {order_id}"
    email_msg = EmailMessage(subject=subject, body=html_body, to=[email])
    email_msg.content_subtype = "html"
    email_msg.attach(f"ticket-{order_id}.png", qr_buf.read(), "image/png")
    email_msg.send(fail_silently=False)

    # 5) испразни кошничка (опционално)
    request.session["cart"] = {}

    return JsonResponse({"ok": True, "redirect": "/checkout/"})
