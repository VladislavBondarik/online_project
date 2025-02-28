from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from courses.models import Course
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class CourseTests(APITestCase):

    def setUp(self):
        # Создаем суперпользователя и токен для аутентификации
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Данные курса для тестов
        self.course_data = {
            'title': 'Django для начинающих',
            'description': 'Изучение фреймворка Django.',
            'start_date': '2025-03-01',
            'end_date': '2025-05-01',
            'instructor': self.user.id,  # Используем ID пользователя, а не строку
        }

    # Юнит-тесты для CRUD-операций
    def test_create_course(self):
        """Тестирование создания нового курса"""
        response = self.client.post(reverse('course-list'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.course_data['title'])

    def test_read_course(self):
        """Тестирование чтения данных о курсе"""
        # Сначала создаем курс через API
        response = self.client.post(reverse('course-list'), self.course_data, format='json')
        course_id = response.data['id']

        # Теперь получаем курс
        response = self.client.get(reverse('course-detail', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course_data['title'])  # исправлено на `self.course_data['title']`

    def test_update_course(self):
        """Тестирование обновления данных курса"""
        # Сначала создаем курс через API
        response = self.client.post(reverse('course-list'), self.course_data, format='json')
        course_id = response.data['id']

        updated_data = {
            'title': 'Django: Продвинутый курс',
            'description': 'Изучение продвинутых функций Django.',
            'start_date': '2025-06-01',
            'end_date': '2025-08-01',
            'instructor': self.user.id,  # Используем ID пользователя, а не строку
        }

        response = self.client.put(reverse('course-detail', kwargs={'pk': course_id}), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])

    def test_delete_course(self):
        """Тестирование удаления курса"""
        # Сначала создаем курс через API
        response = self.client.post(reverse('course-list'), self.course_data, format='json')
        course_id = response.data['id']

        # Удаляем курс
        response = self.client.delete(reverse('course-detail', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что курс удален
        response = self.client.get(reverse('course-detail', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CourseIntegrationTests(APITestCase):

    def setUp(self):
        # Создаем суперпользователя и токен для аутентификации
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Данные курса для тестов
        self.course_data = {
            'title': 'Django для начинающих',
            'description': 'Изучение фреймворка Django.',
            'start_date': '2025-03-01',
            'end_date': '2025-05-01',
            'instructor': self.user.id,  # Используем ID пользователя, а не строку
        }

    def test_create_and_get_course_integration(self):
        """Тестирование взаимодействия: создание и получение курса"""
        response = self.client.post(reverse('course-list'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        course_id = response.data['id']
        response = self.client.get(reverse('course-detail', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course_data['title'])

    def test_delete_course_integration(self):
        """Тестирование взаимодействия: создание и удаление курса"""
        response = self.client.post(reverse('course-list'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Удаляем курс
        course_id = response.data['id']
        response = self.client.delete(reverse('course-detail', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что курс удален
        response = self.client.get(reverse('course-detail', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
