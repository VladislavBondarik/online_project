# initialize_project.py
import os
import sys
import django
from django.core.management import call_command

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
print(f"BASE_DIR: {BASE_DIR}")
print(f"sys.path: {sys.path}")

os.environ['DJANGO_SETTINGS_MODULE'] = 'online_project.settings'
print(f"DJANGO_SETTINGS_MODULE: {os.environ['DJANGO_SETTINGS_MODULE']}")

try:
    django.setup()
except Exception as e:
    print(f"Ошибка при загрузке Django: {e}")
    sys.exit(1)

from django.utils import timezone
from django.contrib.auth.models import User
from courses.models import Course, Module, Material, Enrollment, UserProgress


def create_initial_data():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(username='admin', email='admin@example.com', password='12345')
        print("Создан суперпользователь: admin")

    user = User.objects.get(username='admin')

    courses_data = [
        {
            'title': 'Основы программирования на Python',
            'description': 'Изучение Python с нуля',
            'modules': [
                ('Введение в Python', 'Основы синтаксиса', [
                    ('Что такое Python', 'text', 'Python - это мощный язык...'),
                    ('Установка Python', 'video', 'Видео об установке'),
                ]),
            ]
        },
        {
            'title': 'Веб-разработка (HTML, CSS, JS)',
            'description': 'Основы фронтенда',
            'modules': [
                ('HTML Basics', 'Введение в HTML', [
                    ('Структура HTML', 'text', 'HTML состоит из тегов...'),
                ]),
            ]
        },
    ]

    for course_data in courses_data:
        if not Course.objects.filter(title=course_data['title']).exists():
            course = Course.objects.create(
                title=course_data['title'],
                description=course_data['description'],
                start_date=timezone.now(),
                end_date=timezone.now(),
                instructor=user
            )
            for module_title, module_desc, materials in course_data['modules']:
                module = Module.objects.create(
                    title=module_title,
                    description=module_desc,
                    course=course
                )
                for material_title, material_type, content in materials:
                    Material.objects.create(
                        title=material_title,
                        type=material_type,
                        content=content,
                        module=module
                    )
            Enrollment.objects.create(user=user, course=course)
            UserProgress.objects.create(user=user, course=course, module=course.modules.first(), progress=50)

    print("Курсы:", Course.objects.all())
    print("Записи:", Enrollment.objects.all())
    print("Прогресс:", UserProgress.objects.all())


if __name__ == "__main__":
    print("Создание миграций...")
    call_command('makemigrations')
    print("Применение миграций...")
    call_command('migrate')
    print("Добавление данных...")
    create_initial_data()
    print("Готово!")