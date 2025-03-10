from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Course, Module, Material, Enrollment, UserProgress, FavoriteCourse, Survey
from .serializers import (
    UserSerializer, CourseSerializer, ModuleSerializer, MaterialSerializer,
    EnrollmentSerializer, UserProgressSerializer, FavoriteCourseSerializer, SurveySerializer
)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import locale
from django.contrib.admin.views.decorators import staff_member_required

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


@login_required
def module_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут управлять модулями.')
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, id=course_id)
        Module.objects.create(title=title, description=description, course=course)
        messages.success(request, 'Модуль успешно создан!')
        return redirect('module_list')

    courses = Course.objects.all()
    return render(request, 'module_create.html', {'courses': courses})


@login_required
def module_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут просматривать модули.')
        return redirect('home')

    modules = Module.objects.all()
    return render(request, 'module_list.html', {'modules': modules})


@login_required
def module_edit(request, module_id):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут редактировать модули.')
        return redirect('home')

    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        module.title = request.POST.get('title')
        module.description = request.POST.get('description')
        course_id = request.POST.get('course')
        module.course = get_object_or_404(Course, id=course_id)
        module.save()
        messages.success(request, 'Модуль успешно обновлён!')
        return redirect('module_list')

    courses = Course.objects.all()
    return render(request, 'module_edit.html', {'module': module, 'courses': courses})


@login_required
def module_delete(request, module_id):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут удалять модули.')
        return redirect('home')

    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Модуль успешно удалён!')
        return redirect('module_list')
    return render(request, 'module_delete.html', {'module': module})


@login_required
def material_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут управлять материалами.')
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        type = request.POST.get('type')
        content = request.FILES.get('content') or request.POST.get('content_url')
        module_id = request.POST.get('module')
        module = get_object_or_404(Module, id=module_id)
        material = Material(title=title, type=type, module=module)
        if request.FILES.get('content'):
            material.content = content
        else:
            material.content_url = content
        material.save()
        messages.success(request, 'Материал успешно создан!')
        return redirect('material_list')

    modules = Module.objects.all()
    return render(request, 'material_create.html', {'modules': modules})


@login_required
def material_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут просматривать материалы.')
        return redirect('home')

    materials = Material.objects.all()
    return render(request, 'material_list.html', {'materials': materials})


@login_required
def material_edit(request, material_id):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут редактировать материалы.')
        return redirect('home')

    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.title = request.POST.get('title')
        material.type = request.POST.get('type')
        content = request.FILES.get('content') or request.POST.get('content_url')
        if content:
            if request.FILES.get('content'):
                material.content = content
            else:
                material.content_url = content
        module_id = request.POST.get('module')
        material.module = get_object_or_404(Module, id=module_id)
        material.save()
        messages.success(request, 'Материал успешно обновлён!')
        return redirect('material_list')

    modules = Module.objects.all()
    return render(request, 'material_edit.html', {'material': material, 'modules': modules})


@login_required
def material_delete(request, material_id):
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут удалять материалы.')
        return redirect('home')

    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Материал успешно удалён!')
        return redirect('material_list')
    return render(request, 'material_delete.html', {'material': material})


@staff_member_required
def admin_stats(request):
    """Страница статистики для администраторов."""
    stats = {
        'course_count': Course.objects.count(),
        'module_count': Module.objects.count(),
        'material_count': Material.objects.count(),
        'user_count': User.objects.count(),
    }
    return render(request, 'admin_stats.html', {'stats': stats})


def join(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно! Войдите в систему.')
            return redirect('api_login')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.')
    else:
        form = UserCreationForm()
    return render(request, 'join.html', {'form': form})


def api_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            messages.success(request, 'Вы успешно вошли!')
            return redirect('api_courses')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'api_login.html')


def api_logout(request):
    logout(request)
    return redirect('home')


@login_required
def api_profile(request):
    return render(request, 'api_profile.html', {'user': request.user})


# Общие страницы
def about(request):
    return render(request, 'about.html')


def api_overview(request):
    return render(request, 'api_overview.html')


@login_required
def settings(request):
    if request.user.is_staff or request.user.is_superuser:
        return render(request, 'settings.html')
    return redirect('home')


# Курсы и избранное
def api_courses(request):
    all_courses = [
        {'name': 'Backend', 'icon': '2920/2920346.png', 'date': '15 апреля 2025'},
        {'name': 'Frontend', 'icon': '1055/1055681.png', 'date': '20 апреля 2025'},
        {'name': 'Data Science', 'icon': '2920/2920352.png', 'date': '25 апреля 2025'},
        {'name': 'DevOps', 'icon': '1055/1055680.png', 'date': '30 апреля 2025'},
        {'name': 'AI/ML', 'icon': '2920/2920348.png', 'date': '5 мая 2025'},
        {'name': 'Cybersecurity', 'icon': '5968/5968852.png', 'date': '10 мая 2025'},
        {'name': 'Mobile Development', 'icon': '5968/5968896.png', 'date': '15 мая 2025'},
        {'name': 'Cloud Computing', 'icon': 'question.png', 'date': '20 мая 2025'},
        {'name': 'Game Development', 'icon': '5968/5968880.png', 'date': '25 мая 2025'},
        {'name': 'UI/UX Design', 'icon': '5968/5968908.png', 'date': '30 мая 2025'},
        {'name': 'Blockchain', 'icon': '5968/5968864.png', 'date': '5 июня 2025'},
        {'name': 'Python Basics', 'icon': '5968/5968876.png', 'date': '10 июня 2025'},
        {'name': 'Java Programming', 'icon': '5968/5968844.png', 'date': '15 июня 2025'},
        {'name': 'Web Development', 'icon': '5968/5968912.png', 'date': '20 июня 2025'},
        {'name': 'Database Design', 'icon': '5968/5968820.png', 'date': '25 июня 2025'},
    ]
    if request.user.is_authenticated:
        favorite_courses = FavoriteCourse.objects.filter(user=request.user)
        courses = []
        for course in all_courses:
            fav = favorite_courses.filter(course_name=course['name']).first()
            courses.append({
                'name': course['name'],
                'icon': course['icon'],
                'date': course['date'],
                'progress': fav.progress if fav else 0,
                'is_favorite': fav is not None
            })
    else:
        courses = [{'name': c['name'], 'icon': c['icon'], 'date': c['date'], 'progress': 0, 'is_favorite': False} for c
                   in all_courses]
    return render(request, 'api_courses.html', {'courses': courses})


def home(request):
    return render(request, 'home.html')


@login_required
def favorites(request):
    favorite_courses = FavoriteCourse.objects.filter(user=request.user)
    if not favorite_courses.exists():
        return render(request, 'favorites.html', {'message': 'У вас нет добавленных курсов'})
    courses = []
    all_courses = {
        'Backend': '2920/2920346.png',
        'Frontend': '1055/1055681.png',
        'Data Science': '2920/2920352.png',
        'DevOps': '1055/1055680.png',
        'AI/ML': '2920/2920348.png',
        'Cybersecurity': '5968/5968852.png',
        'Mobile Development': '5968/5968896.png',
        'Cloud Computing': 'question.png',
        'Game Development': '5968/5968880.png',
        'UI/UX Design': '5968/5968908.png',
        'Blockchain': '5968/5968864.png',
        'Python Basics': '5968/5968876.png',
        'Java Programming': '5968/5968844.png',
        'Web Development': '5968/5968912.png',
        'Database Design': '5968/5968820.png',
    }
    for fav in favorite_courses:
        try:
            course = Course.objects.get(title=fav.course_name)
            courses.append({
                'name': fav.course_name,
                'icon': all_courses.get(fav.course_name, 'question.png'),
                'date': course.start_date.strftime('%d %B %Y'),
                'progress': fav.progress,
            })
        except Course.DoesNotExist:
            courses.append({
                'name': fav.course_name,
                'icon': all_courses.get(fav.course_name, 'question.png'),
                'date': timezone.now().strftime('%d %B %Y'),
                'progress': fav.progress,
            })
    return render(request, 'favorites.html', {'favorite_courses': courses})


@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        action = request.POST.get('action')
        if not course_name:
            return JsonResponse({'status': 'error', 'message': 'Course name is required'}, status=400)
        if action == 'remove':
            FavoriteCourse.objects.filter(user=request.user, course_name=course_name).delete()
            return JsonResponse({'status': 'removed'})
        elif action == 'add':
            FavoriteCourse.objects.get_or_create(user=request.user, course_name=course_name, defaults={'progress': 0})
            return JsonResponse({'status': 'added'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@login_required
def course_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if request.user.is_staff:
            from django.utils import timezone
            import datetime
            start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S'))
            end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S'))
            course = Course.objects.create(
                title=title,
                description=description,
                instructor=request.user,
                start_date=start_date,
                end_date=end_date
            )
            messages.success(request, 'Курс успешно создан!')
            return redirect('api_courses')
        else:
            messages.error(request, 'Только администраторы могут создавать курсы.')
    try:
        courses = Course.objects.all()
    except:
        courses = []
    return render(request, 'course_create.html', {'courses': courses})


def course_detail(request, course_name):
    course = get_object_or_404(Course, title=course_name)
    return render(request, 'course_detail.html', {'course': course})


# Тесты для курсов
@login_required
def course_test(request, course_name):
    test_questions = {
        'Backend': [
            {'id': 1, 'text': 'Сколько возможных значений у переменной типа bool?',
             'options': {'a': '1', 'b': '2', 'c': '3', 'd': '4'}, 'correct': 'b'},
            {'id': 2, 'text': 'Что делает метод словаря popitem()?',
             'options': {'a': 'Удаляет случайную пару', 'b': 'Добавляет элемент', 'c': 'Возвращает длину',
                         'd': 'Очищает словарь'}, 'correct': 'a'},
            {'id': 3, 'text': 'Что такое «else»?',
             'options': {'a': 'Цикл', 'b': 'Условие', 'c': 'Исключение', 'd': 'Функция'}, 'correct': 'b'},
            {'id': 4, 'text': 'Что делает функция len?',
             'options': {'a': 'Возвращает длину', 'b': 'Сортирует', 'c': 'Удаляет элемент', 'd': 'Добавляет элемент'},
             'correct': 'a'},
            {'id': 5, 'text': 'Что обозначает тип данных float?',
             'options': {'a': 'Целое число', 'b': 'Строку', 'c': 'Дробное число', 'd': 'Логическое значение'},
             'correct': 'c'},
            {'id': 6, 'text': 'Что хранит в себе переменная?',
             'options': {'a': 'Данные', 'b': 'Функцию', 'c': 'Класс', 'd': 'Модуль'}, 'correct': 'a'},
            {'id': 7, 'text': 'Что лучше использовать для множественного ветвления?',
             'options': {'a': 'if-elif-else', 'b': 'for', 'c': 'while', 'd': 'try-except'}, 'correct': 'a'},
            {'id': 8, 'text': 'Язык Python подходит для разработки:',
             'options': {'a': 'Только веба', 'b': 'Только игр', 'c': 'Многого', 'd': 'Только мобильных приложений'},
             'correct': 'c'},
            {'id': 9, 'text': 'Что является оператором ввода и вывода?',
             'options': {'a': 'print', 'b': 'input', 'c': 'len', 'd': 'range'}, 'correct': 'a,b'},
            # Множественный выбор пока не поддерживается, см. ниже
        ],
        'Frontend': [
            {'id': 1, 'text': 'Что такое HTML?',
             'options': {'a': 'Язык разметки', 'b': 'Язык программирования', 'c': 'Скриптовый язык',
                         'd': 'База данных'}, 'correct': 'a'},
            {'id': 2, 'text': 'Какой тег используется для заголовка?',
             'options': {'a': '<p>', 'b': '<h1>', 'c': '<div>', 'd': '<span>'}, 'correct': 'b'},
            {'id': 3, 'text': 'Что такое CSS?',
             'options': {'a': 'Язык программирования', 'b': 'База данных', 'c': 'Язык стилей', 'd': 'Фреймворк'},
             'correct': 'c'},
            {'id': 4, 'text': 'Какой метод добавляет элемент в массив в JS?',
             'options': {'a': 'push', 'b': 'pop', 'c': 'shift', 'd': 'slice'}, 'correct': 'a'},
            {'id': 5, 'text': 'Что такое DOM?',
             'options': {'a': 'База данных', 'b': 'Объектная модель документа', 'c': 'Язык стилей', 'd': 'Фреймворк'},
             'correct': 'b'},
        ],
        'Data Science': [
            {'id': 1, 'text': 'Что такое Python?',
             'options': {'a': 'Язык программирования', 'b': 'Фреймворк', 'c': 'База данных',
                         'd': 'Операционная система'}, 'correct': 'a'},
            {'id': 2, 'text': 'Какая библиотека используется для анализа данных?',
             'options': {'a': 'Django', 'b': 'Pandas', 'c': 'React', 'd': 'Flask'}, 'correct': 'b'},
            {'id': 3, 'text': 'Что такое машинное обучение?',
             'options': {'a': 'Создание сайтов', 'b': 'Работа с базами', 'c': 'Обучение моделей', 'd': 'Дизайн'},
             'correct': 'c'},
            {'id': 4, 'text': 'Что делает библиотека NumPy?',
             'options': {'a': 'Визуализация', 'b': 'Работа с массивами', 'c': 'Создание API', 'd': 'Парсинг'},
             'correct': 'b'},
            {'id': 5, 'text': 'Что такое SQL?',
             'options': {'a': 'Язык запросов', 'b': 'Язык программирования', 'c': 'Фреймворк', 'd': 'Библиотека'},
             'correct': 'a'},
        ],
        'DevOps': [
            {'id': 1, 'text': 'Что такое Docker?',
             'options': {'a': 'Контейнеризация', 'b': 'Язык программирования', 'c': 'База данных', 'd': 'Скрипт'},
             'correct': 'a'},
            {'id': 2, 'text': 'Что такое CI/CD?',
             'options': {'a': 'Интеграция и доставка', 'b': 'Язык стилей', 'c': 'Фреймворк', 'd': 'Библиотека'},
             'correct': 'a'},
            {'id': 3, 'text': 'Какой инструмент для оркестрации?',
             'options': {'a': 'Kubernetes', 'b': 'Pandas', 'c': 'React', 'd': 'Django'}, 'correct': 'a'},
            {'id': 4, 'text': 'Что делает Ansible?',
             'options': {'a': 'Автоматизация', 'b': 'Визуализация', 'c': 'Парсинг', 'd': 'Создание API'},
             'correct': 'a'},
            {'id': 5, 'text': 'Что такое Jenkins?',
             'options': {'a': 'Сервер автоматизации', 'b': 'Язык', 'c': 'База данных', 'd': 'Фреймворк'},
             'correct': 'a'},
        ],
        'AI/ML': [
            {'id': 1, 'text': 'Что такое нейронная сеть?',
             'options': {'a': 'Модель машинного обучения', 'b': 'Язык', 'c': 'База данных', 'd': 'Скрипт'},
             'correct': 'a'},
            {'id': 2, 'text': 'Какая библиотека для ML?',
             'options': {'a': 'TensorFlow', 'b': 'Django', 'c': 'Flask', 'd': 'React'}, 'correct': 'a'},
            {'id': 3, 'text': 'Что такое overfitting?',
             'options': {'a': 'Переобучение', 'b': 'Недообучение', 'c': 'Оптимизация', 'd': 'Визуализация'},
             'correct': 'a'},
            {'id': 4, 'text': 'Что делает функция sigmoid?',
             'options': {'a': 'Активация', 'b': 'Сортировка', 'c': 'Удаление', 'd': 'Добавление'}, 'correct': 'a'},
            {'id': 5, 'text': 'Что такое кластеризация?',
             'options': {'a': 'Группировка данных', 'b': 'Создание API', 'c': 'Дизайн', 'd': 'Парсинг'},
             'correct': 'a'},
        ],
    }

    questions = test_questions.get(course_name, [])
    if not questions:
        return render(request, 'course_test.html',
                      {'course_name': course_name, 'error': 'Тест для этого курса ещё не готов.'})

    if request.method == 'POST':
        total_questions = len(questions)
        correct_answers = 0
        results = []

        for q in questions:
            user_answer = request.POST.get(f'question_{q["id"]}')
            is_correct = user_answer == q['correct']
            if is_correct:
                correct_answers += 1
            results.append({
                'text': q['text'],
                'user_answer': user_answer or 'Не отвечено',
                'correct_answer': q['correct'],
                'is_correct': is_correct,
                'options': q['options']
            })

        # Проверка, что все вопросы отвечены
        if len([r for r in results if r['user_answer'] == 'Не отвечено']) > 0:
            return render(request, 'course_test.html', {
                'course_name': course_name,
                'questions': questions,
                'error': 'Пожалуйста, ответьте на все вопросы.'
            })

        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        if FavoriteCourse.objects.filter(user=request.user, course_name=course_name).exists():
            favorite = FavoriteCourse.objects.get(user=request.user, course_name=course_name)
            favorite.progress = max(favorite.progress, percentage)
            favorite.save()

        context = {
            'course_name': course_name,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'percentage': round(percentage, 2),
            'results': results,
        }
        return render(request, 'test_results.html', context)

    return render(request, 'course_test.html', {'course_name': course_name, 'questions': questions})


# Опросы
@login_required
def api_survey(request, survey_type):
    survey_questions = {
        'backend': [
            {"id": "q1", "text": "Вам нравится работать с серверной логикой?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q2", "text": "Интересуют ли вас базы данных?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q3", "text": "Любите ли вы оптимизировать код?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q4", "text": "Хотите ли вы разрабатывать API?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q5", "text": "Интересует ли вас безопасность приложений?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q6", "text": "Нравится ли вам работать с Python/Django?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q7", "text": "Любите ли вы сложные серверные задачи?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q8", "text": "Интересует ли вас масштабирование систем?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q9", "text": "Хотите ли вы работать с микросервисами?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q10", "text": "Нравится ли вам отладка серверного кода?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
        ],
        'frontend': [
            {"id": "q1", "text": "Любите ли вы создавать интерфейсы?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q2", "text": "Интересует ли вас дизайн UI/UX?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q3", "text": "Нравится ли вам работать с JavaScript?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q4", "text": "Хотите ли вы изучать React/Vue?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q5", "text": "Интересует ли вас адаптивная вёрстка?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q6", "text": "Любите ли вы анимации на сайтах?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q7", "text": "Нравится ли вам CSS и стилизация?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q8", "text": "Интересует ли вас работа с DOM?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q9", "text": "Хотите ли вы улучшать UX?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q10", "text": "Нравится ли вам тестировать интерфейсы?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
        ],
        'data_science': [
            {"id": "q1", "text": "Интересует ли вас анализ данных?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q2", "text": "Любите ли вы статистику?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q3", "text": "Нравится ли вам работать с Python?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q4", "text": "Интересуют ли вас большие данные?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q5", "text": "Хотите ли вы визуализировать данные?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q6", "text": "Любите ли вы математику?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q7", "text": "Интересует ли вас работа с SQL?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q8", "text": "Нравится ли вам исследовать данные?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q9", "text": "Хотите ли вы предсказывать тренды?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q10", "text": "Интересует ли вас очистка данных?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
        ],
        'devops': [
            {"id": "q1", "text": "Нравится ли вам настраивать серверы?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q2", "text": "Интересует ли вас автоматизация?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q3", "text": "Любите ли вы работать с Docker?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q4", "text": "Хотите ли вы управлять облаком?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q5", "text": "Интересует ли вас CI/CD?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q6", "text": "Нравится ли вам мониторинг систем?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q7", "text": "Любите ли вы Bash-скрипты?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q8", "text": "Интересует ли вас сетевая безопасность?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q9", "text": "Хотите ли вы работать с Kubernetes?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q10", "text": "Нравится ли вам решать проблемы инфраструктуры?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
        ],
        'ai_ml': [
            {"id": "q1", "text": "Интересует ли вас машинное обучение?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q2", "text": "Любите ли вы математику и статистику?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q3", "text": "Нравится ли вам работать с Python?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q4", "text": "Интересуют ли вас нейронные сети?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q5", "text": "Хотите ли вы предсказывать данные?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q6", "text": "Любите ли вы сложные алгоритмы?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q7", "text": "Интересует ли вас обработка данных?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q8", "text": "Нравится ли вам экспериментировать с моделями?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q9", "text": "Хотите ли вы работать с TensorFlow?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
            {"id": "q10", "text": "Интересует ли вас компьютерное зрение?",
             "options": {"Очень": 3, "Да": 2, "Нет": 1, "Совсем нет": 0}},
        ],
    }

    if survey_type not in survey_questions:
        messages.error(request, "Неверный тип опроса.")
        return redirect('home')

    questions = survey_questions[survey_type]

    if request.method == 'POST':
        answers = request.session.get('survey_answers', {})
        current_question = request.POST.get('current_question', 'q1')
        answer = request.POST.get(current_question)

        if answer:
            answers[current_question] = int(answer)
            request.session['survey_answers'] = answers

        next_question = None
        for i, q in enumerate(questions):
            if q['id'] == current_question and i + 1 < len(questions):
                next_question = questions[i + 1]['id']
                break

        if not next_question:
            score = sum(answers.values())
            course_title = {
                'backend': "Backend-разработка с Python",
                'frontend': "Frontend-разработка (React)",
                'data_science': "Анализ данных с Python",
                'devops': "DevOps и администрирование",
                'ai_ml': "Машинное обучение",
            }[survey_type]
            try:
                course = Course.objects.get(title=course_title)
            except Course.DoesNotExist:
                course = Course.objects.create(
                    title=course_title,
                    description=f"Курс по {survey_type}",
                    instructor=User.objects.filter(is_staff=True).first() or request.user,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=90)
                )
            Survey.objects.create(user=request.user, answers=answers, recommended_course=course)
            messages.success(request, f"Рекомендуемый курс: {course.title}")
            del request.session['survey_answers']
            return redirect('course_detail', course_name=course.title)

        return render(request, 'api_survey.html',
                      {'survey_type': survey_type, 'question': next_question, 'questions': questions})

    request.session['survey_answers'] = {}
    return render(request, 'api_survey.html', {'survey_type': survey_type, 'question': 'q1', 'questions': questions})


# Пользователи
@login_required
def api_users(request):
    if request.user.is_staff or request.user.is_superuser:
        users = User.objects.all()
    else:
        users = []
    context = {'users': users}
    return render(request, 'api_users.html', context)


# REST API Views
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        user = serializer.save()
        login(self.request, user)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj != self.request.user:
            self.permission_denied(self.request, message="Вы можете редактировать только свой профиль")
        return obj


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут создавать курсы")
        serializer.save(instructor=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут редактировать курсы")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут удалять курсы")
        instance.delete()


class ModuleListCreateView(generics.ListCreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут создавать модули")
        serializer.save()


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут редактировать модули")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут удалять модули")
        instance.delete()


class MaterialListCreateView(generics.ListCreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут создавать материалы")
        serializer.save()


class MaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут редактировать материалы")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            self.permission_denied(self.request, message="Только админы могут удалять материалы")
        instance.delete()


class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(user=self.request.user)


class UserProgressListCreateView(generics.ListCreateAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProgress.objects.all()
        return UserProgress.objects.filter(user=self.request.user)


class FavoriteCourseListCreateView(generics.ListCreateAPIView):
    queryset = FavoriteCourse.objects.all()
    serializer_class = FavoriteCourseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FavoriteCourse.objects.all()
    serializer_class = FavoriteCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return FavoriteCourse.objects.all()
        return FavoriteCourse.objects.filter(user=self.request.user)


class SurveyListCreateView(generics.ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Survey.objects.all()
        return Survey.objects.filter(user=self.request.user)


class CustomTokenObtainPairView(TokenObtainPairView):
    pass


class CustomTokenRefreshView(TokenRefreshView):
    pass
