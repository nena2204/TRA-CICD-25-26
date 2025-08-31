# events/admin.py
from django.contrib import admin
from .models import Event, EventLocation, TicketType

admin.site.register(Event)
admin.site.register(EventLocation)

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "price", "qty", "sale_starts", "sale_ends")
    list_filter  = ("event",)
