from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

PROJECT_STATUS_CHOICES = [
    ("open", "Открыт"),
    ("closed", "Закрыт"),
]

PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6


class Project(models.Model):
    """Модель проекта для TeamFinder."""

    # Основная информация
    name = models.CharField(_("name"), max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(_("description"), blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name=_("owner"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    # Дополнительные поля
    github_url = models.URLField(_("GitHub URL"), blank=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name=_("participants"),
    )

    # Статусы
    status = models.CharField(
        _("status"),
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default="open",
    )

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Возвращает URL для страницы проекта."""
        from django.urls import reverse

        return reverse("project_detail", kwargs={"pk": self.pk})
