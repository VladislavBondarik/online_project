from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_courses',
                                   verbose_name="Инструктор")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        permissions = [("manage_all_courses", "Управление всеми курсами")]

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE, verbose_name="Курс")

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"

    def __str__(self):
        return self.title


class Material(models.Model):
    TYPE_CHOICES = [
        ('video', 'Видео'),
        ('text', 'Текст'),
        ('pdf', 'PDF'),
    ]
    title = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Тип")
    content = models.TextField(blank=True, null=True, verbose_name="Содержимое")
    file = models.FileField(upload_to='materials/', blank=True, null=True, verbose_name="Файл")
    module = models.ForeignKey(Module, related_name='materials', on_delete=models.CASCADE, verbose_name="Модуль")

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('completed', 'Завершён'),
        ('canceled', 'Отменён'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Пользователь")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Курс")
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата записи")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        permissions = [("enroll_in_course", "Запись на курс")]

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress', verbose_name="Пользователь")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress', verbose_name="Курс")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress', verbose_name="Модуль")
    progress = models.IntegerField(default=0, verbose_name="Прогресс")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        unique_together = ('user', 'course', 'module')
        verbose_name = "Прогресс пользователя"
        verbose_name_plural = "Прогресс пользователей"

    def __str__(self):
        return f'{self.user.username} progress in {self.module.title}: {self.progress}%'


class FavoriteCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_courses',
                             verbose_name="Пользователь")
    course_name = models.CharField(max_length=255, verbose_name="Название курса")
    progress = models.IntegerField(default=0, verbose_name="Прогресс")

    class Meta:
        verbose_name = "Избранный курс"
        verbose_name_plural = "Избранные курсы"
        unique_together = ('user', 'course_name')

    def __str__(self):
        return f'{self.user.username} - {self.course_name}'


class Survey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys', verbose_name="Пользователь")
    answers = models.JSONField(verbose_name="Ответы")  # Храним ответы в JSON
    recommended_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True,
                                           verbose_name="Рекомендуемый курс")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"

    def __str__(self):
        return f'{self.user.username} - Survey {self.created_at}'
