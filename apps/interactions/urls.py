from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Commentaires
    path('commentaires/poster/<int:lesson_id>/', views.post_comment, name='post_comment'),
    path('commentaires/supprimer/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('commentaires/like/<int:comment_id>/', views.toggle_like_comment, name='toggle_like'),

    # Notifications
    path('notifications/', views.NotificationsListView.as_view(), name='notifications_list'),
    path('notifications/dropdown/', views.notifications_dropdown, name='notifications_dropdown'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),
    path('notifications/lire/<int:notif_id>/', views.mark_notification_read, name='mark_read'),
    path('notifications/tout-lire/', views.mark_all_read, name='mark_all_read'),
]