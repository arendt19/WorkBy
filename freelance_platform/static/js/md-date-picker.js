/**
 * Material Design Date Time Picker
 * Реализация на чистом JavaScript без зависимостей
 */

class MDDatePicker {
  constructor(options = {}) {
    // Настройки по умолчанию
    this.options = {
      targetInput: null,          // Элемент ввода для даты
      format: 'YYYY-MM-DD HH:mm', // Формат даты
      language: 'ru',             // Язык
      minDate: null,              // Минимальная дата
      maxDate: null,              // Максимальная дата
      okText: 'ОК',               // Текст кнопки ОК
      cancelText: 'Отмена',       // Текст кнопки Отмена
      timeFormat: '24h',          // Формат времени (12h или 24h)
      ...options
    };

    // Локализация
    this.locales = {
      ru: {
        months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
        monthsShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
        weekdays: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
        weekdaysShort: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
        today: 'Сегодня'
      },
      en: {
        months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        weekdays: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        weekdaysShort: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        today: 'Today'
      }
    };

    // Текущий язык
    this.locale = this.locales[this.options.language] || this.locales.en;

    // Текущая дата
    this.currentDate = new Date();
    
    // Установка выбранной даты (если есть в поле ввода)
    if (this.options.targetInput && this.options.targetInput.value) {
      const dateValue = this.options.targetInput.value;
      if (dateValue) {
        this.selectedDate = this.parseDate(dateValue);
      } else {
        this.selectedDate = new Date();
      }
    } else {
      this.selectedDate = new Date();
    }
    
    // Текущее представление (дата или время)
    this.currentView = 'date';
    
    // Текущий режим времени (часы или минуты)
    this.timeMode = 'hours';
    
    // Создание элементов календаря
    this.createElements();
    
    // Инициализация обработчиков событий
    this.initEvents();
  }

  /**
   * Создание HTML-элементов календаря
   */
  createElements() {
    // Главный контейнер
    this.element = document.createElement('div');
    this.element.className = 'md-date-picker';
    
    // Карточка календаря
    this.card = document.createElement('div');
    this.card.className = 'md-date-card';
    
    // Шапка календаря
    this.header = document.createElement('div');
    this.header.className = 'md-date-header';
    
    this.yearElement = document.createElement('div');
    this.yearElement.className = 'md-date-year';
    
    this.dayMonthElement = document.createElement('div');
    this.dayMonthElement.className = 'md-date-month-day';
    
    this.header.appendChild(this.yearElement);
    this.header.appendChild(this.dayMonthElement);
    
    // Селектор года
    this.yearSelector = document.createElement('div');
    this.yearSelector.className = 'md-year-selector';
    
    this.yearList = document.createElement('ul');
    this.yearList.className = 'md-year-list';
    
    this.yearSelector.appendChild(this.yearList);
    
    // Контент календаря
    this.content = document.createElement('div');
    this.content.className = 'md-date-content';
    
    // Навигация по месяцам
    this.navigation = document.createElement('div');
    this.navigation.className = 'md-date-navigation';
    
    this.prevBtn = document.createElement('div');
    this.prevBtn.className = 'md-date-prev';
    
    this.titleElement = document.createElement('div');
    this.titleElement.className = 'md-date-title';
    
    this.nextBtn = document.createElement('div');
    this.nextBtn.className = 'md-date-next';
    
    this.navigation.appendChild(this.prevBtn);
    this.navigation.appendChild(this.titleElement);
    this.navigation.appendChild(this.nextBtn);
    
    // Дни недели
    this.weekdaysElement = document.createElement('div');
    this.weekdaysElement.className = 'md-date-weekdays';
    
    // Дни месяца
    this.daysElement = document.createElement('div');
    this.daysElement.className = 'md-date-days';
    
    this.content.appendChild(this.navigation);
    this.content.appendChild(this.weekdaysElement);
    this.content.appendChild(this.daysElement);
    
    // Контейнер для выбора времени
    this.timeContainer = document.createElement('div');
    this.timeContainer.className = 'md-time-container';
    
    // Отображение времени
    this.timeContent = document.createElement('div');
    this.timeContent.className = 'md-time-content';
    
    this.hoursElement = document.createElement('div');
    this.hoursElement.className = 'md-time-hours md-time-active';
    
    this.separatorElement = document.createElement('div');
    this.separatorElement.className = 'md-time-separator';
    this.separatorElement.textContent = ':';
    
    this.minutesElement = document.createElement('div');
    this.minutesElement.className = 'md-time-minutes';
    
    this.timeContent.appendChild(this.hoursElement);
    this.timeContent.appendChild(this.separatorElement);
    this.timeContent.appendChild(this.minutesElement);
    
    // Циферблат
    this.clockElement = document.createElement('div');
    this.clockElement.className = 'md-time-clock';
    
    this.clockHandElement = document.createElement('div');
    this.clockHandElement.className = 'md-clock-hand';
    
    this.clockCenterElement = document.createElement('div');
    this.clockCenterElement.className = 'md-clock-center';
    
    this.clockElement.appendChild(this.clockHandElement);
    this.clockElement.appendChild(this.clockCenterElement);
    
    this.timeContainer.appendChild(this.timeContent);
    this.timeContainer.appendChild(this.clockElement);
    
    // Кнопки действий
    this.actions = document.createElement('div');
    this.actions.className = 'md-date-actions';
    
    this.cancelBtn = document.createElement('button');
    this.cancelBtn.className = 'md-date-btn md-date-cancel';
    this.cancelBtn.textContent = this.options.cancelText;
    
    this.okBtn = document.createElement('button');
    this.okBtn.className = 'md-date-btn md-date-ok';
    this.okBtn.textContent = this.options.okText;
    
    this.actions.appendChild(this.cancelBtn);
    this.actions.appendChild(this.okBtn);
    
    // Добавление элементов в карточку
    this.card.appendChild(this.header);
    this.card.appendChild(this.yearSelector);
    this.card.appendChild(this.content);
    this.card.appendChild(this.timeContainer);
    this.card.appendChild(this.actions);
    
    this.element.appendChild(this.card);
    
    // Добавление в DOM
    document.body.appendChild(this.element);
    
    // Обновление содержимого
    this.updateView();
  }

  /**
   * Инициализация обработчиков событий
   */
  initEvents() {
    // Открытие календаря при клике на поле ввода
    if (this.options.targetInput) {
      this.options.targetInput.addEventListener('click', () => {
        this.open();
      });
      
      // Открытие календаря при клике на иконку календаря (если есть)
      const label = document.querySelector(`label[for="${this.options.targetInput.id}"]`);
      if (label) {
        const calendarIcon = label.querySelector('i.bi-calendar');
        if (calendarIcon) {
          calendarIcon.addEventListener('click', (e) => {
            e.preventDefault();
            this.open();
          });
        }
      }
    }
    
    // Закрытие при клике на фон
    this.element.addEventListener('click', (e) => {
      if (e.target === this.element) {
        this.close();
      }
    });
    
    // Переключение между годом и датой
    this.yearElement.addEventListener('click', () => {
      this.yearSelector.classList.add('active');
      this.scrollToSelectedYear();
    });
    
    this.dayMonthElement.addEventListener('click', () => {
      this.yearSelector.classList.remove('active');
    });
    
    // Навигация по месяцам
    this.prevBtn.addEventListener('click', () => {
      this.prevMonth();
    });
    
    this.nextBtn.addEventListener('click', () => {
      this.nextMonth();
    });
    
    // Кнопки действий
    this.cancelBtn.addEventListener('click', () => {
      this.close();
    });
    
    this.okBtn.addEventListener('click', () => {
      this.confirm();
    });
    
    // Переключение между временем и датой
    this.hoursElement.addEventListener('click', () => {
      this.setTimeMode('hours');
    });
    
    this.minutesElement.addEventListener('click', () => {
      this.setTimeMode('minutes');
    });
  }

  /**
   * Открытие календаря
   */
  open() {
    this.element.classList.add('active');
    this.updateView();
    
    // Обновляем выбранную дату из поля ввода
    if (this.options.targetInput && this.options.targetInput.value) {
      const dateValue = this.options.targetInput.value;
      if (dateValue) {
        this.selectedDate = this.parseDate(dateValue);
        this.currentDate = new Date(this.selectedDate);
      }
    }
    
    // Обновляем представление
    this.renderCalendar();
    this.renderClock();
    this.updateHeader();
  }

  /**
   * Закрытие календаря
   */
  close() {
    this.element.classList.remove('active');
  }

  /**
   * Подтверждение выбора даты
   */
  confirm() {
    if (this.options.targetInput) {
      this.options.targetInput.value = this.formatDate(this.selectedDate);
      
      // Вызываем событие change
      const event = new Event('change', { bubbles: true });
      this.options.targetInput.dispatchEvent(event);
    }
    
    this.close();
  }

  /**
   * Обновление представления в зависимости от режима
   */
  updateView() {
    if (this.currentView === 'date') {
      this.content.style.display = 'block';
      this.timeContainer.classList.remove('active');
      this.renderCalendar();
    } else {
      this.content.style.display = 'none';
      this.timeContainer.classList.add('active');
      this.renderClock();
    }
    
    this.updateHeader();
  }

  /**
   * Обновление заголовка
   */
  updateHeader() {
    const year = this.selectedDate.getFullYear();
    const month = this.locale.months[this.selectedDate.getMonth()];
    const day = this.selectedDate.getDate();
    
    this.yearElement.textContent = year;
    this.dayMonthElement.textContent = `${day} ${month}`;
  }

  /**
   * Отрисовка календаря
   */
  renderCalendar() {
    // Очищаем элементы
    this.weekdaysElement.innerHTML = '';
    this.daysElement.innerHTML = '';
    
    // Отображаем дни недели
    for (let i = 0; i < 7; i++) {
      const weekdayElement = document.createElement('div');
      weekdayElement.className = 'md-date-weekday';
      weekdayElement.textContent = this.locale.weekdaysShort[(i + 1) % 7]; // Начинаем с понедельника
      this.weekdaysElement.appendChild(weekdayElement);
    }
    
    // Отображаем месяц и год в навигации
    this.titleElement.textContent = `${this.locale.months[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
    
    // Получаем дни месяца
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    
    // Первый день месяца
    const firstDay = new Date(year, month, 1);
    // Последний день месяца
    const lastDay = new Date(year, month + 1, 0);
    
    // День недели первого дня месяца (0 - воскресенье)
    let firstDayOfWeek = firstDay.getDay();
    // Преобразуем в формат, где понедельник - первый день (1)
    firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;
    
    // Дни предыдущего месяца
    const prevMonthDays = new Date(year, month, 0).getDate();
    
    // Добавляем дни предыдущего месяца
    for (let i = 0; i < firstDayOfWeek; i++) {
      const day = prevMonthDays - firstDayOfWeek + i + 1;
      this.createDayElement(day, 'other-month', new Date(year, month - 1, day));
    }
    
    // Добавляем дни текущего месяца
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(year, month, i);
      let className = '';
      
      // Проверяем, является ли день сегодняшним
      const today = new Date();
      if (i === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
        className = 'today';
      }
      
      // Проверяем, является ли день выбранным
      if (this.selectedDate && i === this.selectedDate.getDate() && 
          month === this.selectedDate.getMonth() && 
          year === this.selectedDate.getFullYear()) {
        className = 'selected';
      }
      
      // Проверяем ограничения минимальной и максимальной даты
      let disabled = false;
      if (this.options.minDate && date < this.options.minDate) {
        disabled = true;
      }
      if (this.options.maxDate && date > this.options.maxDate) {
        disabled = true;
      }
      
      this.createDayElement(i, className, date, disabled);
    }
    
    // Добавляем дни следующего месяца
    const totalDays = firstDayOfWeek + lastDay.getDate();
    const remainingDays = 7 - (totalDays % 7);
    
    if (remainingDays < 7) {
      for (let i = 1; i <= remainingDays; i++) {
        this.createDayElement(i, 'other-month', new Date(year, month + 1, i));
      }
    }
    
    // Отображаем селектор года
    this.renderYearSelector();
  }

  /**
   * Создание элемента дня
   */
  createDayElement(day, className, date, disabled = false) {
    const dayElement = document.createElement('div');
    dayElement.className = `md-date-day ${className}`;
    dayElement.textContent = day;
    
    if (disabled) {
      dayElement.classList.add('disabled');
    } else {
      dayElement.addEventListener('click', () => {
        this.selectDate(date);
      });
    }
    
    this.daysElement.appendChild(dayElement);
  }

  /**
   * Отрисовка селектора года
   */
  renderYearSelector() {
    this.yearList.innerHTML = '';
    
    const currentYear = this.currentDate.getFullYear();
    const startYear = currentYear - 50;
    const endYear = currentYear + 50;
    
    for (let year = startYear; year <= endYear; year++) {
      const yearOption = document.createElement('li');
      yearOption.className = 'md-year-option';
      yearOption.textContent = year;
      
      if (year === currentYear) {
        yearOption.classList.add('selected');
      }
      
      yearOption.addEventListener('click', () => {
        this.selectYear(year);
      });
      
      this.yearList.appendChild(yearOption);
    }
  }

  /**
   * Прокрутка к выбранному году
   */
  scrollToSelectedYear() {
    const selectedYearElement = this.yearList.querySelector('.selected');
    if (selectedYearElement) {
      this.yearSelector.scrollTop = selectedYearElement.offsetTop - this.yearSelector.offsetHeight / 2 + selectedYearElement.offsetHeight / 2;
    }
  }

  /**
   * Отрисовка часов
   */
  renderClock() {
    this.clockElement.innerHTML = '';
    this.clockElement.appendChild(this.clockHandElement);
    this.clockElement.appendChild(this.clockCenterElement);
    
    const values = this.timeMode === 'hours' ? 
      (this.options.timeFormat === '12h' ? [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]) : 
      [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55];
    
    const radius = 90;
    const tickRadius = this.timeMode === 'hours' && this.options.timeFormat === '24h' && values.length > 12 ? 65 : radius;
    
    values.forEach((value, index) => {
      // Расчет положения
      const angle = (index * (360 / (this.timeMode === 'hours' && this.options.timeFormat === '24h' ? 24 : 12)) - 90) * (Math.PI / 180);
      const x = Math.cos(angle) * tickRadius;
      const y = Math.sin(angle) * tickRadius;
      
      // Создание тика
      const tick = document.createElement('div');
      tick.className = 'md-clock-tick';
      tick.textContent = value < 10 ? `0${value}` : value;
      
      tick.style.left = `calc(50% + ${x}px - 15px)`;
      tick.style.top = `calc(50% + ${y}px - 15px)`;
      
      // Активный час/минута
      const activeValue = this.timeMode === 'hours' ? 
        this.selectedDate.getHours() : 
        this.selectedDate.getMinutes();
        
      if (value === activeValue || 
          (this.timeMode === 'hours' && this.options.timeFormat === '12h' && 
           value === activeValue % 12 && (activeValue % 12 === 0 ? 12 : activeValue % 12))) {
        tick.classList.add('active');
      }
      
      tick.addEventListener('click', () => {
        if (this.timeMode === 'hours') {
          // Корректировка для 12-часового формата
          let hours = value;
          if (this.options.timeFormat === '12h') {
            const isPM = this.selectedDate.getHours() >= 12;
            hours = value === 12 ? (isPM ? 12 : 0) : (isPM ? value + 12 : value);
          }
          
          this.selectedDate.setHours(hours);
          this.setTimeMode('minutes');
        } else {
          this.selectedDate.setMinutes(value);
          this.updateClock();
        }
        
        this.updateHeader();
      });
      
      this.clockElement.appendChild(tick);
    });
    
    this.updateClock();
  }

  /**
   * Обновление положения стрелки часов
   */
  updateClock() {
    const value = this.timeMode === 'hours' ? 
      (this.options.timeFormat === '12h' ? this.selectedDate.getHours() % 12 || 12 : this.selectedDate.getHours()) : 
      this.selectedDate.getMinutes();
      
    const angle = this.timeMode === 'hours' ? 
      (value * 30) : // 360 / 12 = 30 градусов для часов
      (value * 6);   // 360 / 60 = 6 градусов для минут
      
    this.clockHandElement.style.transform = `rotate(${angle}deg)`;
    
    this.hoursElement.textContent = this.selectedDate.getHours() < 10 ? 
      `0${this.selectedDate.getHours()}` : this.selectedDate.getHours();
      
    this.minutesElement.textContent = this.selectedDate.getMinutes() < 10 ? 
      `0${this.selectedDate.getMinutes()}` : this.selectedDate.getMinutes();
      
    if (this.timeMode === 'hours') {
      this.hoursElement.classList.add('md-time-active');
      this.minutesElement.classList.remove('md-time-active');
    } else {
      this.hoursElement.classList.remove('md-time-active');
      this.minutesElement.classList.add('md-time-active');
    }
  }

  /**
   * Установка режима выбора времени (часы или минуты)
   */
  setTimeMode(mode) {
    this.timeMode = mode;
    this.renderClock();
  }

  /**
   * Переключение между выбором даты и времени
   */
  toggleView() {
    this.currentView = this.currentView === 'date' ? 'time' : 'date';
    this.updateView();
  }

  /**
   * Выбор даты
   */
  selectDate(date) {
    // Сохраняем время из предыдущей выбранной даты
    const hours = this.selectedDate ? this.selectedDate.getHours() : 0;
    const minutes = this.selectedDate ? this.selectedDate.getMinutes() : 0;
    
    this.selectedDate = new Date(date);
    this.selectedDate.setHours(hours);
    this.selectedDate.setMinutes(minutes);
    
    this.currentDate = new Date(date);
    
    // Переходим к выбору времени
    this.currentView = 'time';
    this.updateView();
  }

  /**
   * Выбор года
   */
  selectYear(year) {
    this.currentDate.setFullYear(year);
    this.yearSelector.classList.remove('active');
    this.renderCalendar();
  }

  /**
   * Переход к предыдущему месяцу
   */
  prevMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() - 1);
    this.renderCalendar();
  }

  /**
   * Переход к следующему месяцу
   */
  nextMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() + 1);
    this.renderCalendar();
  }

  /**
   * Форматирование даты
   */
  formatDate(date) {
    if (!date) return '';
    
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    let formattedDate = this.options.format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes);
      
    return formattedDate;
  }

  /**
   * Разбор строки даты
   */
  parseDate(dateString) {
    if (!dateString) return new Date();
    
    // Простой парсер для формата YYYY-MM-DD HH:mm
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
  }
}

// Инициализация всех полей для выбора даты
document.addEventListener('DOMContentLoaded', function() {
  // Находим элемент для выбора даты
  const dateInput = document.getElementById('deadline_picker');
  
  if (dateInput) {
    console.log('Найдено поле для выбора даты:', dateInput);
    
    // Инициализируем календарь
    const datePicker = new MDDatePicker({
      targetInput: dateInput,
      format: 'YYYY-MM-DD HH:mm',
      language: 'ru',
      minDate: new Date(),
      timeFormat: '24h'
    });
    
    // Добавляем обработчик клика на иконку календаря
    const calendarIcon = document.querySelector('label[for="deadline_picker"] i.bi-calendar');
    if (calendarIcon) {
      calendarIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        datePicker.open();
      });
    }
    
    console.log('Material Design DatePicker успешно инициализирован');
  } else {
    console.error('Поле для выбора даты не найдено!');
  }
});
