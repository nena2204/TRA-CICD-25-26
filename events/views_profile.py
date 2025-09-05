from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from events.models import Event
from orders.models import Order
from collections import Counter
from itertools import chain
from datetime import datetime

@login_required
def profile(request):
    now = timezone.now()

    # Get user's orders and split them into active and expired
    user_orders = Order.objects.filter(user=request.user, status='placed').prefetch_related('items__event')

    active_tickets = []
    expired_tickets = []

    # Track categories and their purchase counts
    category_counts = Counter()
    purchased_event_ids = set()

    for order in user_orders:
        for item in order.items.all():
            # Build ticket info
            ticket_info = {
                'event_name': item.event.name,
                'event_date': item.event.datetime,
                'order_date': order.created_at,
                'quantity': item.qty,
                'status': 'Active' if item.event.datetime > now else 'Past'
            }

            # Sort into active/expired
            if item.event.datetime > now:
                active_tickets.append(ticket_info)
            else:
                expired_tickets.append(ticket_info)

            # Track category statistics
            category_counts[item.event.category] += item.qty
            purchased_event_ids.add(item.event.id)

    # Sort tickets by date
    active_tickets.sort(key=lambda x: x['event_date'])
    expired_tickets.sort(key=lambda x: x['event_date'], reverse=True)

    recommendations = []

    if category_counts:  # Only process if user has purchased tickets
        # Get the highest purchase count
        max_count = max(category_counts.values())

        # Find all categories with the maximum count (there could be ties)
        top_categories = [cat for cat, count in category_counts.items()
                         if count == max_count]

        # Get other categories sorted by count
        other_categories = [cat for cat, count in category_counts.most_common()
                          if cat not in top_categories]

        # Function to get recommendations for a category
        def get_category_recommendations(category, limit=4):
            return Event.objects.filter(
                category=category,
                datetime__gt=now
            ).exclude(
                id__in=purchased_event_ids
            ).order_by('datetime')[:limit]

        # Get recommendations for top categories first
        for category in top_categories:
            category_recommendations = get_category_recommendations(category)
            for event in category_recommendations:
                recommendations.append({
                    'event': event,
                    'is_top_category': True,
                    'category_display': dict(Event.CATEGORY_CHOICES)[category]
                })

        # Then get recommendations for other categories
        for category in other_categories:
            category_recommendations = get_category_recommendations(category, limit=2)
            for event in category_recommendations:
                recommendations.append({
                    'event': event,
                    'is_top_category': False,
                    'category_display': dict(Event.CATEGORY_CHOICES)[category]
                })

    context = {
        'user': request.user,
        'active_tickets': active_tickets,
        'expired_tickets': expired_tickets,
        'recommendations': recommendations,
        'has_tickets': bool(active_tickets or expired_tickets),
        'joined_date': request.user.date_joined,
    }

    return render(request, 'registration/profile.html', context)
