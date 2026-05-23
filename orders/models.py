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


# app: orders/models.py
import uuid
from django.db import models

class TicketOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    street = models.CharField(max_length=120)
    street_no = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=60)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # зачувај што има во кошничка (еден или повеќе типови карти)
    items = models.JSONField(default=list)  # [{"event":"Concert X","ticket":"VIP","qty":2,"price":...}]
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="created")
    pdf = models.FileField(upload_to="tickets/", blank=True, null=True)  # ќе го пополниме

    def __str__(self):
        return f"{self.id} • {self.email}"
