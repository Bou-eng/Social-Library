from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify_view, name='password_reset_verify'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('library/create-list/', views.create_custom_list, name='create_custom_list'),
    path('library/delete-item/', views.delete_library_item, name='delete_library_item'),
    path('library/delete-custom-item/', views.delete_custom_list_item, name='delete_custom_list_item'),
    path('library/delete-list/', views.delete_custom_list, name='delete_custom_list'),
    path('library/list-items/', views.get_custom_list_items, name='get_custom_list_items'),
    path('follow/', views.follow_user, name='follow_user'),
    path('unfollow/', views.unfollow_user, name='unfollow_user'),
]
