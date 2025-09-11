from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from .models import Event

from django import forms
# Create your views here.


def event_list(request):
    events = Event.objects.all().order_by('datetime')

    return render(request, 'events/all-events.html', {'events': events})


def nena(request):
    events = Event.objects.all().order_by('datetime')
    return render(request, 'events/all-events.html', {'events': events})


def contact(request):
    events = Event.objects.all().order_by('datetime')
    return render(request, 'events/contact.html', {'events': events})


def home(request):
    carousel_events = Event.objects.filter(is_popular=True).order_by('datetime')[:5]
    events = Event.objects.order_by('datetime')
    upcoming_events = (
        Event.objects
        .filter(is_popular=True)
        .order_by('datetime')[:4]
    )

    has_popular = events.filter(is_popular=True).exists()
    sections = {
        "concert": Event.objects.filter(category="concert").order_by('datetime')[:3],
        "festival": Event.objects.filter(category="festival").order_by('datetime')[:3],
        "theatre": Event.objects.filter(category="theatre").order_by('datetime')[:1],
        "classical": Event.objects.filter(category="classical").order_by('datetime')[:1],
        "sport": Event.objects.filter(category="sport").order_by('datetime')[:1],
        "other": Event.objects.filter(category="other").order_by('datetime')[:3],
    }

    all_events = Event.objects.order_by('datetime')  # ← без paginator
    print("ALL COUNT =", all_events.count())

    return render(request, 'events/home.html', {
        'carousel_events': carousel_events,
        'sections': sections,
        'all_events': all_events,
        'upcoming_events': upcoming_events,
    })


def ping(request):
    return render(request, 'base.html')


from django.shortcuts import get_object_or_404, render
from .models import Event


def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.select_related("location"),
        pk=pk
    )
    ticket_types = getattr(event, "ticket_types", None)
    if ticket_types:
        ticket_types = event.ticket_types.all().order_by("price")

    return render(request, "events/event_detail.html", {
        "event": event,
        "ticket_types": ticket_types,  # ако имаш типови на карти
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from .forms import ContactForm

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data.get('subject') or "Нова порака"
            message = form.cleaned_data['message']

            full_message = f"Име: {name}\nEmail: {email}\n\nПорака:\n{message}"

            send_mail(
                subject,
                full_message,
                None,  # ќе користи DEFAULT_FROM_EMAIL
                ["contact@ticketo.mk"],  # смени со твојата адреса
                fail_silently=False,
            )
            messages.success(request, "Пораката е успешно пратена!")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "events/contact.html", {"form": form})


class HowToBuyView(TemplateView):
    template_name = "events/how_to_buy.html"