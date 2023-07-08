from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from api_yamdb.settings import CHOICES, USER, ADMIN, MODERATOR


class Category(models.Model):
    """Модель для категорий."""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True,
                            verbose_name='Адрес типа slug')

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для жанров."""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True,
                            verbose_name='Адрес типа slug')

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений."""
    name = models.CharField(max_length=200, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    rating = models.IntegerField(null=True, default=None)
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
    )


class GenreTitle(models.Model):
    """
    Вспомогательная модель.
    Для реализаци связи М2М между моделями Title и Genre.
    """
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class User(AbstractUser):
    """Кастомная модель пользователя."""

    first_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=100
    )
    role = models.CharField(
        'Статус пользователя',
        max_length=25,
        choices=CHOICES,
        default=USER
    )
    bio = models.TextField(
        'Информация о пользователе',
        blank=True,
    )
    confirmation_code = models.CharField(max_length=150)

    @property
    def is_admin(self):
        return (self.role == ADMIN or self.is_staff
                or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        default=0,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        )
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отзыва'
    )

    class Meta:
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзывы'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Комментарий'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self) -> str:
        return self.text
