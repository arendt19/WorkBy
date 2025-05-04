#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("SERVER_ENV", "local")
    os.environ.setdefault("DJANGO_DEBUG", "True")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freelance_core.settings")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Запускаем обычный HTTP-сервер
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"] + sys.argv[1:]) 