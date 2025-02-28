from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Добавляем кастомное сообщение об ошибке
        response.data['detail'] = 'Произошла ошибка'

    return response
