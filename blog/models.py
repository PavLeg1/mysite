from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'DRAFT'
        PUBLISHED = 'PB', 'PUBLISHED'

    title = models.CharField(max_length=250)
    # Поле заголовка (VARCHAR type SQL)

    slug = models.SlugField(max_length=250)
    # Слаг - метка только из букв, цифр, _ или - (VARCHAR type SQL)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    # Используем модель User модуля аутентификации, чтобы создавать
    # взаимосвязи между пользователями и постами

    # on_delete определяет поведение, применяемое при удалении объекта,
    # на который есть ссылка.

    # CASCADE указывает на то, что при удалении пользователя БД удалит
    # все его посты в блоге

    body = models.TextField()
    # Тело поста (Text type SQL)

    publish = models.DateTimeField(default=timezone.now)
    # Хранение даты и времени публикации поста (DATETIME type SQL)

    created = models.DateTimeField(auto_now_add=True)
    # Дата и время создания поста
    # При применении параметра auto_now_add дата будет сохраняться
    # автоматически во время создания объекта
    # (DATETIME type SQL)

    updated = models.DateTimeField(auto_now=True)
    # Хранение последней даты и времени обновления поста.
    # При применении параметра auto_now_add дата будет сохраняться
    # автоматически во время создания объекта
    # (DATETIME type SQL)

    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)

    objects = models.Manager()  # Менеджер по-умолчанию
    published = PublishedManager()  # Конкретно-прикладной менеджер

    class Meta:
        ordering = ['-publish']  # Отображение постов в порядке (сначала новые)
        # Добавление индекса по полю publish
        # MySQL не поддерживает индексное упорядочивание
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])