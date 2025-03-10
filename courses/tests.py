from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from courses.models import Course, FavoriteCourse
from django.utils import timezone
from datetime import datetime
from django.test import TestCase, Client


# Тесты для API
class CourseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course_data = {
            'title': 'Django для начинающих',
            'description': 'Изучение фреймворка Django.',
            'start_date': timezone.make_aware(datetime(2025, 3, 1)),
            'end_date': timezone.make_aware(datetime(2025, 5, 1)),
            'instructor': self.user.id,
        }

    def test_create_course(self):
        response = self.client.post(reverse('course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.course_data['title'])


class CourseIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course_data = {
            'title': 'Django для начинающих',
            'description': 'Изучение фреймворка Django.',
            'start_date': timezone.make_aware(datetime(2025, 3, 1)),
            'end_date': timezone.make_aware(datetime(2025, 5, 1)),
            'instructor': self.user.id,
        }

    def test_create_and_get_course_integration(self):
        response = self.client.post(reverse('course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['id']
        response = self.client.get(reverse('course_detail_api', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course_data['title'])

    def test_delete_course_integration(self):
        response = self.client.post(reverse('course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['id']
        response = self.client.delete(reverse('course_detail_api', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(reverse('course_detail_api', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Тесты для обычных вьюх
class CoursesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.admin = User.objects.create_superuser(username='admin', password='adminpass123')
        self.course = Course.objects.create(
            title='Backend',
            description='Тестовый курс',
            instructor=self.admin,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )

    def test_courses_list_page(self):
        response = self.client.get(reverse('api_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api_courses.html')

    def test_toggle_favorite_add(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('toggle_favorite'),
            {'course_name': 'Backend', 'action': 'add'},
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'added'})
        self.assertTrue(FavoriteCourse.objects.filter(user=self.user, course_name='Backend').exists())

    def test_favorites_page_with_course(self):
        self.client.login(username='testuser', password='testpass123')
        FavoriteCourse.objects.create(user=self.user, course_name='Backend', progress=50)
        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend')

    def test_users_page_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('api_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api_users.html')
        self.assertContains(response, 'testuser')
