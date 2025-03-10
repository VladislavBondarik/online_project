from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from courses.models import Course, Module, Material, Enrollment, UserProgress, FavoriteCourse
from django.utils import timezone
from datetime import datetime
from django.test import TestCase, Client


# Тесты для API
class CourseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course_data = {
            'title': 'Django для начинающих',
            'description': 'Изучение фреймворка Django.',
            'start_date': timezone.make_aware(datetime(2025, 3, 1)).isoformat(),
            'end_date': timezone.make_aware(datetime(2025, 5, 1)).isoformat(),
            'instructor': self.admin.id
        }

    def test_create_course(self):
        response = self.client.post(reverse('courses:course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.course_data['title'])

    def test_update_course(self):
        course = Course.objects.create(
            title='Django для начинающих', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )
        updated_data = {
            'title': 'Django Advanced',
            'description': 'Изучение фреймворка Django.',
            'start_date': timezone.make_aware(datetime(2025, 3, 1)).isoformat(),
            'end_date': timezone.make_aware(datetime(2025, 5, 1)).isoformat(),
            'instructor': self.admin.id
        }
        response = self.client.put(reverse('courses:course_detail_api', kwargs={'pk': course.id}), updated_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Django Advanced')

    def test_delete_course(self):
        course = Course.objects.create(
            title='Django для начинающих', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )
        response = self.client.delete(reverse('courses:course_detail_api', kwargs={'pk': course.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ModuleTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course = Course.objects.create(
            title='Test Course', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.module_data = {
            'title': 'Module 1',
            'description': 'First module',
            'course': self.course.id
        }

    def test_create_module(self):
        response = self.client.post(reverse('courses:module_list_create'), self.module_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Module 1')

    def test_update_module(self):
        module = Module.objects.create(title='Module 1', description='First module', course=self.course)
        updated_data = {
            'title': 'Module 2',
            'description': 'First module',
            'course': self.course.id
        }
        response = self.client.put(reverse('courses:module_detail', kwargs={'pk': module.id}), updated_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Module 2')


class MaterialTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course = Course.objects.create(
            title='Test Course', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.module = Module.objects.create(title='Module 1', description='Test', course=self.course)
        self.material_data = {
            'title': 'Material 1',
            'type': 'video',
            'content': 'http://example.com/video',
            'module': self.module.id
        }

    def test_create_material(self):
        response = self.client.post(reverse('courses:material_list_create'), self.material_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Material 1')

    def test_get_material(self):
        material = Material.objects.create(title='Material 1', type='video', content='http://example.com/video',
                                           module=self.module)
        response = self.client.get(reverse('courses:material_detail', kwargs={'pk': material.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Material 1')


class EnrollmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course = Course.objects.create(
            title='Test Course', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.enrollment_data = {
            'user': self.user.id,
            'course': self.course.id,
            'status': 'active'
        }

    def test_create_enrollment(self):
        response = self.client.post(reverse('courses:enrollment_list_create'), self.enrollment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_enrollment(self):
        enrollment = Enrollment.objects.create(user=self.user, course=self.course, status='active')
        updated_data = {'status': 'completed'}
        response = self.client.patch(reverse('courses:enrollment_detail', kwargs={'pk': enrollment.id}), updated_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')


class UserProgressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course = Course.objects.create(
            title='Test Course', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.module = Module.objects.create(title='Module 1', description='Test', course=self.course)
        self.progress_data = {
            'user': self.user.id,
            'course': self.course.id,
            'module': self.module.id,
            'progress': 50
        }

    def test_create_progress(self):
        response = self.client.post(reverse('courses:progress_list_create'), self.progress_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['progress'], 50)

    def test_update_progress(self):
        progress = UserProgress.objects.create(user=self.user, course=self.course, module=self.module, progress=50)
        updated_data = {'progress': 75}
        response = self.client.patch(reverse('courses:progress_detail', kwargs={'pk': progress.id}), updated_data,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 75)


# Интеграционные тесты
class CourseIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username="admin", password="password")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course_data = {
            'title': 'Django для начинающих',
            'description': 'Изучение фреймворка Django.',
            'start_date': timezone.make_aware(datetime(2025, 3, 1)).isoformat(),
            'end_date': timezone.make_aware(datetime(2025, 5, 1)).isoformat(),
            'instructor': self.user.id
        }

    def test_create_and_get_course_integration(self):
        response = self.client.post(reverse('courses:course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['id']
        response = self.client.get(reverse('courses:course_detail_api', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course_data['title'])

    def test_delete_course_integration(self):
        response = self.client.post(reverse('courses:course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['id']
        response = self.client.delete(reverse('courses:course_detail_api', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(reverse('courses:course_detail_api', kwargs={'pk': course_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EnrollmentIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.course = Course.objects.create(
            title='Test Course', description='Test', instructor=self.admin,
            start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=30)
        )

    def test_enroll_and_check_progress(self):
        enrollment_data = {'user': self.user.id, 'course': self.course.id, 'status': 'active'}
        response = self.client.post(reverse('courses:enrollment_list_create'), enrollment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        enrollment_id = response.data['id']
        response = self.client.get(reverse('courses:enrollment_detail', kwargs={'pk': enrollment_id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


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
        response = self.client.get(reverse('courses:api_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api_courses.html')

    def test_toggle_favorite_add(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('courses:toggle_favorite'),
            {'course_name': 'Backend', 'action': 'add'},
            content_type='application/x-www-form-urlencoded'
        )
        print(f"Request URL: {response.request['PATH_INFO']}")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'added'})
        self.assertTrue(FavoriteCourse.objects.filter(user=self.user, course_name='Backend').exists())

    def test_favorites_page_with_course(self):
        self.client.login(username='testuser', password='testpass123')
        FavoriteCourse.objects.create(user=self.user, course_name='Backend', progress=50)
        response = self.client.get(reverse('courses:favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend')

    def test_users_page_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('courses:api_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api_users.html')
        self.assertContains(response, 'testuser')

    def test_course_create_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(
            reverse('courses:course_create'),
            {'title': 'New Course', 'description': 'Test', 'start_date': '2025-03-01', 'end_date': '2025-05-01',
             'instructor': self.admin.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Course.objects.filter(title='New Course').exists())

    def test_course_detail(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('courses:course_detail', kwargs={'course_name': 'Backend'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_detail.html')
        self.assertContains(response, 'Backend')

    def test_profile_page(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('courses:api_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api_profile.html')
        self.assertContains(response, 'testuser')

    def test_enroll_course(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('courses:course_detail', kwargs={'course_name': 'Backend'}),
            {'enroll': 'True'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())