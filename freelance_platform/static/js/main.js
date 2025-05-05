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
        return new bootstrap.Tooltip(tooltipTriggerEl);
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

    // Создаем элемент для отображения всплывающего уведомления
    const confirmationDiv = document.createElement('div');
    confirmationDiv.className = 'proposal-confirmation';
    confirmationDiv.innerHTML = '<i class="fas fa-check-circle me-2"></i> Предложение успешно отправлено!';
    document.body.appendChild(confirmationDiv);

    // Создаем элемент для отображения ошибок
    const errorDiv = document.createElement('div');
    errorDiv.className = 'proposal-error';
    errorDiv.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i> Ошибка при отправке предложения';
    document.body.appendChild(errorDiv);

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
        .then(response => {
            if (response.ok) {
                return response.json().then(data => {
                    // Показываем уведомление об успешной отправке
                    confirmationDiv.classList.add('show');
                    
                    // Скрываем уведомление через 3 секунды
                    setTimeout(() => {
                        confirmationDiv.classList.add('hide');
                        
                        // После завершения анимации скрытия, перенаправляем на страницу my_proposals
                        setTimeout(() => {
                            if (data.redirect_url) {
                                window.location.href = data.redirect_url;
                            } else {
                                window.location.href = '/jobs/my-proposals/';
                            }
                        }, 300);
                    }, 3000);
                });
            } else {
                // Обрабатываем ошибки
                return response.json().then(errorData => {
                    // Возвращаем кнопку в исходное состояние
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                    
                    // Проверяем, есть ли ошибки валидации формы
                    if (errorData.errors) {
                        try {
                            const errors = JSON.parse(errorData.errors);
                            
                            // Отображаем ошибки в соответствующих полях
                            Object.keys(errors).forEach(fieldName => {
                                const field = proposalForm.querySelector(`[name="${fieldName}"]`);
                                if (field) {
                                    field.classList.add('is-invalid');
                                    
                                    // Создаем элемент с сообщением об ошибке
                                    const errorMessage = document.createElement('div');
                                    errorMessage.className = 'invalid-feedback';
                                    errorMessage.textContent = errors[fieldName][0].message;
                                    
                                    // Добавляем сообщение после поля
                                    field.parentNode.appendChild(errorMessage);
                                }
                            });
                        } catch (e) {
                            // Если не удалось разобрать JSON с ошибками, показываем общее сообщение
                            errorDiv.textContent = 'Пожалуйста, проверьте правильность заполнения формы';
                            errorDiv.classList.add('show');
                            
                            setTimeout(() => {
                                errorDiv.classList.remove('show');
                            }, 5000);
                        }
                    } else {
                        // Показываем общее сообщение об ошибке
                        errorDiv.classList.add('show');
                        
                        setTimeout(() => {
                            errorDiv.classList.remove('show');
                        }, 5000);
                    }
                }).catch(() => {
                    // Если не удалось получить JSON с ошибками
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                    
                    errorDiv.classList.add('show');
                    setTimeout(() => {
                        errorDiv.classList.remove('show');
                    }, 5000);
                });
            }
        })
        .catch(error => {
            // Возвращаем кнопку в исходное состояние
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            
            // Показываем ошибку
            console.error('Error:', error);
            errorDiv.classList.add('show');
            setTimeout(() => {
                errorDiv.classList.remove('show');
            }, 5000);
        });
    });
} 