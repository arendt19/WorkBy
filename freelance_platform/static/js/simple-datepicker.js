/**
 * Простой и надежный выбор даты и времени
 * Без зависимостей, минимальный код
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Инициализация простого календаря...');
    
    // Находим элемент для выбора даты
    const dateInput = document.getElementById('deadline_picker');
    
    if (!dateInput) {
        console.error('Поле для выбора даты не найдено!');
        return;
    }
    
    console.log('Поле для выбора даты найдено:', dateInput);
    
    // Создаем модальное окно для выбора даты
    const createDatePicker = function() {
        // Удаляем существующий календарь, если есть
        const existingPicker = document.getElementById('simple-date-picker');
        if (existingPicker) {
            document.body.removeChild(existingPicker);
        }
        
        // Определяем текущую дату
        const now = new Date();
        let selectedDate = dateInput.value ? parseDate(dateInput.value) : now;
        let currentMonth = selectedDate.getMonth();
        let currentYear = selectedDate.getFullYear();
        let selectedHours = selectedDate.getHours();
        let selectedMinutes = selectedDate.getMinutes();
        
        // Создаем контейнер календаря
        const pickerContainer = document.createElement('div');
        pickerContainer.id = 'simple-date-picker';
        pickerContainer.className = 'date-picker-modal';
        
        // Добавляем содержимое календаря
        pickerContainer.innerHTML = `
            <div class="date-picker-content">
                <div class="date-picker-header">
                    <div class="date-picker-title">Выберите дату и время</div>
                    <div class="date-picker-close">&times;</div>
                </div>
                <div class="date-picker-body">
                    <div class="date-picker-month-selector">
                        <button class="date-picker-prev" id="prev-month">&lt;</button>
                        <div class="date-picker-current-month" id="current-month"></div>
                        <button class="date-picker-next" id="next-month">&gt;</button>
                    </div>
                    <div class="date-picker-calendar" id="calendar"></div>
                    <div class="date-picker-time">
                        <div class="date-picker-time-label">Время:</div>
                        <div class="date-picker-time-selector">
                            <select id="hour-select"></select>
                            <span>:</span>
                            <select id="minute-select"></select>
                        </div>
                    </div>
                    <div class="date-picker-actions">
                        <button class="date-picker-cancel">Отмена</button>
                        <button class="date-picker-confirm">ОК</button>
                    </div>
                </div>
            </div>
        `;
        
        // Добавляем календарь в DOM
        document.body.appendChild(pickerContainer);
        
        // Обновляем заголовок месяца
        const updateMonthYear = function() {
            const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
            document.getElementById('current-month').textContent = `${months[currentMonth]} ${currentYear}`;
        };
        
        // Генерируем календарь
        const renderCalendar = function() {
            const calendarDiv = document.getElementById('calendar');
            calendarDiv.innerHTML = '';
            
            // Добавляем дни недели
            const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
            weekdays.forEach(day => {
                const dayElement = document.createElement('div');
                dayElement.className = 'date-picker-weekday';
                dayElement.textContent = day;
                calendarDiv.appendChild(dayElement);
            });
            
            // Получаем первый день месяца
            const firstDay = new Date(currentYear, currentMonth, 1);
            let weekDay = firstDay.getDay() || 7; // Преобразуем 0 (воскресенье) в 7
            
            // Получаем количество дней в месяце
            const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
            
            // Добавляем пустые ячейки для дней перед первым днем месяца
            for (let i = 1; i < weekDay; i++) {
                const emptyDay = document.createElement('div');
                emptyDay.className = 'date-picker-day empty';
                calendarDiv.appendChild(emptyDay);
            }
            
            // Добавляем дни месяца
            const today = new Date();
            for (let day = 1; day <= daysInMonth; day++) {
                const dayElement = document.createElement('div');
                dayElement.className = 'date-picker-day';
                dayElement.textContent = day;
                
                // Выделяем сегодняшний день
                if (day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()) {
                    dayElement.classList.add('today');
                }
                
                // Выделяем выбранный день
                if (day === selectedDate.getDate() && currentMonth === selectedDate.getMonth() && currentYear === selectedDate.getFullYear()) {
                    dayElement.classList.add('selected');
                }
                
                // Обработчик клика по дню
                dayElement.addEventListener('click', function() {
                    // Снимаем выделение с предыдущего выбранного дня
                    const selectedDay = document.querySelector('.date-picker-day.selected');
                    if (selectedDay) {
                        selectedDay.classList.remove('selected');
                    }
                    
                    // Выделяем новый выбранный день
                    this.classList.add('selected');
                    
                    // Обновляем выбранную дату
                    selectedDate = new Date(currentYear, currentMonth, day, selectedHours, selectedMinutes);
                });
                
                calendarDiv.appendChild(dayElement);
            }
        };
        
        // Заполняем селекты для часов и минут
        const populateTimeSelects = function() {
            const hourSelect = document.getElementById('hour-select');
            const minuteSelect = document.getElementById('minute-select');
            
            // Заполняем часы (0-23)
            for (let i = 0; i < 24; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i < 10 ? `0${i}` : i;
                if (i === selectedHours) {
                    option.selected = true;
                }
                hourSelect.appendChild(option);
            }
            
            // Заполняем минуты (0-59, шаг 5)
            for (let i = 0; i < 60; i += 5) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i < 10 ? `0${i}` : i;
                if (i === Math.floor(selectedMinutes / 5) * 5) {
                    option.selected = true;
                }
                minuteSelect.appendChild(option);
            }
            
            // Обработчики изменения времени
            hourSelect.addEventListener('change', function() {
                selectedHours = parseInt(this.value);
                selectedDate.setHours(selectedHours);
            });
            
            minuteSelect.addEventListener('change', function() {
                selectedMinutes = parseInt(this.value);
                selectedDate.setMinutes(selectedMinutes);
            });
        };
        
        // Инициализация календаря
        updateMonthYear();
        renderCalendar();
        populateTimeSelects();
        
        // Обработчики навигации по месяцам
        document.getElementById('prev-month').addEventListener('click', function() {
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            updateMonthYear();
            renderCalendar();
        });
        
        document.getElementById('next-month').addEventListener('click', function() {
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            updateMonthYear();
            renderCalendar();
        });
        
        // Обработчик подтверждения выбора даты
        document.querySelector('.date-picker-confirm').addEventListener('click', function() {
            // Форматируем дату в формат YYYY-MM-DD HH:mm
            const formattedDate = formatDate(selectedDate);
            dateInput.value = formattedDate;
            
            // Закрываем календарь
            document.body.removeChild(pickerContainer);
            
            // Вызываем событие изменения для поля ввода
            const event = new Event('change', { bubbles: true });
            dateInput.dispatchEvent(event);
        });
        
        // Обработчики закрытия календаря
        document.querySelector('.date-picker-close').addEventListener('click', function() {
            document.body.removeChild(pickerContainer);
        });
        
        document.querySelector('.date-picker-cancel').addEventListener('click', function() {
            document.body.removeChild(pickerContainer);
        });
        
        // Закрытие при клике вне календаря
        pickerContainer.addEventListener('click', function(e) {
            if (e.target === pickerContainer) {
                document.body.removeChild(pickerContainer);
            }
        });
    };
    
    // Функция для разбора строки даты
    const parseDate = function(dateString) {
        if (!dateString) return new Date();
        
        try {
            // Попытка разобрать строку формата YYYY-MM-DD HH:mm
            const parts = dateString.split(' ');
            const dateParts = parts[0].split('-');
            let timeParts = ['00', '00'];
            
            if (parts.length > 1 && parts[1].includes(':')) {
                timeParts = parts[1].split(':');
            }
            
            const year = parseInt(dateParts[0], 10);
            const month = parseInt(dateParts[1], 10) - 1;
            const day = parseInt(dateParts[2], 10);
            const hours = parseInt(timeParts[0], 10);
            const minutes = parseInt(timeParts[1], 10);
            
            return new Date(year, month, day, hours, minutes);
        } catch (e) {
            console.error('Ошибка при разборе даты:', e);
            return new Date();
        }
    };
    
    // Функция для форматирования даты
    const formatDate = function(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    };
    
    // Добавляем обработчик клика на поле даты
    dateInput.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Клик по полю даты');
        createDatePicker();
    });
    
    // Добавляем обработчик клика на иконку календаря
    const calendarIcon = document.querySelector('label[for="deadline_picker"] i.bi-calendar');
    if (calendarIcon) {
        calendarIcon.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Клик по иконке календаря');
            createDatePicker();
        });
    }
    
    console.log('Простой календарь успешно инициализирован');
});
