from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Настройка отображения модели Project в админке."""

    list_display = ["name", "owner", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]
    filter_horizontal = ["participants"]
