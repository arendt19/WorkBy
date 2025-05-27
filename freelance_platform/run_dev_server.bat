@echo off
echo Запускаю сервер разработки на порту 8000...
SET SERVER_ENV=local
SET DJANGO_DEBUG=True
python manage.py runserver 0.0.0.0:8000 