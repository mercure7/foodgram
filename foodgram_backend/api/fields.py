"""Кастом поля для сериализаторов."""
import base64

from rest_framework import serializers
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    """Класс для кастомного поля image сериализатора Recipes."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)
