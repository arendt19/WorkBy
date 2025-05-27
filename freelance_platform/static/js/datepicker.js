/**
 * Глобальная инициализация календарей для выбора даты
 * Использует Flatpickr для создания удобного и красивого выбора даты
 */

// Прямое подключение скрипта Flatpickr
(function() {
    // Загрузка стилей Flatpickr
    var linkMain = document.createElement('link');
    linkMain.rel = 'stylesheet';
    linkMain.href = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css';
    document.head.appendChild(linkMain);

    var linkDark = document.createElement('link');
    linkDark.rel = 'stylesheet';
    linkDark.href = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/dark.css';
    document.head.appendChild(linkDark);

    // Загрузка скрипта Flatpickr
    var script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/flatpickr';
    script.onload = function() {
        // Загрузка русской локализации
        var localeScript = document.createElement('script');
        localeScript.src = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js';
        localeScript.onload = function() {
            setTimeout(initAllDatepickers, 500);  // Небольшая задержка для гарантии загрузки
        };
        document.head.appendChild(localeScript);
    };
    document.head.appendChild(script);

    // Главная функция инициализации всех датапикеров
    function initAllDatepickers() {
        if (typeof flatpickr === 'undefined') {
            console.error('Ошибка: Flatpickr не загружен');
            return;
        }

        // Добавляем дополнительные стили для календаря
        var extraStyles = document.createElement('style');
        extraStyles.textContent = `
            .flatpickr-calendar.dark {
                background: #222;
                border-color: #444;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                z-index: 99999 !important;
            }
            .flatpickr-calendar.dark .flatpickr-months .flatpickr-month,
            .flatpickr-calendar.dark .flatpickr-months .flatpickr-next-month, 
            .flatpickr-calendar.dark .flatpickr-months .flatpickr-prev-month {
                color: #fff;
                fill: #fff;
            }
            .flatpickr-calendar.dark .flatpickr-day {
                color: #eee;
            }
            .flatpickr-calendar.dark .flatpickr-day.selected {
                background: #dc3545;
                border-color: #dc3545;
            }
            .flatpickr-calendar.dark .flatpickr-day:hover {
                background: #333;
            }
            input[type="date"], input[type="datetime-local"], input.datepicker {
                cursor: pointer;
            }
        `;
        document.head.appendChild(extraStyles);

        // Находим все поля для выбора даты
        var dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"], input.datepicker');
        console.log('Найдено полей для даты:', dateInputs.length);

        // Общие настройки календаря
        var defaultConfig = {
            dateFormat: 'Y-m-d',
            locale: 'ru',
            theme: 'dark',
            allowInput: true,
            disableMobile: true,
            appendTo: document.body,
            position: 'auto center',
            static: false,
            time_24hr: true,
            monthSelectorType: 'static'
        };

        // Инициализируем календарь для каждого поля
        dateInputs.forEach(function(input) {
            try {
                // Если инпут уже инициализирован, уничтожаем его
                if (input._flatpickr) {
                    input._flatpickr.destroy();
                }
                
                // Изменяем тип поля на text
                var originalType = input.type;
                if (originalType === 'date' || originalType === 'datetime-local') {
                    input.setAttribute('data-original-type', originalType);
                    input.type = 'text';
                }
                
                // Добавляем класс datepicker, если его нет
                if (!input.classList.contains('datepicker')) {
                    input.classList.add('datepicker');
                }
                
                // Настраиваем конфигурацию для конкретного поля
                var config = Object.assign({}, defaultConfig);
                if (originalType === 'datetime-local' || input.getAttribute('data-original-type') === 'datetime-local') {
                    config.dateFormat = 'Y-m-d H:i';
                    config.enableTime = true;
                }
                
                // Создаем календарь
                var datepicker = flatpickr(input, config);
                console.log('Инициализирован календарь для', input.id || input.name || 'unnamed input');
                
                // Добавляем обработчик клика для дополнительной гарантии
                input.addEventListener('click', function() {
                    if (datepicker) {
                        datepicker.open();
                    }
                });
                
            } catch (e) {
                console.error('Ошибка при инициализации календаря:', e);
            }
        });
        
        // Отслеживание динамически добавляемых полей
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Элемент
                            var newDateInputs = node.querySelectorAll ? 
                                node.querySelectorAll('input[type="date"], input[type="datetime-local"], input.datepicker') : [];
                            
                            if (newDateInputs.length > 0) {
                                setTimeout(function() {
                                    newDateInputs.forEach(function(input) {
                                        try {
                                            if (!input._flatpickr) {
                                                var originalType = input.type;
                                                if (originalType === 'date' || originalType === 'datetime-local') {
                                                    input.setAttribute('data-original-type', originalType);
                                                    input.type = 'text';
                                                }
                                                
                                                var config = Object.assign({}, defaultConfig);
                                                if (originalType === 'datetime-local' || input.getAttribute('data-original-type') === 'datetime-local') {
                                                    config.dateFormat = 'Y-m-d H:i';
                                                    config.enableTime = true;
                                                }
                                                
                                                flatpickr(input, config);
                                                console.log('Инициализирован динамический календарь для', input.id || input.name || 'unnamed input');
                                            }
                                        } catch (e) {
                                            console.error('Ошибка при инициализации динамического календаря:', e);
                                        }
                                    });
                                }, 100);
                            }
                        }
                    });
                }
            });
        });
        
        // Начинаем наблюдение за изменениями в DOM
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Инициализация при загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof flatpickr !== 'undefined') {
            setTimeout(initAllDatepickers, 100);
        }
    });

    // Дублируем инициализацию для уверенности
    window.onload = function() {
        if (typeof flatpickr !== 'undefined') {
            setTimeout(initAllDatepickers, 100);
        }
    };

    // Экспортируем функцию для внешнего использования
    window.initAllDatepickers = initAllDatepickers;
})();

/**
 * Инициализация календарей на странице
 */
function initDatepickers() {
    if (!isFlatpickrLoaded()) {
        console.warn('Библиотека Flatpickr не загружена. Календари не будут инициализированы.');
        return;
    }
    
    // Находим все поля с типом date и datetime-local
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"], input.datepicker');
    
    if (dateInputs.length === 0) return;
    
    console.log('Найдено полей для даты:', dateInputs.length);
    
    // Создаем конфигурацию для календаря
    const defaultConfig = {
        dateFormat: 'Y-m-d',
        locale: 'ru',
        theme: 'dark',
        allowInput: true,
        disableMobile: true,
        monthSelectorType: 'static',
        appendTo: document.body,
        position: 'auto center',
        static: false,
        animate: true,
        time_24hr: true,
        onChange: function(selectedDates, dateStr, instance) {
            console.log('Выбрана дата:', dateStr);
        }
    };
    
    // Применяем календарь ко всем найденным полям
    dateInputs.forEach(function(input) {
        try {
            // Если календарь уже инициализирован, пропускаем
            if (input._flatpickr) return;

            // Меняем тип поля на text для лучшей стилизации
            const originalType = input.type;
            if (originalType === 'date' || originalType === 'datetime-local') {
                input.setAttribute('data-original-type', originalType);
                input.type = 'text';
                input.classList.add('datepicker');
            }
            
            // Настраиваем формат даты в зависимости от типа поля
            const config = { ...defaultConfig };
            if (originalType === 'datetime-local' || input.getAttribute('data-original-type') === 'datetime-local') {
                config.dateFormat = 'Y-m-d H:i';
                config.enableTime = true;
            }
            
            // Инициализируем Flatpickr
            const instance = flatpickr(input, config);
            console.log('Инициализирован календарь для', input.id || input.name || 'unnamed input');
        } catch (e) {
            console.error('Ошибка при инициализации календаря:', e);
        }
    });
}

/**
 * Отслеживание динамически добавленных полей даты
 */
function observeDynamicDatepickers() {
    // Настраиваем MutationObserver для отслеживания изменений в DOM
    const observer = new MutationObserver(function(mutations) {
        let shouldInit = false;
        
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        // Проверяем, есть ли поля даты в добавленных узлах
                        const dateInputs = node.querySelectorAll ? 
                            node.querySelectorAll('input[type="date"], input[type="datetime-local"], input.datepicker') : [];
                        
                        if (dateInputs.length > 0) {
                            shouldInit = true;
                        }
                    }
                });
            }
        });
        
        // Если найдены новые поля даты, инициализируем их
        if (shouldInit) {
            initDatepickers();
        }
    });
    
    // Начинаем наблюдение за изменениями в DOM
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
}
