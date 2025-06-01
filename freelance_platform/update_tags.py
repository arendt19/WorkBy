import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

from jobs.models import Tag

# Технические навыки для проектов
tech_tags = [
    # Веб-разработка
    {"name": "JavaScript", "name_en": "JavaScript", "name_ru": "JavaScript", "name_kk": "JavaScript"},
    {"name": "TypeScript", "name_en": "TypeScript", "name_ru": "TypeScript", "name_kk": "TypeScript"},
    {"name": "React", "name_en": "React", "name_ru": "React", "name_kk": "React"},
    {"name": "Angular", "name_en": "Angular", "name_ru": "Angular", "name_kk": "Angular"},
    {"name": "Vue.js", "name_en": "Vue.js", "name_ru": "Vue.js", "name_kk": "Vue.js"},
    {"name": "Node.js", "name_en": "Node.js", "name_ru": "Node.js", "name_kk": "Node.js"},
    {"name": "PHP", "name_en": "PHP", "name_ru": "PHP", "name_kk": "PHP"},
    {"name": "Laravel", "name_en": "Laravel", "name_ru": "Laravel", "name_kk": "Laravel"},
    {"name": "Django", "name_en": "Django", "name_ru": "Django", "name_kk": "Django"},
    {"name": "Flask", "name_en": "Flask", "name_ru": "Flask", "name_kk": "Flask"},
    {"name": "ASP.NET", "name_en": "ASP.NET", "name_ru": "ASP.NET", "name_kk": "ASP.NET"},
    
    # Мобильная разработка
    {"name": "iOS", "name_en": "iOS", "name_ru": "iOS", "name_kk": "iOS"},
    {"name": "Android", "name_en": "Android", "name_ru": "Android", "name_kk": "Android"},
    {"name": "Swift", "name_en": "Swift", "name_ru": "Swift", "name_kk": "Swift"},
    {"name": "Kotlin", "name_en": "Kotlin", "name_ru": "Kotlin", "name_kk": "Kotlin"},
    {"name": "Flutter", "name_en": "Flutter", "name_ru": "Flutter", "name_kk": "Flutter"},
    {"name": "React Native", "name_en": "React Native", "name_ru": "React Native", "name_kk": "React Native"},
    
    # Дизайн
    {"name": "UI Design", "name_en": "UI Design", "name_ru": "UI Дизайн", "name_kk": "UI Дизайн"},
    {"name": "UX Design", "name_en": "UX Design", "name_ru": "UX Дизайн", "name_kk": "UX Дизайн"},
    {"name": "Figma", "name_en": "Figma", "name_ru": "Figma", "name_kk": "Figma"},
    {"name": "Adobe XD", "name_en": "Adobe XD", "name_ru": "Adobe XD", "name_kk": "Adobe XD"},
    {"name": "Photoshop", "name_en": "Photoshop", "name_ru": "Photoshop", "name_kk": "Photoshop"},
    {"name": "Illustrator", "name_en": "Illustrator", "name_ru": "Illustrator", "name_kk": "Illustrator"},
    {"name": "Logo Design", "name_en": "Logo Design", "name_ru": "Дизайн логотипа", "name_kk": "Логотип дизайны"},
    {"name": "Branding", "name_en": "Branding", "name_ru": "Брендинг", "name_kk": "Брендинг"},
    
    # Контент и копирайтинг
    {"name": "Copywriting", "name_en": "Copywriting", "name_ru": "Копирайтинг", "name_kk": "Копирайтинг"},
    {"name": "Content Writing", "name_en": "Content Writing", "name_ru": "Написание контента", "name_kk": "Контент жазу"},
    {"name": "SEO Writing", "name_en": "SEO Writing", "name_ru": "SEO копирайтинг", "name_kk": "SEO копирайтинг"},
    {"name": "Technical Writing", "name_en": "Technical Writing", "name_ru": "Техническая документация", "name_kk": "Техникалық құжаттама"},
    {"name": "Blog Writing", "name_en": "Blog Writing", "name_ru": "Написание блогов", "name_kk": "Блог жазу"},
    
    # Перевод и локализация
    {"name": "Translation", "name_en": "Translation", "name_ru": "Перевод", "name_kk": "Аударма"},
    {"name": "Localization", "name_en": "Localization", "name_ru": "Локализация", "name_kk": "Локализация"},
    {"name": "Proofreading", "name_en": "Proofreading", "name_ru": "Корректура", "name_kk": "Түзету"},
    
    # Маркетинг
    {"name": "Digital Marketing", "name_en": "Digital Marketing", "name_ru": "Цифровой маркетинг", "name_kk": "Цифрлық маркетинг"},
    {"name": "Social Media", "name_en": "Social Media", "name_ru": "Социальные сети", "name_kk": "Әлеуметтік желілер"},
    {"name": "Content Strategy", "name_en": "Content Strategy", "name_ru": "Контент-стратегия", "name_kk": "Контент стратегиясы"},
    {"name": "Email Marketing", "name_en": "Email Marketing", "name_ru": "Email-маркетинг", "name_kk": "Email-маркетинг"},
    
    # SEO
    {"name": "SEO", "name_en": "SEO", "name_ru": "SEO", "name_kk": "SEO"},
    {"name": "SEM", "name_en": "SEM", "name_ru": "SEM", "name_kk": "SEM"},
    {"name": "Google Ads", "name_en": "Google Ads", "name_ru": "Google Ads", "name_kk": "Google Ads"},
    {"name": "Analytics", "name_en": "Analytics", "name_ru": "Аналитика", "name_kk": "Аналитика"},
    
    # Аудио и видео
    {"name": "Video Editing", "name_en": "Video Editing", "name_ru": "Видеомонтаж", "name_kk": "Бейне өңдеу"},
    {"name": "Animation", "name_en": "Animation", "name_ru": "Анимация", "name_kk": "Анимация"},
    {"name": "Voice Over", "name_en": "Voice Over", "name_ru": "Озвучивание", "name_kk": "Дауыстандыру"},
    {"name": "Audio Editing", "name_en": "Audio Editing", "name_ru": "Аудиомонтаж", "name_kk": "Аудио өңдеу"},
    
    # Data Science
    {"name": "Data Analysis", "name_en": "Data Analysis", "name_ru": "Анализ данных", "name_kk": "Деректерді талдау"},
    {"name": "Machine Learning", "name_en": "Machine Learning", "name_ru": "Машинное обучение", "name_kk": "Машиналық оқыту"},
    {"name": "Python", "name_en": "Python", "name_ru": "Python", "name_kk": "Python"},
    {"name": "R", "name_en": "R", "name_ru": "R", "name_kk": "R"},
    {"name": "SQL", "name_en": "SQL", "name_ru": "SQL", "name_kk": "SQL"},
    {"name": "Big Data", "name_en": "Big Data", "name_ru": "Большие данные", "name_kk": "Үлкен деректер"},
    
    # Финансы
    {"name": "Accounting", "name_en": "Accounting", "name_ru": "Бухгалтерия", "name_kk": "Бухгалтерлік есеп"},
    {"name": "Financial Analysis", "name_en": "Financial Analysis", "name_ru": "Финансовый анализ", "name_kk": "Қаржылық талдау"},
    {"name": "Tax Preparation", "name_en": "Tax Preparation", "name_ru": "Налоговая отчетность", "name_kk": "Салық есептілігі"},
    
    # Юридические услуги
    {"name": "Legal Writing", "name_en": "Legal Writing", "name_ru": "Юридические тексты", "name_kk": "Заңды мәтіндер"},
    {"name": "Contract Review", "name_en": "Contract Review", "name_ru": "Проверка договоров", "name_kk": "Келісімшарттарды тексеру"},
    {"name": "Legal Consulting", "name_en": "Legal Consulting", "name_ru": "Юридическая консультация", "name_kk": "Заңгерлік кеңес беру"},
    
    # Виртуальные ассистенты
    {"name": "Virtual Assistant", "name_en": "Virtual Assistant", "name_ru": "Виртуальный ассистент", "name_kk": "Виртуалды көмекші"},
    {"name": "Data Entry", "name_en": "Data Entry", "name_ru": "Ввод данных", "name_kk": "Деректерді енгізу"},
    {"name": "Administrative Support", "name_en": "Administrative Support", "name_ru": "Административная поддержка", "name_kk": "Әкімшілік қолдау"},
]

# Подсчет тегов для отчета
created_count = 0
updated_count = 0
error_count = 0

# Проходим по всем тегам и создаем или обновляем их
for tag_data in tech_tags:
    try:
        tag, created = Tag.objects.update_or_create(
            name=tag_data["name"],
            defaults={
                "name_en": tag_data.get("name_en", ""),
                "name_ru": tag_data.get("name_ru", ""),
                "name_kk": tag_data.get("name_kk", ""),
                "slug": tag_data["name"].lower().replace(" ", "-").replace(".", "")
            }
        )
        
        if created:
            print(f"Создан тег: {tag.name}")
            created_count += 1
        else:
            print(f"Обновлен тег: {tag.name}")
            updated_count += 1
            
    except Exception as e:
        print(f"Ошибка при обработке тега {tag_data['name']}: {str(e)}")
        error_count += 1

print(f"\nИтоги:")
print(f"Создано новых тегов: {created_count}")
print(f"Обновлено существующих тегов: {updated_count}")
print(f"Ошибок: {error_count}")
print(f"Всего обработано: {len(tech_tags)}")
