from django.urls import path, include
from .views import (
    UserCreateView, UserListView, UserDetailView, LoginView, LogoutView,
    CourseListCreateView, CourseDetailView,
    ModuleListCreateView, ModuleDetailView,
    MaterialListCreateView, MaterialDetailView,
    EnrollmentListCreateView, EnrollmentDetailView,
    UserProgressListCreateView, UserProgressDetailView,
    CustomTokenObtainPairView, CustomTokenRefreshView,CourseViewSet

)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
urlpatterns = [

    # --- Пользователи ---
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # --- Курсы ---
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    # --- Модули ---
    path('modules/', ModuleListCreateView.as_view(), name='module-list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),

    # --- Учебные материалы ---
    path('materials/', MaterialListCreateView.as_view(), name='material-list'),
    path('materials/<int:pk>/', MaterialDetailView.as_view(), name='material-detail'),

    # --- Записи на курсы ---
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),

    # --- Прогресс пользователя ---
    path('progress/', UserProgressListCreateView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', UserProgressDetailView.as_view(), name='progress-detail'),

    # ... другие маршруты
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('api/', include(router.urls)),
]

