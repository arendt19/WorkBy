from django.core.management.base import BaseCommand
from jobs.models import Tag

class Command(BaseCommand):
    help = 'Fills translations for tags'

    def handle(self, *args, **options):
        # Словарь с переводами с русского на английский
        translations = {
            # Технологии и языки программирования
            'Питон': 'Python',
            'Джаваскрипт': 'JavaScript',
            'Джанго': 'Django',
            'Реакт': 'React',
            'Ангуляр': 'Angular',
            'Вью': 'Vue.js',
            'ХТМЛ': 'HTML',
            'ЦСС': 'CSS',
            'ЭсКьюЭль': 'SQL',
            'НоСКЛ': 'NoSQL',
            # Дизайн
            'Фотошоп': 'Photoshop',
            'Иллюстратор': 'Illustrator', 
            'Фигма': 'Figma',
            'Дизайн интерфейса': 'UI Design',
            'Дизайн взаимодействия': 'UX Design',
            'Графический дизайн': 'Graphic Design',
            'Веб-дизайн': 'Web Design',
            # Маркетинг
            'Контекстная реклама': 'PPC Advertising',
            'Поисковая оптимизация': 'SEO',
            'Контент-маркетинг': 'Content Marketing',
            'Маркетинг в соцсетях': 'Social Media Marketing',
            'Аналитика': 'Analytics',
        }
        
        # Словарь с обратными переводами (с английского на русский)
        reverse_translations = {
            'Python': 'Питон',
            'JavaScript': 'Джаваскрипт',
            'Django': 'Джанго',
            'React': 'Реакт',
            'Angular': 'Ангуляр',
            'Vue.js': 'Вью',
            'HTML': 'HTML',
            'CSS': 'CSS',
            'SQL': 'SQL',
            'NoSQL': 'НоСКЛ',
            'Photoshop': 'Фотошоп',
            'Illustrator': 'Иллюстратор',
            'Figma': 'Фигма',
            'UI Design': 'Дизайн интерфейса',
            'UX Design': 'Дизайн взаимодействия',
            'Graphic Design': 'Графический дизайн',
            'Web Design': 'Веб-дизайн',
            'PPC Advertising': 'Контекстная реклама',
            'SEO': 'Поисковая оптимизация',
            'Content Marketing': 'Контент-маркетинг',
            'Social Media Marketing': 'Маркетинг в соцсетях',
            'Analytics': 'Аналитика',
            'Branding': 'Брендинг',
            'UI/UX': 'UI/UX',
            'Translation': 'Перевод',
            'Wordpress': 'Вордпресс',
            'Swift': 'Свифт',
            'Java': 'Ява',
        }
        
        tags = Tag.objects.all()
        updated_count_en = 0
        updated_count_ru = 0
        
        for tag in tags:
            updated = False
            
            # Заполняем английский перевод, если он отсутствует
            if not tag.name_en:
                # Пытаемся найти перевод по русскому имени или основному имени
                if tag.name_ru and tag.name_ru in translations:
                    tag.name_en = translations[tag.name_ru]
                    updated = True
                    updated_count_en += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated name_en: {tag.name} -> {tag.name_en}"))
                elif tag.name in translations:
                    tag.name_en = translations[tag.name]
                    updated = True
                    updated_count_en += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated name_en: {tag.name} -> {tag.name_en}"))
                else:
                    # Если перевод не найден, используем основное имя
                    tag.name_en = tag.name
                    updated = True
                    updated_count_en += 1
                    self.stdout.write(self.style.WARNING(f"No English translation found, using original name: {tag.name}"))
            
            # Заполняем русский перевод, если он отсутствует
            if not tag.name_ru:
                # Пытаемся найти обратный перевод по английскому имени или основному имени
                if tag.name_en and tag.name_en in reverse_translations:
                    tag.name_ru = reverse_translations[tag.name_en]
                    updated = True
                    updated_count_ru += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated name_ru: {tag.name} -> {tag.name_ru}"))
                elif tag.name in reverse_translations:
                    tag.name_ru = reverse_translations[tag.name]
                    updated = True
                    updated_count_ru += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated name_ru: {tag.name} -> {tag.name_ru}"))
                else:
                    # Для технических терминов часто оставляем такие же как в английском
                    tag.name_ru = tag.name
                    updated = True
                    updated_count_ru += 1
                    self.stdout.write(self.style.WARNING(f"No Russian translation found, using original name: {tag.name}"))
            
            if updated:
                tag.save()
        
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count_en} English translations and {updated_count_ru} Russian translations successfully!")) 