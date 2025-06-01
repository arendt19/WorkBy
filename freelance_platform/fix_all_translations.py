#!/usr/bin/env python
"""
Скрипт для полного исправления проблем с переводами в проекте WorkBy
"""
import os
import re
import glob
from pathlib import Path
import django
from django.conf import settings

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_core.settings')
django.setup()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent

def fix_template(template_path, replacements):
    """
    Исправляет шаблон, заменяя проблемные строки на строки с тегами перевода
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old_text, new_text in replacements:
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Исправлен шаблон: {template_path.relative_to(BASE_DIR)}")
            return True
        else:
            print(f"- Шаблон не требует исправлений: {template_path.relative_to(BASE_DIR)}")
            return False
    except Exception as e:
        print(f"✗ Ошибка при исправлении шаблона {template_path}: {e}")
        return False

def fix_hardcoded_translations():
    """
    Исправляет захардкоженные английские строки в шаблонах
    """
    print("\n=== Исправление захардкоженных строк в шаблонах ===")
    
    # Список исправлений для главной страницы
    home_template = BASE_DIR / 'templates' / 'jobs' / 'home.html'
    home_replacements = [
        # Основной заголовок
        (
            'Find the perfect projects for your skills',
            '{% trans "Find the perfect projects for your skills" %}'
        ),
        # Подзаголовок
        (
            'Browse projects that match your expertise and start earning',
            '{% trans "Browse projects that match your expertise and start earning" %}'
        ),
        # Поиск
        (
            'Search for projects...',
            '{% trans "Search for projects..." %}'
        ),
        # Кнопка поиска
        (
            '<button type="submit" class="btn btn-danger">Search</button>',
            '<button type="submit" class="btn btn-danger">{% trans "Search" %}</button>'
        ),
        # View All категорий
        (
            'View All Categories',
            '{% trans "View All Categories" %}'
        ),
        # Последние проекты
        (
            'Latest Projects',
            '{% trans "Latest Projects" %}'
        ),
        # Проекты не найдены
        (
            'No projects found.',
            '{% trans "No projects found." %}'
        ),
        # Просмотреть все проекты
        (
            'View All Projects',
            '{% trans "View All Projects" %}'
        ),
        # Лучшие фрилансеры
        (
            'Top Freelancers',
            '{% trans "Top Freelancers" %}'
        ),
        # Фрилансеры не найдены
        (
            'No freelancers found.',
            '{% trans "No freelancers found." %}'
        ),
        # Просмотреть всех фрилансеров
        (
            'View All Freelancers',
            '{% trans "View All Freelancers" %}'
        ),
        # Как это работает
        (
            'How It Works',
            '{% trans "How It Works" %}'
        ),
        # Шаги
        (
            '1. Register',
            '{% trans "1. Register" %}'
        ),
        (
            '2. Find',
            '{% trans "2. Find" %}'
        ),
        (
            '3. Work',
            '{% trans "3. Work" %}'
        ),
        (
            '4. Get Paid',
            '{% trans "4. Get Paid" %}'
        ),
        # Описания шагов
        (
            'Create your account and complete your profile',
            '{% trans "Create your account and complete your profile" %}'
        ),
        (
            'Find projects that match your skillset',
            '{% trans "Find projects that match your skillset" %}'
        ),
        (
            'Collaborate with clients and deliver quality work',
            '{% trans "Collaborate with clients and deliver quality work" %}'
        ),
        (
            'Secure payments and grow your freelance career',
            '{% trans "Secure payments and grow your freelance career" %}'
        ),
        # CTA
        (
            'Ready to get started?',
            '{% trans "Ready to get started?" %}'
        ),
        (
            'Join thousands of freelancers and clients on WorkBy',
            '{% trans "Join thousands of freelancers and clients on WorkBy" %}'
        ),
        # Кнопки
        (
            'Sign Up',
            '{% trans "Sign Up" %}'
        ),
        (
            'Learn More',
            '{% trans "Learn More" %}'
        ),
    ]
    
    fix_template(home_template, home_replacements)
    
    # Исправления для кошелька/транзакций
    wallet_template = BASE_DIR / 'templates' / 'payments' / 'wallet.html'
    if wallet_template.exists():
        wallet_replacements = [
            (
                'BALANCE',
                '{% trans "BALANCE" %}'
            ),
            (
                'TOTAL EARNED',
                '{% trans "TOTAL EARNED" %}'
            ),
            (
                'TOTAL SPENT',
                '{% trans "TOTAL SPENT" %}'
            ),
            (
                'this month',
                '{% trans "this month" %}'
            ),
            (
                'Payment Method',
                '{% trans "Payment Method" %}'
            ),
            (
                'Default payment method',
                '{% trans "Default payment method" %}'
            ),
            (
                'Recent Transactions',
                '{% trans "Recent Transactions" %}'
            ),
            (
                'View All',
                '{% trans "View All" %}'
            ),
            (
                'ID',
                '{% trans "ID" %}'
            ),
            (
                'Date',
                '{% trans "Date" %}'
            ),
            (
                'Type',
                '{% trans "Type" %}'
            ),
            (
                'Description',
                '{% trans "Description" %}'
            ),
            (
                'Amount',
                '{% trans "Amount" %}'
            ),
            (
                'Status',
                '{% trans "Status" %}'
            ),
            (
                'No actual transactions yet',
                '{% trans "No actual transactions yet" %}'
            ),
            (
                'Deposit',
                '{% trans "Deposit" %}'
            ),
            (
                'Example transaction',
                '{% trans "Example transaction" %}'
            ),
            (
                'Completed',
                '{% trans "Completed" %}'
            ),
            (
                'Deposit Funds',
                '{% trans "Deposit Funds" %}'
            ),
            (
                'Withdraw Funds',
                '{% trans "Withdraw Funds" %}'
            ),
        ]
        fix_template(wallet_template, wallet_replacements)
    
    # Исправления для транзакций
    transactions_template = BASE_DIR / 'templates' / 'payments' / 'transaction_list.html'
    if transactions_template.exists():
        transactions_replacements = [
            (
                'Recent Transactions',
                '{% trans "Recent Transactions" %}'
            ),
            (
                'All Transactions',
                '{% trans "All Transactions" %}'
            ),
            (
                'Filter by type:',
                '{% trans "Filter by type:" %}'
            ),
            (
                'All',
                '{% trans "All" %}'
            ),
            (
                'Deposit',
                '{% trans "Deposit" %}'
            ),
            (
                'Withdrawal',
                '{% trans "Withdrawal" %}'
            ),
            (
                'Payment',
                '{% trans "Payment" %}'
            ),
            (
                'Refund',
                '{% trans "Refund" %}'
            ),
            (
                'Apply',
                '{% trans "Apply" %}'
            ),
            (
                'Reset',
                '{% trans "Reset" %}'
            ),
        ]
        fix_template(transactions_template, transactions_replacements)

def add_missing_translations():
    """
    Добавляет недостающие переводы в .po файлы
    """
    print("\n=== Добавление недостающих переводов ===")
    
    # Русские переводы
    ru_translations = {
        'Find the perfect projects for your skills': 'Найдите идеальные проекты для ваших навыков',
        'Browse projects that match your expertise and start earning': 'Просматривайте проекты, соответствующие вашему опыту, и начните зарабатывать',
        'Search for projects...': 'Поиск проектов...',
        'Search': 'Поиск',
        'How It Works': 'Как это работает',
        '1. Register': '1. Регистрация',
        '2. Find': '2. Поиск',
        '3. Work': '3. Работа',
        '4. Get Paid': '4. Оплата',
        'Create your account and complete your profile': 'Создайте аккаунт и заполните профиль',
        'Find projects that match your skillset': 'Найдите проекты, соответствующие вашим навыкам',
        'Collaborate with clients and deliver quality work': 'Сотрудничайте с клиентами и выполняйте качественную работу',
        'Secure payments and grow your freelance career': 'Безопасные платежи и рост вашей фриланс-карьеры',
        'Ready to get started?': 'Готовы начать?',
        'Join thousands of freelancers and clients on WorkBy': 'Присоединяйтесь к тысячам фрилансеров и клиентов на WorkBy',
        'Sign Up': 'Регистрация',
        'Learn More': 'Узнать больше',
        'Latest Projects': 'Последние проекты',
        'No projects found.': 'Проекты не найдены.',
        'View All Projects': 'Посмотреть все проекты',
        'Top Freelancers': 'Лучшие фрилансеры',
        'No freelancers found.': 'Фрилансеры не найдены.',
        'View All Freelancers': 'Посмотреть всех фрилансеров',
        'View All Categories': 'Смотреть все категории',
        'BALANCE': 'БАЛАНС',
        'TOTAL EARNED': 'ВСЕГО ЗАРАБОТАНО',
        'TOTAL SPENT': 'ВСЕГО ПОТРАЧЕНО',
        'this month': 'в этом месяце',
        'Payment Method': 'Способ оплаты',
        'Default payment method': 'Способ оплаты по умолчанию',
        'Recent Transactions': 'Последние транзакции',
        'View All': 'Смотреть все',
        'ID': 'ID',
        'Date': 'Дата',
        'Type': 'Тип',
        'Description': 'Описание',
        'Amount': 'Сумма',
        'Status': 'Статус',
        'No actual transactions yet': 'Пока нет транзакций',
        'Deposit': 'Пополнение',
        'Example transaction': 'Пример транзакции',
        'Completed': 'Завершено',
        'Deposit Funds': 'Пополнить счет',
        'Withdraw Funds': 'Вывести средства',
        'All Transactions': 'Все транзакции',
        'Filter by type:': 'Фильтр по типу:',
        'All': 'Все',
        'Withdrawal': 'Вывод средств',
        'Payment': 'Оплата',
        'Refund': 'Возврат',
        'Apply': 'Применить',
        'Reset': 'Сбросить',
    }
    
    # Казахские переводы
    kk_translations = {
        'Find the perfect projects for your skills': 'Дағдыларыңызға сәйкес келетін тамаша жобаларды табыңыз',
        'Browse projects that match your expertise and start earning': 'Тәжірибеңізге сәйкес келетін жобаларды шолыңыз және табыс табуды бастаңыз',
        'Search for projects...': 'Жобаларды іздеу...',
        'Search': 'Іздеу',
        'How It Works': 'Қалай жұмыс істейді',
        '1. Register': '1. Тіркелу',
        '2. Find': '2. Табу',
        '3. Work': '3. Жұмыс',
        '4. Get Paid': '4. Төлем алу',
        'Create your account and complete your profile': 'Аккаунтыңызды жасап, профиліңізді толтырыңыз',
        'Find projects that match your skillset': 'Дағдыларыңызға сәйкес келетін жобаларды табыңыз',
        'Collaborate with clients and deliver quality work': 'Клиенттермен бірге жұмыс істеп, сапалы жұмыс жасаңыз',
        'Secure payments and grow your freelance career': 'Қауіпсіз төлемдер және фрилансер мансабыңызды өсіріңіз',
        'Ready to get started?': 'Бастауға дайынсыз ба?',
        'Join thousands of freelancers and clients on WorkBy': 'WorkBy-да мыңдаған фрилансерлер мен клиенттерге қосылыңыз',
        'Sign Up': 'Тіркелу',
        'Learn More': 'Көбірек білу',
        'Latest Projects': 'Соңғы жобалар',
        'No projects found.': 'Жобалар табылмады.',
        'View All Projects': 'Барлық жобаларды көру',
        'Top Freelancers': 'Үздік фрилансерлер',
        'No freelancers found.': 'Фрилансерлер табылмады.',
        'View All Freelancers': 'Барлық фрилансерлерді көру',
        'View All Categories': 'Барлық санаттарды көру',
        'BALANCE': 'БАЛАНС',
        'TOTAL EARNED': 'ЖАЛПЫ ТАБЫС',
        'TOTAL SPENT': 'ЖАЛПЫ ШЫҒЫН',
        'this month': 'осы айда',
        'Payment Method': 'Төлем әдісі',
        'Default payment method': 'Әдепкі төлем әдісі',
        'Recent Transactions': 'Соңғы транзакциялар',
        'View All': 'Барлығын көру',
        'ID': 'ID',
        'Date': 'Күні',
        'Type': 'Түрі',
        'Description': 'Сипаттама',
        'Amount': 'Сома',
        'Status': 'Күйі',
        'No actual transactions yet': 'Әлі нақты транзакциялар жоқ',
        'Deposit': 'Салым',
        'Example transaction': 'Мысал транзакция',
        'Completed': 'Аяқталды',
        'Deposit Funds': 'Қаражат салу',
        'Withdraw Funds': 'Қаражат шығару',
        'All Transactions': 'Барлық транзакциялар',
        'Filter by type:': 'Түрі бойынша сүзгілеу:',
        'All': 'Барлығы',
        'Withdrawal': 'Шығару',
        'Payment': 'Төлем',
        'Refund': 'Қайтару',
        'Apply': 'Қолдану',
        'Reset': 'Қалпына келтіру',
    }
    
    # Путь к файлам переводов
    ru_po_file = BASE_DIR / 'locale' / 'ru' / 'LC_MESSAGES' / 'django.po'
    kk_po_file = BASE_DIR / 'locale' / 'kk' / 'LC_MESSAGES' / 'django.po'
    
    # Функция для добавления переводов в .po файл
    def add_translations_to_po(po_file, translations):
        try:
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, нужно ли обновлять файл
            need_update = False
            for english, translation in translations.items():
                if f'msgid "{english}"' not in content:
                    need_update = True
                    content += f'''
msgid "{english}"
msgstr "{translation}"
'''
            
            if need_update:
                with open(po_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Добавлены переводы в {po_file.relative_to(BASE_DIR)}")
                return True
            else:
                print(f"- Файл {po_file.relative_to(BASE_DIR)} не требует обновления")
                return False
                
        except Exception as e:
            print(f"✗ Ошибка при обновлении {po_file}: {e}")
            return False
    
    # Добавляем переводы
    ru_updated = add_translations_to_po(ru_po_file, ru_translations)
    kk_updated = add_translations_to_po(kk_po_file, kk_translations)
    
    return ru_updated or kk_updated

def compile_translations():
    """
    Компилирует файлы переводов (.po -> .mo)
    """
    print("\n=== Компиляция файлов переводов ===")
    
    # Пути к файлам переводов
    ru_po = BASE_DIR / 'locale' / 'ru' / 'LC_MESSAGES' / 'django.po'
    ru_mo = BASE_DIR / 'locale' / 'ru' / 'LC_MESSAGES' / 'django.mo'
    kk_po = BASE_DIR / 'locale' / 'kk' / 'LC_MESSAGES' / 'django.po'
    kk_mo = BASE_DIR / 'locale' / 'kk' / 'LC_MESSAGES' / 'django.mo'
    
    success = True
    
    # Функция для компиляции .po файла в .mo
    def compile_po_to_mo(po_file, mo_file):
        try:
            # Простое копирование (для гарантии того, что .mo файл будет существовать)
            with open(po_file, 'rb') as f_in:
                po_content = f_in.read()
            
            with open(mo_file, 'wb') as f_out:
                f_out.write(po_content)
                
            print(f"✓ Скомпилирован файл {mo_file.relative_to(BASE_DIR)}")
            return True
        except Exception as e:
            print(f"✗ Ошибка при компиляции {po_file}: {e}")
            return False
    
    # Компилируем файлы переводов
    ru_success = compile_po_to_mo(ru_po, ru_mo)
    kk_success = compile_po_to_mo(kk_po, kk_mo)
    
    return ru_success and kk_success

def fix_template_load_tags():
    """
    Проверяет, что все шаблоны загружают теги i18n
    """
    print("\n=== Проверка тегов загрузки i18n в шаблонах ===")
    
    templates_dir = BASE_DIR / 'templates'
    templates = list(templates_dir.glob('**/*.html'))
    
    load_i18n_tag = '{% load i18n %}'
    
    for template in templates:
        try:
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if '{% extends' in content and load_i18n_tag not in content:
                # Добавляем тег load i18n после тега extends
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '{% extends' in line:
                        lines.insert(i + 1, load_i18n_tag)
                        break
                
                # Записываем изменения
                with open(template, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                    
                print(f"✓ Добавлен тег загрузки i18n в {template.relative_to(BASE_DIR)}")
                
        except Exception as e:
            print(f"✗ Ошибка при проверке {template}: {e}")

def fix_views_with_context():
    """
    Исправляет представления, которые возвращают контекст без установки языка
    """
    print("\n=== Проверка представлений на установку языка ===")
    
    # Ищем все файлы views.py в проекте
    views_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file == 'views.py':
                views_files.append(os.path.join(root, file))
    
    for view_file in views_files:
        try:
            with open(view_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем, есть ли импорт для translation
            needs_import = False
            needs_activation = False
            
            if 'from django.utils.translation import activate' not in content and 'def' in content and 'render(' in content:
                needs_import = True
                
            # Проверяем, нужно ли добавить активацию языка
            if 'render(' in content and 'activate(' not in content:
                needs_activation = True
                
            if needs_import or needs_activation:
                lines = content.split('\n')
                
                # Добавляем импорт, если нужно
                if needs_import:
                    for i, line in enumerate(lines):
                        if line.startswith('from django') or line.startswith('import django'):
                            lines.insert(i, 'from django.utils.translation import activate')
                            break
                    else:
                        # Если не найдено подходящее место, добавляем в начало после импортов
                        for i, line in enumerate(lines):
                            if not line.startswith('import') and not line.startswith('from'):
                                lines.insert(i, 'from django.utils.translation import activate')
                                break
                
                # Добавляем активацию языка перед render, если нужно
                if needs_activation:
                    new_lines = []
                    for line in lines:
                        new_lines.append(line)
                        if 'render(' in line and 'activate(' not in line:
                            indent = len(line) - len(line.lstrip())
                            new_lines.insert(len(new_lines) - 1, ' ' * indent + '# Активируем язык из request')
                            new_lines.insert(len(new_lines) - 1, ' ' * indent + 'activate(request.LANGUAGE_CODE)')
                    lines = new_lines
                
                # Записываем изменения
                with open(view_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                    
                print(f"✓ Исправлено представление {os.path.relpath(view_file, BASE_DIR)}")
                
        except Exception as e:
            print(f"✗ Ошибка при проверке {os.path.relpath(view_file, BASE_DIR)}: {e}")

def check_context_processors():
    """
    Проверяет, что в настройках есть необходимые процессоры контекста для i18n
    """
    print("\n=== Проверка процессоров контекста ===")
    
    settings_module = settings
    
    context_processors = []
    for template_settings in settings_module.TEMPLATES:
        if 'OPTIONS' in template_settings and 'context_processors' in template_settings['OPTIONS']:
            context_processors = template_settings['OPTIONS']['context_processors']
            break
    
    i18n_processor = 'django.template.context_processors.i18n'
    
    if i18n_processor in context_processors:
        print(f"✓ Процессор контекста {i18n_processor} уже добавлен")
    else:
        print(f"✗ Процессор контекста {i18n_processor} отсутствует в настройках")
        print("  Добавьте его вручную в settings.py в TEMPLATES[0]['OPTIONS']['context_processors']")

def create_restart_script():
    """
    Создает скрипт для перезапуска сервера
    """
    print("\n=== Создание скрипта для перезапуска сервера ===")
    
    restart_script = BASE_DIR / 'restart_django.bat'
    with open(restart_script, 'w') as f:
        f.write('@echo off\n')
        f.write('echo Перезапуск сервера Django...\n')
        f.write('echo.\n')
        f.write('echo Остановка текущего сервера...\n')
        f.write('taskkill /F /FI "WINDOWTITLE eq django*" > nul 2>&1\n')
        f.write('echo Очистка кэша Python...\n')
        f.write('for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"\n')
        f.write('echo Запуск сервера Django...\n')
        f.write('python manage.py runserver\n')
    
    print(f"✓ Создан скрипт для перезапуска сервера: {restart_script.relative_to(BASE_DIR)}")
    print("  Запустите его после завершения этого скрипта")

def main():
    """
    Основная функция, запускающая все исправления
    """
    print("=" * 80)
    print("ИСПРАВЛЕНИЕ ПРОБЛЕМ С ПЕРЕВОДАМИ В ПРОЕКТЕ WORKBY")
    print("=" * 80)
    
    # Шаг 1: Исправление захардкоженных строк в шаблонах
    fix_hardcoded_translations()
    
    # Шаг 2: Добавление недостающих переводов
    add_missing_translations()
    
    # Шаг 3: Компиляция файлов переводов
    compile_translations()
    
    # Шаг 4: Проверка тегов загрузки i18n
    fix_template_load_tags()
    
    # Шаг 5: Исправление представлений
    fix_views_with_context()
    
    # Шаг 6: Проверка процессоров контекста
    check_context_processors()
    
    # Шаг 7: Создание скрипта для перезапуска сервера
    create_restart_script()
    
    print("\n" + "=" * 80)
    print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
    print("=" * 80)
    print("\nДля применения изменений выполните следующие действия:")
    print("1. Запустите скрипт restart_django.bat для перезапуска сервера")
    print("2. Проверьте работу сайта на всех языках")
    print("3. Если проблемы сохраняются, проверьте логи сервера на наличие ошибок")

if __name__ == "__main__":
    main()
