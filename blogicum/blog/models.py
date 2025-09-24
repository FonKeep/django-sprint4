from django.contrib.auth import get_user_model
from django.db import models

from .const import MAX_LENGTH


User = get_user_model()


class BlogModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')

    class Meta:
        abstract = True


class Category(BlogModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return f'{self.title[:10]}'


class Location(BlogModel):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name[:10]}'


class Post(BlogModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True, upload_to='images/')
    comment_count = models.PositiveIntegerField(
        verbose_name='Счетчик комментариев',
        default=0)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.title[:10]}'


class Comments(models.Model):
    text = models.TextField(verbose_name='Текст коментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='К публикации'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.text[:10]}'
