from django.contrib import admin
from .models import Comment, Notification


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'lesson', 'content_short', 'is_instructor_reply', 'is_pinned', 'created_at')
    list_filter = ('is_instructor_reply', 'is_pinned', 'created_at')
    search_fields = ('content', 'author__email', 'lesson__title')
    readonly_fields = ('created_at', 'updated_at', 'is_instructor_reply')

    def content_short(self, obj):
        return obj.content[:60] + ('...' if len(obj.content) > 60 else '')
    content_short.short_description = 'Contenu'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'title')
    readonly_fields = ('created_at', 'read_at')