@echo off
echo Запускаю сервер разработки с SSL на порту 8000...
SET SERVER_ENV=local
SET DJANGO_DEBUG=True

REM Проверяем наличие SSL-сертификатов
if not exist "ssl" mkdir ssl
if not exist "ssl\sslserver.crt" (
    echo SSL-сертификаты не найдены. Пробую создать...
    if exist "generate_ssl_cert.py" (
        python generate_ssl_cert.py
    ) else (
        echo ВНИМАНИЕ: Скрипт generate_ssl_cert.py не найден
        echo Запускаю сервер без SSL...
        python manage.py runserver 0.0.0.0:8000
        exit /b
    )
)

REM Устанавливаем переменные окружения для SSL
if exist "ssl\sslserver.crt" (
    SET SSLSERVER_CERTIFICATE=%CD%\ssl\sslserver.crt
)
if exist "ssl\sslserver.key" (
    SET SSLSERVER_KEY=%CD%\ssl\sslserver.key
)

python manage.py runsslserver --addrport=0.0.0.0:8000 