from django.contrib import admin
from .models import Video, Comment, Rating

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'genre', 'age_rating', 'views', 'upload_date')
    list_filter = ('genre', 'age_rating', 'upload_date')
    search_fields = ('title', 'description', 'creator__username')
    readonly_fields = ('views', 'upload_date')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'creator')
        }),
        ('Media', {
            'fields': ('video_file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('publisher', 'producer', 'genre', 'age_rating')
        }),
        ('Statistics', {
            'fields': ('views', 'upload_date'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'user', 'video', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'video__title')
    
    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Comment'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('video__title', 'user__username')