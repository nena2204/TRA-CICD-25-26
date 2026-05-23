# tickets_addons/apps.py
from django.apps import AppConfig

class TicketsAddonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets_addons'
    verbose_name = "Tickets Addons"

    def ready(self):
        # опционален сигнал – ако го користиш signals.py
        try:
            from .signals import try_connect_ticket_signal
            try_connect_ticket_signal()
        except Exception:
            # тивко игнорирај ако нема signals.py или има нешто непотребно во дев
            pass
