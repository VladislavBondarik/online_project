# API-документация

## 1. Создание курса
### Endpoint:
`POST /api/courses/`

### Параметры:
- `title`: (string) Название курса.
- `description`: (string) Описание курса.
- `start_date`: (string, формат: YYYY-MM-DD) Дата начала курса.
- `end_date`: (string, формат: YYYY-MM-DD) Дата окончания курса.
- `instructor`: (integer) ID инструктора (ссылка на пользователя).

### Пример запроса:
```json
{
  "title": "Django для начинающих",
  "description": "Основы работы с Django.",
  "start_date": "2025-03-01",
  "end_date": "2025-05-01",
  "instructor": 1
}
