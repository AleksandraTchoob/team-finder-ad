from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from .managers import UserManager

from PIL import Image, ImageDraw, ImageFont
import io
import random
import os


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя для TeamFinder."""

    # Обязательные поля
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("name"), max_length=124)
    surname = models.CharField(_("surname"), max_length=124)
    phone = models.CharField(_("phone"), max_length=12)
    avatar = models.ImageField(_("avatar"), upload_to="avatars/", blank=True)

    # Дополнительные поля
    github_url = models.URLField(_("GitHub URL"), blank=True)
    about = models.TextField(_("about"), max_length=256, blank=True)

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
            self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        """Генерирует аватарку с первой буквой имени пользователя на однотонном фоне."""
        colors = [
            (236, 64, 122),  # Pink
            (33, 150, 243),  # Blue
            (76, 175, 80),  # Green
            (255, 152, 0),  # Orange
            (156, 39, 176),  # Purple
            (0, 150, 136),  # Teal
            (109, 76, 65),  # Brown
            (96, 125, 139),  # Blue Grey
        ]
        bg_color = random.choice(colors)
        text_color = (255, 255, 255)

        image = Image.new("RGB", (200, 200), bg_color)
        draw = ImageDraw.Draw(image)

        first_letter = self.name[0].upper() if self.name else "U"
        try:
            # Пробуем найти системный шрифт
            font = ImageFont.truetype("arial.ttf", 100)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2 - bbox[0]
        y = (200 - text_height) // 2 - bbox[1]

        draw.text((x, y), first_letter, fill=text_color, font=font)

        # Сохраняем в буфер
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"avatar_{self.email.split('@')[0]}.png"
        self.avatar.save(filename, ContentFile(buffer.getvalue()), save=False)
