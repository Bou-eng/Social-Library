from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.decorators.http import require_POST
from accounts.models import Activity, Follow, Like, ActivityComment, Notification
from django.contrib.auth.models import User
from django.db.models import Count
import json


def _json_payload(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except (TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _human_time(dt):
    if not dt:
        return ''
    s = timesince(dt, timezone.now())
    s = s.split(',')[0]
    return f"{s} ago"


def _avatar_url(user):
    profile = getattr(user, 'profile', None)
    return profile.avatar.url if profile and profile.avatar else '/static/accounts/avatar-placeholder.svg'


def _display_name(user):
    profile = getattr(user, 'profile', None)
    if profile and profile.display_name:
        return profile.display_name
    return user.first_name or user.username


def _activity_payload(activity, viewer):
    return {
        'id': activity.id,
        'username': activity.user.username,
        'display_name': _display_name(activity.user),
        'avatar': _avatar_url(activity.user),
        'content_type': activity.content_type,
        'content_id': activity.content_id,
        'type': activity.type,
        'rating': activity.rating,
        'review_excerpt': activity.excerpt(180),
        'created_at': activity.created_at.isoformat(),
        'human_time': _human_time(activity.created_at),
        'title': activity.title,
        'cover_url': activity.cover_url,
        'year': activity.year,
        'overview': activity.overview[:200] if activity.overview else '',
        'likes_count': activity.likes.count(),
        'user_liked': activity.likes.filter(user=viewer).exists(),
        'comments_count': activity.comments.count(),
    }


def root_redirect(request):
    """Redirect root URL to login or home depending on auth state."""
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')


@login_required
def home(request):
    user = request.user
    following_qs = Follow.objects.filter(follower=user).values_list('following', flat=True)
    following_ids = list(following_qs)

    activities = Activity.objects.filter(user__in=following_ids).select_related('user', 'user__profile').order_by('-created_at')
    page_size = 12
    paginator = Paginator(activities, page_size)
    page_obj = paginator.get_page(1)

    # Load notifications for the user - count unread BEFORE slicing
    notifications_qs = Notification.objects.filter(user=user).select_related('actor', 'actor__profile', 'activity').order_by('-created_at')
    unread_count = notifications_qs.filter(is_seen=False).count()
    notifications = notifications_qs[:20]

    initial_activities = [_activity_payload(a, user) for a in page_obj.object_list]

    most_active_user = (
        User.objects
        .annotate(activity_count=Count('activities'))
        .exclude(id=user.id)
        .exclude(id__in=following_ids)
        .filter(activity_count__gt=0)
        .order_by('-activity_count')
        .first()
    )

    suggested_user = None
    if most_active_user:
        suggested_user = {
            'id': most_active_user.id,
            'avatar_url_or_default': _avatar_url(most_active_user),
            'display_name': _display_name(most_active_user),
            'is_following': False,
        }

    return render(request, 'home.html', {
        'activities': initial_activities,
        'page_count': paginator.num_pages,
        'suggested_user': suggested_user,
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def load_more(request):
    # AJAX endpoint: /home/load-more/?page=2
    user = request.user
    try:
        page = int(request.GET.get('page', '1'))
    except (TypeError, ValueError):
        page = 1
    page = max(page, 1)
    following_qs = Follow.objects.filter(follower=user).values_list('following', flat=True)
    activities = Activity.objects.filter(user__in=following_qs).select_related('user', 'user__profile').order_by('-created_at')
    page_size = 12
    paginator = Paginator(activities, page_size)
    if page > paginator.num_pages:
        return JsonResponse({'activities': []})

    page_obj = paginator.get_page(page)
    data = [_activity_payload(a, user) for a in page_obj.object_list]

    return JsonResponse({'activities': data})


@login_required
@require_POST
def toggle_like(request):
    """Toggle like on an activity."""
    data = _json_payload(request)
    activity_id = data.get('activity_id')

    if not activity_id:
        return JsonResponse({'success': False, 'error': 'Missing activity_id'})

    activity = get_object_or_404(Activity, id=activity_id)
    like_obj = Like.objects.filter(user=request.user, activity=activity).first()

    if like_obj:
        # Unlike
        like_obj.delete()
        liked = False
    else:
        # Like
        Like.objects.create(user=request.user, activity=activity)
        liked = True
        # Create notification if liking someone else's activity
        if activity.user != request.user:
            Notification.objects.create(
                user=activity.user,
                actor=request.user,
                notif_type='like',
                activity=activity
            )

    likes_count = activity.likes.count()
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': likes_count
    })


@login_required
@require_POST
def add_activity_comment(request):
    """Add a comment to an activity."""
    data = _json_payload(request)
    activity_id = data.get('activity_id')
    comment_text = str(data.get('comment') or '').strip()

    if not activity_id or not comment_text:
        return JsonResponse({'success': False, 'error': 'Missing data'})

    activity = get_object_or_404(Activity, id=activity_id)
    comment = ActivityComment.objects.create(
        activity=activity,
        user=request.user,
        comment=comment_text
    )

    # Create notification if commenting on someone else's activity
    if activity.user != request.user:
        Notification.objects.create(
            user=activity.user,
            actor=request.user,
            notif_type='comment',
            activity=activity,
            comment_text=comment_text
        )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'user': _display_name(request.user),
            'user_id': request.user.id,
            'avatar': _avatar_url(request.user),
            'comment': comment.comment,
            'created_at': comment.created_at.isoformat(),
            'human_time': _human_time(comment.created_at),
        }
    })


@login_required
def get_activity_comments(request, activity_id):
    """Get all comments for an activity."""
    activity = get_object_or_404(Activity, id=activity_id)
    comments = activity.comments.all()

    comments_data = []
    for c in comments:
        comments_data.append({
            'id': c.id,
            'user': _display_name(c.user),
            'user_id': c.user.id,
            'avatar': _avatar_url(c.user),
            'comment': c.comment,
            'created_at': c.created_at.isoformat(),
            'human_time': _human_time(c.created_at),
        })

    return JsonResponse({'success': True, 'comments': comments_data})


@login_required
@require_POST
def delete_activity_comment(request):
    """Delete a comment (only by the author)."""
    data = _json_payload(request)
    comment_id = data.get('comment_id')

    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Missing comment_id'})

    comment = get_object_or_404(ActivityComment, id=comment_id)

    # Only allow the author to delete
    if comment.user != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized'})

    comment.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_notifications_seen(request):
    """Mark all notifications as seen for the current user."""
    Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)
    return JsonResponse({'success': True})
