from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("manage_all_courses", "Управление всеми курсами"),  # Администратор может управлять всеми курсами
            ("manage_all_users", "Управление всеми пользователями"),  # Администратор может управлять всеми пользователями
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Material(models.Model):
    TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('pdf', 'PDF'),
    ]
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.TextField()  # Можно использовать FileField для файлов, например PDF
    module = models.ForeignKey(Module, related_name='materials', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        permissions = [
            ("enroll_in_course", "Запись на курс"),  # Пользователь может записываться на курсы
            ("manage_own_profile", "Управление своим профилем"),  # Пользователь может управлять только своим профилем
        ]

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    progress = models.IntegerField()  # Процент завершения
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} progress in {self.module.title}: {self.progress}%'
