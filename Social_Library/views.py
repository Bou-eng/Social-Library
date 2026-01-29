from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.decorators.http import require_POST
from accounts.models import Activity, Follow, Like, ActivityComment, Notification
import json


def _human_time(dt):
    # human readable like '3 hours ago'
    if not dt:
        return ''
    delta = timezone.now() - dt
    # timesince returns e.g. '3 hours, 2 minutes'
    s = timesince(dt, timezone.now())
    # simplify to first unit
    s = s.split(',')[0]
    return f"{s} ago"


def root_redirect(request):
    """Redirect root URL to login or home depending on auth state."""
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')


@login_required
def home(request):
    # get users current user follows
    user = request.user
    following_qs = Follow.objects.filter(follower=user).values_list('following', flat=True)

    activities = Activity.objects.filter(user__in=following_qs).select_related('user', 'user__profile').order_by('-created_at')
    page_size = 12
    paginator = Paginator(activities, page_size)
    page_obj = paginator.get_page(1)

    # Load notifications for the user - count unread BEFORE slicing
    notifications_qs = Notification.objects.filter(user=user).select_related('actor', 'actor__profile', 'activity').order_by('-created_at')
    unread_count = notifications_qs.filter(is_seen=False).count()
    notifications = notifications_qs[:20]
    
    # Get list of user IDs that current user follows for notification follow button state
    following_ids = list(following_qs)

    # prepare initial activities list for template (we render server-side cards too)
    initial_activities = []
    for a in page_obj.object_list:
        likes_count = a.likes.count()
        user_liked = a.likes.filter(user=user).exists()
        comments_count = a.comments.count()
        
        # Get avatar and display name using same logic as suggested users
        profile = getattr(a.user, 'profile', None)
        avatar_url = profile.avatar.url if profile and profile.avatar else '/static/accounts/avatar-placeholder.png'
        display_name = profile.display_name if profile and profile.display_name else a.user.username
        
        initial_activities.append({
            'id': a.id,
            'username': a.user.username,
            'display_name': display_name,
            'avatar': avatar_url,
            'content_type': a.content_type,
            'content_id': a.content_id,
            'type': a.type,
            'rating': a.rating,
            'review_excerpt': a.excerpt(180),
            'created_at': a.created_at.isoformat(),
            'human_time': _human_time(a.created_at),
            'title': a.title,
            'cover_url': a.cover_url,
            'year': a.year,
            'overview': a.overview[:200] if a.overview else '',
            'likes_count': likes_count,
            'user_liked': user_liked,
            'comments_count': comments_count,
        })

    # Find the most active user (excluding current user)
    from django.db.models import Count
    from django.contrib.auth.models import User
    most_active_user = (
        User.objects
        .annotate(activity_count=Count('activities'))
        .exclude(id=user.id)
        .order_by('-activity_count')
        .first()
    )

    # Prepare avatar and display name logic
    suggested_user = None
    if most_active_user:
        profile = getattr(most_active_user, 'profile', None)
        avatar_url = profile.avatar.url if profile and profile.avatar else '/static/accounts/avatar-placeholder.png'
        display_name = profile.display_name if profile and profile.display_name else most_active_user.username
        is_following = Follow.objects.filter(follower=user, following=most_active_user).exists()
        suggested_user = {
            'id': most_active_user.id,
            'avatar_url_or_default': avatar_url,
            'display_name': display_name,
            'is_following': is_following,
        }

    # Add following_ids to user context for template
    user.following_ids = following_ids
    
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
    page = int(request.GET.get('page', '1'))
    following_qs = Follow.objects.filter(follower=user).values_list('following', flat=True)
    activities = Activity.objects.filter(user__in=following_qs).select_related('user', 'user__profile').order_by('-created_at')
    page_size = 12
    paginator = Paginator(activities, page_size)
    if page > paginator.num_pages:
        return JsonResponse({'activities': []})

    page_obj = paginator.get_page(page)
    data = []
    for a in page_obj.object_list:
        likes_count = a.likes.count()
        user_liked = a.likes.filter(user=user).exists()
        comments_count = a.comments.count()
        
        # Get avatar and display name using same logic as suggested users
        profile = getattr(a.user, 'profile', None)
        avatar_url = profile.avatar.url if profile and profile.avatar else '/static/accounts/avatar-placeholder.png'
        display_name = profile.display_name if profile and profile.display_name else a.user.username
        
        data.append({
            'id': a.id,
            'username': a.user.username,
            'display_name': display_name,
            'avatar': avatar_url,
            'content_type': a.content_type,
            'content_id': a.content_id,
            'type': a.type,
            'rating': a.rating,
            'review_excerpt': a.excerpt(180),
            'created_at': a.created_at.isoformat(),
            'human_time': _human_time(a.created_at),
            'title': a.title,
            'cover_url': a.cover_url,
            'year': a.year,
            'overview': a.overview[:200] if a.overview else '',
            'likes_count': likes_count,
            'user_liked': user_liked,
            'comments_count': comments_count,
        })

    return JsonResponse({'activities': data})


@login_required
@require_POST
def toggle_like(request):
    """Toggle like on an activity."""
    data = json.loads(request.body)
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
    data = json.loads(request.body)
    activity_id = data.get('activity_id')
    comment_text = data.get('comment', '').strip()
    
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
    
    profile = getattr(request.user, 'profile', None)
    avatar_url = profile.avatar.url if profile and profile.avatar else '/static/accounts/avatar-placeholder.png'
    display_name = profile.display_name if profile and profile.display_name else request.user.username
    
    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'user': display_name,
            'user_id': request.user.id,
            'avatar': avatar_url,
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
        profile = getattr(c.user, 'profile', None)
        avatar_url = profile.avatar.url if profile and profile.avatar else '/static/accounts/avatar-placeholder.png'
        display_name = profile.display_name if profile and profile.display_name else c.user.username
        
        comments_data.append({
            'id': c.id,
            'user': display_name,
            'user_id': c.user.id,
            'avatar': avatar_url,
            'comment': c.comment,
            'created_at': c.created_at.isoformat(),
            'human_time': _human_time(c.created_at),
        })
    
    return JsonResponse({'success': True, 'comments': comments_data})


@login_required
@require_POST
def delete_activity_comment(request):
    """Delete a comment (only by the author)."""
    data = json.loads(request.body)
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
