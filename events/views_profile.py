from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from events.models import Event
from orders.models import Order
from collections import Counter
from datetime import datetime

@login_required
def profile(request):
    # Get user's orders
    user_orders = Order.objects.filter(user=request.user, status='placed')

    # If user has no orders, return empty recommendations
    if not user_orders.exists():
        return render(request, 'registration/profile.html', {
            'recommendations': []
        })

    # Count purchases by category to determine priority
    category_counts = Counter()
    purchased_event_ids = set()

    for order in user_orders:
        for item in order.items.all():
            category_counts[item.event.category] += 1
            purchased_event_ids.add(item.event.id)

    # Sort categories by number of purchases
    sorted_categories = sorted(
        category_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Get current date for filtering
    now = timezone.now()

    # Prepare recommendations
    recommendations = []

    for category, count in sorted_categories:
        # Get only future events from this category
        category_events = Event.objects.filter(
            category=category,
            datetime__gt=now  # Only future events
        ).exclude(
            id__in=purchased_event_ids  # Exclude purchased events
        ).order_by('datetime')

        if category_events.exists():
            recommendations.append({
                'category': category,
                'events': category_events,
                'purchase_count': count
            })

    return render(request, 'registration/profile.html', {
        'recommendations': recommendations
    })
