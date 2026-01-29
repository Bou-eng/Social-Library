from django.urls import path
from . import views

app_name = 'explore'

urlpatterns = [
    path('', views.explore_view, name='explore'),
    path('search/', views.explore_search, name='explore_search'),
    path('item-details/', views.get_item_details, name='item_details'),
    path('save-item-preferences/', views.save_item_preferences, name='save_item_preferences'),
    path('save-comment/', views.save_comment, name='save_comment'),
]
