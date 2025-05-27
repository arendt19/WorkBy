from django.core.management.base import BaseCommand
from jobs.models import Category

class Command(BaseCommand):
    help = 'Fills translations for categories'

    def handle(self, *args, **options):
        # Словарь с переводами с русского на английский
        translations = {
            'Веб-разработка': 'Web Development',
            'Разработка мобильных приложений': 'Mobile App Development',
            'Графический дизайн': 'Graphic Design',
            'Написание контента': 'Content Writing',
            'Цифровой маркетинг': 'Digital Marketing',
            'Видеопроизводство': 'Video Production',
            'Перевод': 'Translation',
            'Наука о данных': 'Data Science',
            'UI/UX дизайн': 'UI/UX Design',
            'Бэкенд-разработка': 'Backend Development',
            'Фронтенд-разработка': 'Frontend Development',
            'DevOps': 'DevOps',
            'Разработка игр': 'Game Development',
            'ИИ и машинное обучение': 'AI & Machine Learning',
            'Блокчейн': 'Blockchain',
            'Разработка электронной коммерции': 'E-commerce Development',
            'Юридические услуги': 'Legal Services',
            'Финансовые услуги': 'Financial Services',
            'Бизнес-консалтинг': 'Business Consulting',
            'Бухгалтерский учет': 'Accounting & Bookkeeping',
            'SEO и SMM': 'SEO & SMM',
            'Аудио и видео': 'Audio & Video',
            'Веб-разработка': 'Web Development',
            'Дизайн': 'Design',
            'Контент и копирайтинг': 'Content & Copywriting',
            'Маркетинг': 'Marketing',
            'Мобильная разработка': 'Mobile Development',
        }
        
        # Словарь с обратными переводами (с английского на русский)
        reverse_translations = {v: k for k, v in translations.items()}
        
        categories = Category.objects.all()
        updated_count = 0
        ru_updated_count = 0
        
        for category in categories:
            updated = False
            
            # Заполняем английский перевод, если он отсутствует
            if not category.name_en:
                # Пытаемся найти перевод по русскому имени или основному имени
                if category.name_ru and category.name_ru in translations:
                    category.name_en = translations[category.name_ru]
                    updated = True
                    self.stdout.write(self.style.SUCCESS(f"Updated name_en: {category.name} -> {category.name_en}"))
                elif category.name in translations:
                    category.name_en = translations[category.name]
                    updated = True
                    self.stdout.write(self.style.SUCCESS(f"Updated name_en: {category.name} -> {category.name_en}"))
                else:
                    # Если перевод не найден, используем основное имя
                    category.name_en = category.name
                    updated = True
                    self.stdout.write(self.style.WARNING(f"No English translation found, using original name: {category.name}"))
                
                updated_count += 1
            
            # Заполняем русский перевод, если он отсутствует
            if not category.name_ru:
                # Пытаемся найти обратный перевод по английскому имени
                if category.name_en and category.name_en in reverse_translations:
                    category.name_ru = reverse_translations[category.name_en]
                    updated = True
                    ru_updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated name_ru: {category.name} -> {category.name_ru}"))
                elif category.name in reverse_translations:
                    category.name_ru = reverse_translations[category.name]
                    updated = True
                    ru_updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated name_ru: {category.name} -> {category.name_ru}"))
                else:
                    # Если обратный перевод не найден и имя похоже на русское, используем основное имя
                    category.name_ru = category.name
                    updated = True
                    ru_updated_count += 1
                    self.stdout.write(self.style.WARNING(f"No Russian translation found, using original name: {category.name}"))
            
            if updated:
                category.save()
        
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} English translations and {ru_updated_count} Russian translations successfully!")) 