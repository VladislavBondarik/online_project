from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Module, Material, Enrollment, UserProgress, FavoriteCourse, Survey


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'instructor']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'course']


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'title', 'type', 'content', 'file', 'module']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'enrollment_date', 'status']


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'course', 'module', 'progress', 'last_updated']


class FavoriteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteCourse
        fields = ['id', 'user', 'course_name', 'progress']


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'user', 'answers', 'recommended_course', 'created_at']
