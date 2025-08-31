from django.db import models
from django.conf import settings
from events.models import Event, TicketType


class Order(models.Model):
    STATUS_CHOICES = [
        ("cart", "Cart"),
        ("placed", "Placed"),
        ("canceled", "Canceled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(i.subtotal() for i in self.items.all())

    def __str__(self):
        who = self.user.username if self.user else self.session_key or "guest"
        return f"Order #{self.pk} ({self.status}) – {who}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)

    def subtotal(self):
        return self.qty * self.unit_price
