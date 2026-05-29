import os

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .utils import generate_avatar_image


NAMES_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя для TeamFinder."""

    # Обязательные поля
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("name"), max_length=NAMES_MAX_LENGTH)
    surname = models.CharField(_("surname"), max_length=NAMES_MAX_LENGTH)
    phone = models.CharField(_("phone"), max_length=PHONE_MAX_LENGTH)
    avatar = models.ImageField(_("avatar"), upload_to="avatars/", blank=True)

    # Дополнительные поля
    github_url = models.URLField(_("GitHub URL"), blank=True)
    about = models.TextField(_("about"), max_length=ABOUT_MAX_LENGTH, blank=True)

    # Статусы
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Дополнение к модели User (Вариант 1)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name=_("favorite projects"),
    )

    # Менеджер и настройки аутентификации
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        """Переопределяем save() для авто-генерации аватарки."""
        # Генерируем аватарку, если поле пустое и есть имя
        if not self.avatar and self.name:
            filename, content = generate_avatar_image(self.name, self.email)
            if filename and content:
                self.avatar.save(filename, content, save=False)
        super().save(*args, **kwargs)
