import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from jobs.models import Category

# Словарь с обновленными названиями категорий
category_updates = {
    # ID: {name_en}
    1: {'name_en': 'Web Development'},
    2: {'name_en': 'Mobile Development'},
    3: {'name_en': 'Design & UI/UX'},
    4: {'name_en': 'Content & Copywriting'},
    5: {'name_en': 'Translation & Localization'},
    6: {'name_en': 'Digital Marketing'},
    7: {'name_en': 'SEO & SEM'},
    8: {'name_en': 'Audio & Video Production'},
    9: {'name_en': 'Data Science & Analytics'},
    10: {'name_en': 'Finance & Accounting'},
    11: {'name_en': 'Legal Services'},
    12: {'name_en': 'Virtual Assistance & Admin Support'},
}

# Обновление категорий
updated_count = 0
for category_id, updates in category_updates.items():
    try:
        category = Category.objects.get(id=category_id)
        
        # Обновление полей
        for field, value in updates.items():
            setattr(category, field, value)
        
        category.save()
        print(f"Обновлена категория {category.id}: {category.name} → {category.name_en}")
        updated_count += 1
        
    except Category.DoesNotExist:
        print(f"Категория с ID {category_id} не найдена")
    except Exception as e:
        print(f"Ошибка при обновлении категории {category_id}: {str(e)}")

print(f"\nОбновлено категорий: {updated_count}")
