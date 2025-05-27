# WorkBy - Платформа для фрилансеров

WorkBy - это современная платформа для фрилансеров и заказчиков, где можно находить и публиковать проекты, а также общаться с потенциальными клиентами и исполнителями.

## Особенности

- Аутентификация и авторизация пользователей
- Личные профили фрилансеров и клиентов
- Создание и поиск проектов
- Система предложений и контрактов
- Безопасная система оплаты
- Чат между клиентами и фрилансерами
- Многоязычный интерфейс (английский, русский, казахский)
- Адаптивный дизайн (включая тёмную тему)

## Технологии

- Django 5.1
- Django Channels (для вебсокетов)
- Bootstrap 4
- PostgreSQL (SQLite для разработки)
- Redis (для кеширования и очередей)

## Установка и запуск

### Для разработки

1. Клонируйте репозиторий:
```
git clone https://github.com/yourusername/workby.git
cd workby
```

2. Создайте виртуальное окружение и установите зависимости:
```
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
pip install -e .
pip install -r .venv-requirements.txt
```

3. Запустите миграции:
```
python manage.py migrate
```

4. Создайте суперпользователя:
```
python manage.py createsuperuser
```

5. Запустите сервер разработки:
```
python manage.py runserver
```

### Для продакшена

1. Установите зависимости продакшена:
```
pip install -r requirements-prod.txt
```

2. Настройте переменные окружения или файл `.env`:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@host:port/database
ALLOWED_HOSTS=example.com,www.example.com
```

3. Соберите статические файлы:
```
python manage.py collectstatic
```

4. Запустите миграции:
```
python manage.py migrate
```

5. Запустите с использованием ASGI-сервера (например, Daphne):
```
daphne freelance_core.asgi:application
```

## Структура проекта

- `accounts` - Приложение для управления пользователями и профилями
- `jobs` - Приложение для управления проектами и предложениями
- `payments` - Приложение для управления платежами
- `chat` - Приложение для системы сообщений
- `freelance_core` - Основные настройки проекта

## Разработка



### Форматирование кода

```
black .
isort .
```

### Статический анализ

```
pylint --load-plugins=pylint_django accounts jobs payments chat
```

## Лицензия

Этот проект распространяется под лицензией MIT. 