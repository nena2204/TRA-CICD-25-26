from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
#
# class EventCategory(models.Model):
#     name = models.CharField(max_length=100)
#     def __str__(self):
#         return self.name


class EventLocation(models.Model):
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    name=models.CharField(max_length=100)
    capacity=models.IntegerField()

    def __str__(self):
        return f'{self.city} {self.address} {self.capacity}'


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("concert", "Concert"),
        ("festival", "Festival"),
        ("theatre", "Theatre"),
        ("classical", "Classical Music"),
        ("sport", "Sport"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=150)
    # category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    category=models.CharField(max_length=100,choices=CATEGORY_CHOICES)
    datetime=models.DateTimeField()
    description = models.TextField()
    ticket_price=models.IntegerField() #moze i DecimalField ili??
    image=models.ImageField(upload_to='images/')
    location=models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    is_popular=models.BooleanField(default=False)


    def __str__(self):
        return self.name

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type=models.CharField(max_length=50)

    def __str__(self):
        return self.event.name


class TicketType(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="ticket_types"
    )
    name  = models.CharField(max_length=120)         # „Регуларен билет“, „ВИП“, ...
    price = models.DecimalField(max_digits=9, decimal_places=2)
    qty   = models.PositiveIntegerField(null=True, blank=True)  # опционално ограничување
    sale_starts = models.DateTimeField(null=True, blank=True)
    sale_ends   = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.event.name} – {self.name}"

