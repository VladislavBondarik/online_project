from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Course, Module, Material


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Обязательно. До 150 символов. Только буквы, цифры и @/./+/-/_',
            'password1': 'Минимум 8 символов. Не используйте личные данные или простые пароли.',
            'password2': 'Введите пароль ещё раз для подтверждения.',
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'instructor', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'course']


class MaterialForm(forms.ModelForm):
    content_url = forms.CharField(
        label='URL (альтернатива файлу)',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Или введите URL'})
    )

    class Meta:
        model = Material
        fields = ['title', 'type', 'content', 'module']
        widgets = {
            'content': forms.FileInput(),
        }
