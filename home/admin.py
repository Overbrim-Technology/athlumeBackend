from django.contrib import admin
from .models import Highlight, FeaturedAthlete


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'published', 'image')
    list_filter = ('published',)
    search_fields = ('title', 'body')


@admin.register(FeaturedAthlete)
class FeaturedAthleteAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'order', 'active', 'added_by', 'added_at')
    list_editable = ('order', 'active')
    search_fields = ('athlete__first_name', 'athlete__last_name', 'athlete__email')
    autocomplete_fields = ('athlete',)
    exclude = ('added_by',)

    def save_model(self, request, obj, form, change):
        # Automatically set the admin who added this featured athlete
        if not obj.added_by:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)