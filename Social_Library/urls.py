
from django.contrib import admin
from django.urls import path, include
from Social_Library import views
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.root_redirect, name='root'),
    # root redirect handled elsewhere; keep home at /home/
    path('home/', views.home, name='home'),
    path('home/load-more/', views.load_more, name='home_load_more'),
    path('activities/toggle-like/', views.toggle_like, name='toggle_like'),
    path('activities/add-comment/', views.add_activity_comment, name='add_activity_comment'),
    path('activities/<int:activity_id>/comments/', views.get_activity_comments, name='get_activity_comments'),
    path('activities/delete-comment/', views.delete_activity_comment, name='delete_activity_comment'),
    path('notifications/mark-seen/', views.mark_notifications_seen, name='mark_notifications_seen'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('explore/', include('explore.urls')),
    path('library/', accounts_views.library_view, name='library'),
    # Public profile URLs (no prefix) per requirement
    path('user/<str:username>/', accounts_views.public_profile_view, name='public_profile'),
    path('user/<str:username>/edit/', accounts_views.edit_profile_view, name='edit_profile'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
