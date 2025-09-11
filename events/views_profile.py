# events/views_profile.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from collections import Counter
from events.models import Event
from orders.models import Order

@login_required
def profile(request):
    now = timezone.now()

    # User’s placed orders with items + event prefetched
    user_orders = (
        Order.objects
        .filter(user=request.user, status='placed')
        .prefetch_related('items__event')
    )

    active_tickets = []
    expired_tickets = []

    category_counts = Counter()
    purchased_event_ids = set()

    for order in user_orders:
        for item in order.items.all():
            e = item.event
            # (history table is hidden in template now, but we keep the data)
            ticket_info = {
                'event_name': e.name,
                'event_date': e.datetime,
                'order_date': order.created_at,
                'quantity': item.qty,
                'status': 'Active' if e.datetime > now else 'Past',
            }
            if e.datetime > now:
                active_tickets.append(ticket_info)
            else:
                expired_tickets.append(ticket_info)

            category_counts[e.category] += item.qty
            purchased_event_ids.add(e.id)

    active_tickets.sort(key=lambda x: x['event_date'])
    expired_tickets.sort(key=lambda x: x['event_date'], reverse=True)

    recommendations = []
    if category_counts:
        max_count = max(category_counts.values())

        # categories with highest count (tie-friendly)
        top_categories = [c for c, cnt in category_counts.items() if cnt == max_count]
        # remaining categories, sorted by count desc
        other_categories = [c for c, _ in category_counts.most_common() if c not in top_categories]

        def get_category_recommendations(category, limit=4):
            return (
                Event.objects
                .select_related('location')
                .filter(category=category, datetime__gt=now)
                .exclude(id__in=purchased_event_ids)
                .order_by('datetime')[:limit]
            )

        # Top categories first
        for category in top_categories:
            for e in get_category_recommendations(category, limit=4):
                recommendations.append({
                    'event': e,
                    'is_top_category': True,
                    'category_display': dict(Event.CATEGORY_CHOICES)[category],
                })

        # Then other categories
        for category in other_categories:
            for e in get_category_recommendations(category, limit=2):
                recommendations.append({
                    'event': e,
                    'is_top_category': False,
                    'category_display': dict(Event.CATEGORY_CHOICES)[category],
                })

    context = {
        'user': request.user,
        'has_tickets': bool(active_tickets or expired_tickets),
        'recommendations': recommendations,
        'joined_date': request.user.date_joined,
    }
    return render(request, 'registration/profile.html', context)
