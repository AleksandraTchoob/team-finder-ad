import io
import random
import re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont


AVATAR_SIZE = (200, 200)
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_COLOR = (255, 255, 255)

COLOR_PINK = (236, 64, 122)
COLOR_BLUE = (33, 150, 243)
COLOR_GREEN = (76, 175, 80)
COLOR_ORANGE = (255, 152, 0)
COLOR_PURPLE = (156, 39, 176)
COLOR_TEAL = (0, 150, 136)
COLOR_BROWN = (109, 76, 65)
COLOR_BLUE_GREY = (96, 125, 139)
AVATAR_COLORS = [
    COLOR_PINK, COLOR_BLUE, COLOR_GREEN, COLOR_ORANGE,
    COLOR_PURPLE, COLOR_TEAL, COLOR_BROWN, COLOR_BLUE_GREY
]


def validate_phone(phone: str, exclude_pk=None) -> str:
    if not phone:
        return phone
        
    phone = phone.replace(" ", "").replace("-", "")
    # Должен сохраняться только номер телефона в одном из двух форматов: либо 8XXXXXXXXXX, либо +7XXXXXXXXXX.
    if not re.match(r"^(8\d{10}|\+7\d{10})$", phone):
        raise ValidationError(
            "Введите корректный номер телефона: 8XXXXXXXXXX или +7XXXXXXXXXX!"
        )
    if phone.startswith("8"):
        phone = "+7" + phone[1:]

    from .models import User
    # Номера телефона должны быть уникальны
    qs = User.objects.filter(phone=phone)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    
    if qs.exists():
        raise ValidationError("Этот номер телефона уже используется!")
    
    return phone


def validate_github_url(url: str) -> str:
    if url and "github.com" not in url:
        raise ValidationError("Ссылка должна вести на GitHub!")
    return url


def generate_avatar_image(name: str, email: str) -> tuple[str, ContentFile]:
        """Генерирует аватарку с первой буквой имени пользователя на однотонном фоне."""
        if not name:
            return None, None

        bg_color = random.choice(AVATAR_COLORS)
        text_color = AVATAR_TEXT_COLOR

        image = Image.new("RGB", AVATAR_SIZE, bg_color)
        draw = ImageDraw.Draw(image)

        first_letter = name[0].upper()
        try:
            # Пробуем найти системный шрифт
            font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (AVATAR_SIZE[0] - text_width) // 2 - bbox[0]
        y = (AVATAR_SIZE[1] - text_height) // 2 - bbox[1]

        draw.text((x, y), first_letter, fill=text_color, font=font)

        # Сохраняем в буфер
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"avatar_{email.split('@')[0]}.png"

        return filename, ContentFile(buffer.getvalue())


def get_paginated_queryset(queryset, request, items_per_page=12):
    """Универсальная функция для пагинации."""
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
