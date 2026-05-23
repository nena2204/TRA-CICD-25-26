from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import generate_qr_png, send_ticket_email

def try_connect_ticket_signal():
    """
    Ако постои модел `Ticket` (во било кое app) и има поле `email`,
    ќе закачиме post_save хендлер за автоматски да испраќаме QR мејл.
    Ова не бара промена на твојот код — само додавање на ова app.
    """
    # обиди се да најдеш модел по име 'Ticket' во сите апликации
    ticket_model = None
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model("Ticket")
            # провери условно дали има поле email (за да не кршиш други модели)
            if "email" in [f.name for f in model._meta.get_fields()]:
                ticket_model = model
                break
        except LookupError:
            continue

    if not ticket_model:
        return  # нема погоден модел, прекини

    @receiver(post_save, sender=ticket_model, dispatch_uid="tickets_addons_ticket_postsave")
    def on_ticket_created(sender, instance, created, **kwargs):
        """
        Ако се креира нов Ticket (создаден = True), прати мејл со QR.
        Очекуваме instance да има атрибути:
          - email (задолжително)
          - event/title или __str__
          - first_name/last_name/address (ако ги нема, ќе пополниме со празно)
        """
        if not created:
            return
        try:
            to_email = getattr(instance, "email", None)
            if not to_email:
                return
            event_title = getattr(getattr(instance, "event", None), "title", None) or \
                          getattr(instance, "title", None) or str(instance)
            first_name = getattr(instance, "first_name", "") or ""
            last_name = getattr(instance, "last_name", "") or ""
            address = getattr(instance, "address", "") or ""

            payload = (
                f"TICKET_ID={getattr(instance, 'id', '')}\n"
                f"EVENT={event_title}\n"
                f"NAME={first_name} {last_name}\n"
                f"EMAIL={to_email}"
            )
            qr_buf = generate_qr_png(payload)
            ctx = {
                "event_title": event_title,
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
            }
            filename = f"ticket-{getattr(instance, 'id', 'x')}.png"
            send_ticket_email(to_email, ctx, qr_buf, filename)
        except Exception:
            # тивко игнорирај за да не влијае на твојот flow
            pass
