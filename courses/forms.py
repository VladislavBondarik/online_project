from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


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
