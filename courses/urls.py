from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('overview/', views.api_overview, name='api_overview'),
    path('about/', views.about, name='about'),
    path('join/', views.join, name='join'),
    path('login/', views.api_login, name='api_login'),
    path('logout/', views.api_logout, name='api_logout'),
    path('profile/', views.api_profile, name='api_profile'),
    path('settings/', views.settings, name='settings'),

    # Курсы и связанные функции
    path('courses/', views.api_courses, name='api_courses'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:pk>/edit/', views.course_create, name='course_edit'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('course/<str:course_name>/', views.course_detail, name='course_detail'),
    path('course/<str:course_name>/test/', views.course_test, name='course_test'),
    path('favorites/', views.favorites, name='favorites'),
    path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('survey/<str:survey_type>/', views.api_survey, name='api_survey'),

    # Модули
    path('modules/', views.module_list, name='module_list'),
    path('modules/create/', views.module_create, name='module_create'),
    path('modules/<int:pk>/edit/', views.module_edit, name='module_edit'),
    path('modules/<int:pk>/delete/', views.module_delete, name='module_delete'),

    # Материалы
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),

    # Админ
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('users/', views.api_users, name='api_users'),

    # REST API
    path('api/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('api/users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('api/courses/', views.CourseListCreateView.as_view(), name='course_list_create'),
    path('api/courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail_api'),
    path('api/modules/', views.ModuleListCreateView.as_view(), name='module_list_create'),
    path('api/modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('api/materials/', views.MaterialListCreateView.as_view(), name='material_list_create'),
    path('api/materials/<int:pk>/', views.MaterialDetailView.as_view(), name='material_detail'),
    path('api/enrollments/', views.EnrollmentListCreateView.as_view(), name='enrollment_list_create'),
    path('api/enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('api/progress/', views.UserProgressListCreateView.as_view(), name='progress_list_create'),
    path('api/progress/<int:pk>/', views.UserProgressDetailView.as_view(), name='progress_detail'),
    path('api/favorites/', views.FavoriteCourseListCreateView.as_view(), name='favorite_list_create'),
    path('api/favorites/<int:pk>/', views.FavoriteCourseDetailView.as_view(), name='favorite_detail'),
    path('api/surveys/', views.SurveyListCreateView.as_view(), name='survey_list_create'),
    path('api/surveys/<int:pk>/', views.SurveyDetailView.as_view(), name='survey_detail'),
]