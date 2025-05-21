/**
 * WorkBy Platform - Main JavaScript File
 * Contains global functions and utilities used across the platform
 */

// Base64 звуковое уведомление (короткий звук)
const NOTIFICATION_SOUND_BASE64 = "data:audio/mp3;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gQ29uZWN0ZWRTb3VuZHMuY29tAAAAQ09NTAAAAB0AAABUaXRsZQBOb3RpZmljYXRpb24gU291bmQgMQAAAENPTU0AAAAlAAAAYWxidW0AU291bmQgRWZmZWN0cyAtIE5vdGlmaWNhdGlvbnMAAP/7kAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAABCAAAisAAGBg0NDRQUGxsb" + 
"IiIoKCgvLzU1NTw8QkJCSUlJUFBWVlZdXWNjY2pqcHBwd3d9fX2EhIqKipGRl5eXnp6kpKSrq7Gxsbi4vr6+xcXLy8vS0tjY2N/f5eXl7Oz4+Pj///8AAAA5TEFNRTMuMTAwAc0AAAAAAAAAABRAJAjmQgAAMAAAACKwxZC9OAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + 
"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/7kGQAD/AAAGkAAAAIAAANIAAAAQAAAaQAAAAgAAA0gAAABExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV" + 
"VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//uQZAAP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV" + 
"VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV" + 
"VVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVQ==";

/**
 * Функция для воспроизведения звукового уведомления
 * @param {number} volume - громкость от 0 до 1, по умолчанию 0.5
 */
function playNotificationSound(volume = 0.5) {
    try {
        const audio = new Audio(NOTIFICATION_SOUND_BASE64);
        audio.volume = volume;
        audio.play().catch(e => {
            console.log('Notification sound could not be played', e);
        });
    } catch (e) {
        console.error('Error playing notification sound:', e);
    }
}

/**
 * Функция для обработки AJAX-запросов
 * @param {Object} options - настройки запроса
 */
function ajaxRequest(options) {
    const defaultOptions = {
        method: 'GET',
        url: '',
        data: null,
        success: function() {},
        error: function() {},
        complete: function() {}
    };

    // Объединяем переданные параметры с параметрами по умолчанию
    const settings = Object.assign({}, defaultOptions, options);
    
    // Создаём объект XMLHttpRequest
    const xhr = new XMLHttpRequest();
    
    xhr.open(settings.method, settings.url, true);
    
    // Устанавливаем заголовки
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    if (settings.method.toUpperCase() === 'POST') {
        // Для POST-запросов с FormData не устанавливаем Content-Type
        if (!(settings.data instanceof FormData)) {
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        }
    }
    
    // Получаем CSRF-токен из cookie
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }
    
    // Обработчики событий
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            let response;
            try {
                response = JSON.parse(xhr.responseText);
            } catch (e) {
                response = xhr.responseText;
            }
            settings.success(response, xhr);
        } else {
            settings.error(xhr);
        }
        settings.complete(xhr);
    };
    
    xhr.onerror = function() {
        settings.error(xhr);
        settings.complete(xhr);
    };
    
    // Отправляем запрос
    if (settings.data) {
        if (settings.data instanceof FormData) {
            xhr.send(settings.data);
        } else if (typeof settings.data === 'object') {
            xhr.send(JSON.stringify(settings.data));
        } else {
            xhr.send(settings.data);
        }
    } else {
        xhr.send();
    }
    
    return xhr;
}

/**
 * Получение значения cookie по имени
 * @param {string} name - название cookie
 * @return {string|null} - значение cookie или null
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Форматирование даты и времени
 * @param {Date|string} dateInput - объект Date или строка с датой
 * @param {string} format - формат вывода (по умолчанию 'DD.MM.YYYY HH:mm')
 * @return {string} - отформатированная дата
 */
function formatDateTime(dateInput, format = 'DD.MM.YYYY HH:mm') {
    const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
    
    if (isNaN(date.getTime())) {
        return 'Invalid Date';
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return format
        .replace('DD', day)
        .replace('MM', month)
        .replace('YYYY', year)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

/**
 * Функция для форматирования валюты
 * @param {number} amount - сумма
 * @param {string} currency - символ валюты (по умолчанию '₸')
 * @return {string} - форматированная строка с суммой и валютой
 */
function formatCurrency(amount, currency = '₸') {
    return amount.toLocaleString('ru-RU') + ' ' + currency;
}

/**
 * Показать быстрое уведомление пользователю
 * @param {string} message - сообщение для отображения
 * @param {string} type - тип уведомления ('success', 'error', 'info', 'warning')
 * @param {number} timeout - время в миллисекундах, через которое сообщение исчезнет
 */
function showToast(message, type = 'info', timeout = 3000) {
    // Проверяем, существует ли контейнер для уведомлений
    let container = document.getElementById('toast-container');
    
    // Если контейнера нет, создаем его
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Создаем элемент уведомления
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.backgroundColor = type === 'success' ? '#28a745' : 
                                 type === 'error' ? '#dc3545' : 
                                 type === 'warning' ? '#ffc107' : '#17a2b8';
    toast.style.color = type === 'warning' ? '#212529' : '#fff';
    toast.style.padding = '12px 15px';
    toast.style.borderRadius = '4px';
    toast.style.marginBottom = '10px';
    toast.style.boxShadow = '0 0.25rem 0.75rem rgba(0, 0, 0, 0.1)';
    toast.style.transition = 'all 0.3s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    toast.textContent = message;
    
    // Добавляем уведомление в контейнер
    container.appendChild(toast);
    
    // Анимируем появление
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Запускаем звуковое уведомление
    if (type === 'success' || type === 'error') {
        playNotificationSound(0.3);
    }
    
    // Устанавливаем таймер для удаления
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        
        // После завершения анимации удаляем элемент
        setTimeout(() => {
            container.removeChild(toast);
            
            // Если в контейнере не осталось уведомлений, удаляем его
            if (container.children.length === 0) {
                document.body.removeChild(container);
            }
        }, 300);
    }, timeout);
}

/**
 * Инициализация при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Инициализация Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Экспортируем функции для использования в других скриптах
window.WorkBy = {
    playNotificationSound,
    ajaxRequest,
    getCookie,
    formatDateTime,
    formatCurrency,
    showToast
};

// Main JavaScript for WorkBy

// Функция для инициализации всех тултипов
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Функция для инициализации всех поповеров
function initPopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

// Функция для инициализации форм переключения языка
function initLanguageForms() {
    // Находим все формы переключения языка
    const languageForms = document.querySelectorAll('.language-form');
    
    languageForms.forEach(form => {
        // Находим кнопку внутри формы
        const button = form.querySelector('button');
        // Находим выбранный язык
        const langInput = form.querySelector('input[name="language"]');
        
        if (button && langInput) {
            // Добавляем обработчик на клик по кнопке
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Получаем выбранный язык
                const selectedLang = langInput.value;
                
                // Получаем текущий URL
                let currentPath = window.location.pathname;
                
                // Отправляем форму, но не переходим по ее действию
                fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                }).then(response => {
                    // После отправки формы, перенаправляем пользователя на URL с правильным префиксом языка
                    let newPath = currentPath;
                    
                    // Удаляем существующий префикс языка, если он есть
                    const langPrefixes = ['/en/', '/ru/', '/kk/'];
                    for (const prefix of langPrefixes) {
                        if (currentPath.startsWith(prefix)) {
                            currentPath = currentPath.substring(prefix.length - 1);
                            break;
                        }
                    }
                    
                    // Если начинается с '/', сохраняем, иначе добавляем '/'
                    if (!currentPath.startsWith('/')) {
                        currentPath = '/' + currentPath;
                    }
                    
                    // Если выбранный язык не является языком по умолчанию (английский), добавляем префикс
                    if (selectedLang !== 'en') {
                        newPath = '/' + selectedLang + currentPath;
                    } else {
                        newPath = currentPath;
                    }
                    
                    // Перенаправляем на новый URL
                    window.location.href = newPath;
                });
            });
        }
    });
}

// Функция для анимации числовых счетчиков
function animateCounters() {
    const counters = document.querySelectorAll('.counter-value');
    if (!counters.length) return;
    
    let animated = false;
    
    // Функция проверки видимости элементов
    function checkCountersVisibility() {
        // Проверяем, видимы ли счетчики в области просмотра
        if (!animated && isElementInViewport(counters[0])) {
            animated = true; // Отмечаем, что анимация запущена
            
            counters.forEach(counter => {
                // Получаем целевое значение из атрибута 
                const target = parseInt(counter.getAttribute('data-target') || '0');
                const duration = 1500; // Длительность анимации в миллисекундах
                
                // Начальное значение
                let start = 0;
                // Время начала анимации
                const startTime = performance.now();
                
                // Функция анимации
                function animate(currentTime) {
                    // Прошедшее время с начала анимации
                    const elapsedTime = currentTime - startTime;
                    // Прогресс анимации (от 0 до 1)
                    const progress = Math.min(elapsedTime / duration, 1);
                    
                    // Расчет текущего значения с эффектом замедления в конце
                    const value = Math.floor(progress * target);
                    
                    // Обновляем текст счетчика
                    counter.textContent = value.toLocaleString();
                    
                    // Если анимация не завершена, запрашиваем следующий кадр
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        // Финальное значение для уверенности
                        counter.textContent = target.toLocaleString();
                    }
                }
                
                // Запускаем анимацию
                requestAnimationFrame(animate);
            });
        }
    }
    
    // Запускаем проверку при загрузке и прокрутке страницы
    checkCountersVisibility();
    window.addEventListener('scroll', checkCountersVisibility);
}

// Вспомогательная функция для проверки видимости элемента
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Функция для обработки переключения типа метода оплаты
function handlePaymentMethodToggle() {
    const methodSelector = document.querySelector('.method-type-select');
    if (!methodSelector) return;
    
    const toggleFields = (value) => {
        const cardFields = document.querySelectorAll('.card-field');
        const bankFields = document.querySelectorAll('.bank-field');
        
        if (value === 'card') {
            cardFields.forEach(field => field.closest('.mb-3').style.display = 'block');
            bankFields.forEach(field => field.closest('.mb-3').style.display = 'none');
        } else if (value === 'bank') {
            cardFields.forEach(field => field.closest('.mb-3').style.display = 'none');
            bankFields.forEach(field => field.closest('.mb-3').style.display = 'block');
        } else {
            cardFields.forEach(field => field.closest('.mb-3').style.display = 'none');
            bankFields.forEach(field => field.closest('.mb-3').style.display = 'none');
        }
    };
    
    // Начальное состояние
    toggleFields(methodSelector.value);
    
    // Обработка изменений
    methodSelector.addEventListener('change', (e) => {
        toggleFields(e.target.value);
    });
}

// Функция для инициализации фильтров для списка проектов
function initProjectFilters() {
    const filterForm = document.getElementById('project-filter-form');
    if (!filterForm) return;
    
    const applyFilters = () => {
        filterForm.submit();
    };
    
    // Применяем фильтры при изменении селекторов
    const selects = filterForm.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', applyFilters);
    });
    
    // Применяем фильтры при нажатии на чекбоксы
    const checkboxes = filterForm.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
}

// Функция для обработки динамического добавления полей этапов в контрактах
function initMilestoneFormset() {
    const addBtn = document.getElementById('add-milestone');
    if (!addBtn) return;
    
    const formsetContainer = document.getElementById('milestone-formset');
    const totalForms = document.getElementById('id_milestone_set-TOTAL_FORMS');
    
    addBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        const formCount = parseInt(totalForms.value);
        
        // Клонируем первую форму
        const emptyForm = document.querySelector('.milestone-form').cloneNode(true);
        
        // Обновляем индексы в id и name атрибутах
        emptyForm.innerHTML = emptyForm.innerHTML.replace(/-0-/g, `-${formCount}-`);
        emptyForm.innerHTML = emptyForm.innerHTML.replace(/_0_/g, `_${formCount}_`);
        
        // Очищаем значения полей
        const inputs = emptyForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.value = '';
        });
        
        // Добавляем новую форму в контейнер
        formsetContainer.appendChild(emptyForm);
        
        // Увеличиваем счетчик форм
        totalForms.value = formCount + 1;
    });
}

// Функция для инициализации чата через веб-сокеты
function initChatWebSocket() {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;
    
    const conversationId = chatContainer.getAttribute('data-conversation-id');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-message');
    
    // Создаем WebSocket соединение
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const chatSocket = new WebSocket(
        `${wsProtocol}${window.location.host}/ws/chat/${conversationId}/`
    );
    
    // Обработка входящих сообщений
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        addMessageToChat(data.message, data.sender_id, data.sender_username, data.timestamp);
        
        // Прокручиваем чат вниз
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };
    
    // Обработка закрытия соединения
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };
    
    // Отправка сообщения при нажатии на кнопку
    sendBtn.addEventListener('click', function() {
        sendMessage();
    });
    
    // Отправка сообщения при нажатии Enter
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Функция отправки сообщения
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        }
    }
    
    // Функция добавления сообщения в чат
    function addMessageToChat(message, senderId, senderUsername, timestamp) {
        const currentUserId = chatContainer.getAttribute('data-user-id');
        const isSent = senderId.toString() === currentUserId.toString();
        
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isSent ? 'sent' : 'received');
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('content');
        
        if (!isSent) {
            const senderElement = document.createElement('div');
            senderElement.classList.add('sender');
            senderElement.textContent = senderUsername;
            messageContent.appendChild(senderElement);
        }
        
        const textElement = document.createElement('div');
        textElement.classList.add('text');
        textElement.textContent = message;
        messageContent.appendChild(textElement);
        
        const timeElement = document.createElement('div');
        timeElement.classList.add('time');
        
        const date = new Date(timestamp);
        timeElement.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageContent.appendChild(timeElement);
        messageElement.appendChild(messageContent);
        
        chatContainer.appendChild(messageElement);
    }
    
    // Прокручиваем чат вниз при инициализации
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Функция для обновления количества непрочитанных сообщений/уведомлений
function updateUnreadCounters() {
    // Эта функция отключена по требованию заказчика
    return;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация компонентов Bootstrap
    initTooltips();
    initPopovers();
    
    // Инициализация пользовательских функций
    initLanguageForms();
    animateCounters();
    handlePaymentMethodToggle();
    initProjectFilters();
    initMilestoneFormset();
    initChatWebSocket();
    initFlatpickr(); // Инициализация улучшенного выбора даты
    enhanceProposalForm(); // Улучшаем форму отправки предложений
    
    // Обновление счетчиков непрочитанных сообщений и уведомлений
    updateUnreadCounters();
    
    // Закрываем мобильное меню при клике на ссылку
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const menuToggle = document.getElementById('navbarSupportedContent');
    const bsCollapse = menuToggle ? new bootstrap.Collapse(menuToggle, {toggle: false}) : null;
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Проверяем, открыто ли меню и видим ли toggle (мобильный режим)
            if (menuToggle && menuToggle.classList.contains('show') && window.getComputedStyle(document.querySelector('.navbar-toggler')).display !== 'none') {
                bsCollapse.hide();
            }
        });
    });
});

// WorkBy Main JavaScript

document.addEventListener('DOMContentLoaded', function() {


    // Инициализация всплывающих подсказок
    initializeTooltips();
    
    // Обработка формы поиска
    setupSearchForm();
    
    // Анимации появления элементов
    animateElements();
});



// Инициализация всплывающих подсказок Bootstrap
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            container: 'body',
            trigger: 'hover'
        });
    });
}

// Настройка формы поиска
function setupSearchForm() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[type="search"]');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
}

// Анимация появления элементов при прокрутке
function animateElements() {
    const animatedElements = document.querySelectorAll('.fade-in');
    
    if (animatedElements.length > 0) {
        // Функция проверки, видны ли элементы
        function checkVisible() {
            animatedElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                const windowHeight = window.innerHeight || document.documentElement.clientHeight;
                
                if (rect.top <= windowHeight * 0.8) {
                    element.classList.add('visible');
                }
            });
        }
        
        // Первичная проверка
        checkVisible();
        
        // Проверка при прокрутке
        window.addEventListener('scroll', checkVisible);
    }
}

// Функция для форматирования денежных значений
function formatCurrency(amount, currency = '₸') {
    return amount.toLocaleString('ru-KZ') + ' ' + currency;
}

// Функция для определения активного раздела меню
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath || currentPath.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });
}

// Обработчик для автоматического увеличения размера текстового поля
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
}

// Функция для генерации аватара с инициалами
function generateInitialsAvatar(name, size = 40, bgColor = '#8B0000') {
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const context = canvas.getContext('2d');
    
    // Рисуем фон
    context.fillStyle = bgColor;
    context.beginPath();
    context.arc(size/2, size/2, size/2, 0, Math.PI * 2);
    context.fill();
    
    // Получаем инициалы
    const nameParts = name.split(' ');
    let initials = '';
    
    if (nameParts.length >= 2) {
        initials = nameParts[0].charAt(0) + nameParts[1].charAt(0);
    } else if (nameParts.length === 1) {
        initials = nameParts[0].charAt(0);
    } else {
        initials = '?';
    }
    
    // Рисуем текст
    context.fillStyle = 'white';
    context.font = `bold ${size/2}px Arial`;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(initials.toUpperCase(), size/2, size/2);
    
    return canvas.toDataURL();
}

// Инициализация улучшенного выбора даты
function initFlatpickr() {
    // Проверяем наличие библиотеки flatpickr
    if (typeof flatpickr === 'undefined') {
        // Если библиотека не найдена, подключаем ее
        const head = document.querySelector('head');
        
        // Подключаем стили
        const linkCSS = document.createElement('link');
        linkCSS.rel = 'stylesheet';
        linkCSS.href = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css';
        head.appendChild(linkCSS);
        
        // Подключаем локализацию для русского языка
        const scriptRu = document.createElement('script');
        scriptRu.src = 'https://npmcdn.com/flatpickr/dist/l10n/ru.js';
        head.appendChild(scriptRu);
        
        // Подключаем скрипт
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/flatpickr';
        script.onload = function() {
            // Ждем загрузки локализации
            setTimeout(initDatepickers, 100);
        };
        head.appendChild(script);
    } else {
        // Если библиотека уже подключена, инициализируем все поля выбора даты
        initDatepickers();
    }
}

// Инициализация всех полей выбора даты
function initDatepickers() {
    // Настройки по умолчанию
    const dateConfig = {
        dateFormat: "Y-m-d",
        enableTime: false,
        altInput: true,
        altFormat: "d M Y",
        disableMobile: true, // Отключаем нативные элементы на мобильных
        locale: "ru",
        allowInput: true,
        position: "auto"
    };
    
    // Инициализация полей с типом date
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Сохраняем текущее значение поля
        const currentValue = input.value;
        
        // Создаем скрытое поле для хранения исходного значения
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = input.name;
        hiddenInput.value = currentValue;
        input.parentNode.insertBefore(hiddenInput, input.nextSibling);
        
        // Изменяем тип поля и удаляем name атрибут, чтобы избежать дублирования
        input.type = 'text';
        input.removeAttribute('name');
        input.classList.add('flatpickr-input');
        
        // Инициализируем flatpickr и привязываем обновление скрытого поля
        const fp = flatpickr(input, {
            ...dateConfig,
            defaultDate: currentValue || null,
            onChange: function(selectedDates, dateStr) {
                hiddenInput.value = dateStr;
            }
        });
    });
    
    // Настройки для полей дата-время
    const dateTimeConfig = {
        ...dateConfig,
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        altFormat: "d M Y, H:i",
        time_24hr: true
    };
    
    // Инициализация полей с типом datetime-local
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateTimeInputs.forEach(input => {
        // Сохраняем текущее значение поля
        const currentValue = input.value;
        
        // Создаем скрытое поле для хранения исходного значения
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = input.name;
        hiddenInput.value = currentValue;
        input.parentNode.insertBefore(hiddenInput, input.nextSibling);
        
        // Изменяем тип поля и удаляем name атрибут
        input.type = 'text';
        input.removeAttribute('name');
        input.classList.add('flatpickr-input');
        
        // Инициализируем flatpickr
        const fp = flatpickr(input, {
            ...dateTimeConfig,
            defaultDate: currentValue || null,
            onChange: function(selectedDates, dateStr) {
                hiddenInput.value = dateStr;
            }
        });
    });
    
    // Находим все поля даты, которые использует Django admin
    const djangoDateInputs = document.querySelectorAll('.vDateField, input[name*="date"]:not([type="hidden"])');
    djangoDateInputs.forEach(input => {
        if (input.type !== 'date' && input.type !== 'datetime-local' && !input.classList.contains('flatpickr-input')) {
            flatpickr(input, input.classList.contains('vTimeField') ? dateTimeConfig : dateConfig);
        }
    });
    
    // Запускаем обработчик для Bootstrap datepicker если он используется
    const bootstrapDatepickers = document.querySelectorAll('.datepicker');
    if (bootstrapDatepickers.length > 0 && typeof $.fn !== 'undefined' && typeof $.fn.datepicker !== 'undefined') {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true,
            language: 'ru'
        });
    }
}

// Улучшение формы отправки предложений 
function enhanceProposalForm() {
    const proposalForm = document.querySelector('form[action*="proposal"]');
    if (!proposalForm) return;

    // Стилизуем поля формы
    const bidInput = proposalForm.querySelector('#id_bid_amount');
    const deliverySelect = proposalForm.querySelector('#id_delivery_time');
    
    if (bidInput) {
        // Добавляем подсветку при вводе суммы
        bidInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value > 0) {
                this.classList.add('border-primary');
            } else {
                this.classList.remove('border-primary');
            }
        });
    }
    
    if (deliverySelect) {
        // Добавляем подсветку при выборе срока
        deliverySelect.addEventListener('change', function() {
            this.classList.add('border-primary');
        });
    }

    // Обрабатываем отправку формы
    proposalForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Скрываем сообщения об ошибках
        const errorElements = proposalForm.querySelectorAll('.invalid-feedback');
        errorElements.forEach(el => el.remove());
        
        proposalForm.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        
        // Показываем индикатор загрузки на кнопке
        const submitBtn = proposalForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Отправка...';
        submitBtn.disabled = true;
        
        // Получаем токен CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Отправляем форму с помощью AJAX
        const formData = new FormData(proposalForm);
        
        fetch(proposalForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Показываем сообщение об успехе
                showNotification('success', data.message || 'Предложение успешно отправлено!');
                
                // Перенаправляем на страницу проекта или предложения
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1000);
            } else {
                // Обрабатываем ошибки
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.errors) {
                    // Показываем ошибки валидации формы
                    Object.keys(data.errors).forEach(field => {
                        const input = proposalForm.querySelector(`#id_${field}`);
                        if (input) {
                            input.classList.add('is-invalid');
                            const errorMsg = document.createElement('div');
                            errorMsg.className = 'invalid-feedback d-block';
                            errorMsg.textContent = data.errors[field][0];
                            input.parentNode.appendChild(errorMsg);
                        }
                    });
                } else {
                    // Общая ошибка
                    showNotification('error', data.message || 'Произошла ошибка при отправке предложения.');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            showNotification('error', 'Произошла ошибка при отправке. Попробуйте еще раз.');
        });
    });
}

/**
 * Показывает всплывающее уведомление
 * @param {string} type - тип уведомления (success, error, warning, info)
 * @param {string} message - текст сообщения
 * @param {number} duration - длительность отображения в миллисекундах
 */
function showNotification(type, message, duration = 3000) {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `toast toast-${type} show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.minWidth = '250px';
    notification.style.zIndex = '9999';
    notification.style.backgroundColor = type === 'success' ? '#198754' : 
                                        type === 'error' ? '#dc3545' : 
                                        type === 'warning' ? '#ffc107' : '#0dcaf0';
    notification.style.color = ['warning', 'info'].includes(type) ? '#000' : '#fff';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '5px';
    notification.style.boxShadow = '0 3px 15px rgba(0, 0, 0, 0.3)';
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    notification.style.transition = 'all 0.3s ease';
    
    // Добавляем иконку в зависимости от типа уведомления
    let icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle me-2"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle me-2"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle me-2"></i>';
            break;
        case 'info':
            icon = '<i class="fas fa-info-circle me-2"></i>';
            break;
    }
    
    notification.innerHTML = icon + message;
    
    // Добавляем уведомление в DOM
    document.body.appendChild(notification);
    
    // Показываем уведомление с анимацией
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Скрываем уведомление через указанное время
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        
        // Удаляем элемент после завершения анимации
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, duration);
}

// Инициализация всех функций при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех всплывающих подсказок
    initTooltips();
    
    // Инициализация датапикеров
    initDatepickers();
    
    // Улучшение формы отправки предложения
    enhanceProposalForm();
    
    // Инициализация прочих компонентов интерфейса
    initNotifications();
    initContractFunctions();
    initChatComponents();
    
    console.log('WorkBy App initialized successfully');
});

/**
 * Инициализирует систему уведомлений
 */
function initNotifications() {
    // Обрабатываем отметку уведомлений как прочитанных
    const notificationLinks = document.querySelectorAll('.notification-item');
    if (notificationLinks) {
        notificationLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const notificationId = this.dataset.notificationId;
                if (notificationId) {
                    // Можно отправить AJAX-запрос для отметки уведомления как прочитанного
                    fetch(`/notifications/mark-as-read/${notificationId}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                            'Content-Type': 'application/json'
                        }
                    }).then(response => {
                        if (response.ok) {
                            // Обновляем счетчик непрочитанных уведомлений
                            const counter = document.querySelector('.notification-counter');
                            if (counter) {
                                const count = parseInt(counter.textContent) - 1;
                                counter.textContent = count > 0 ? count : '';
                                if (count <= 0) {
                                    counter.classList.add('d-none');
                                }
                            }
                        }
                    });
                }
            });
        });
    }
}

/**
 * Инициализирует функции для контрактов
 */
function initContractFunctions() {
    // Функционал для страницы контракта
    const contractTimeline = document.querySelector('.contract-timeline');
    if (contractTimeline) {
        // Анимация временной линии контракта
        contractTimeline.querySelectorAll('.timeline-item').forEach((item, index) => {
            setTimeout(() => {
                item.classList.add('show');
            }, 100 * (index + 1));
        });
    }
}

/**
 * Инициализирует компоненты чата
 */
function initChatComponents() {
    // Компоненты чата
    const chatContainer = document.getElementById('chat-messages');
    if (chatContainer) {
        // Прокрутка чата вниз при загрузке
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Обработка отправки сообщения
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const messageInput = this.querySelector('textarea[name="message"]');
                const message = messageInput.value.trim();
                
                if (message) {
                    // Очищаем поле ввода
                    messageInput.value = '';
                    
                    // В реальном приложении здесь должен быть код для отправки сообщения через WebSocket
                    // и добавления его в чат после успешной отправки
                }
            });
        }
    }
} 