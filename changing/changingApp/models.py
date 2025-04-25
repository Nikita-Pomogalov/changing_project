from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

# Create your models here.
class Announcement(models.Model):

    CONDITIONS = {
        ('new', 'Новый'),
        ('used', 'Б/У'),
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание товара')
    image = models.ImageField(
        upload_to='announcements/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    category = models.CharField(max_length=100, verbose_name='Категория товара')
    condition = models.CharField(max_length=10, choices=CONDITIONS, verbose_name='Состояние товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')


