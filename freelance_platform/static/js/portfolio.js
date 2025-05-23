/**
 * Скрипт для управления формой создания/редактирования проекта портфолио
 */

document.addEventListener('DOMContentLoaded', function() {
    // Объект с переводами для разных языков
    const translations = {
        en: {
            dragDropText: "Drag and drop images here or click to select files",
            imagePreview: "Image Preview",
            fileTooBig: "File is too large. Maximum size is 5MB",
            invalidFileType: "Invalid file type. Only images are allowed",
            addImage: "Add Image",
            deleteImage: "Delete this image",
            orderHint: "Lower numbers appear first",
            requiredField: "This field is required",
            successUpload: "Image uploaded successfully",
            errorUpload: "Error uploading image",
            confirmDelete: "Are you sure you want to delete this image?",
            yes: "Yes",
            no: "No"
        },
        ru: {
            dragDropText: "Перетащите изображения сюда или нажмите для выбора файлов",
            imagePreview: "Предпросмотр изображения",
            fileTooBig: "Файл слишком большой. Максимальный размер 5МБ",
            invalidFileType: "Недопустимый тип файла. Разрешены только изображения",
            addImage: "Добавить изображение",
            deleteImage: "Удалить это изображение",
            orderHint: "Меньшие числа отображаются первыми",
            requiredField: "Это поле обязательно для заполнения",
            successUpload: "Изображение успешно загружено",
            errorUpload: "Ошибка при загрузке изображения",
            confirmDelete: "Вы уверены, что хотите удалить это изображение?",
            yes: "Да",
            no: "Нет"
        },
        kk: {
            dragDropText: "Суреттерді осында сүйреп апарыңыз немесе файлдарды таңдау үшін басыңыз",
            imagePreview: "Суретті алдын ала қарау",
            fileTooBig: "Файл тым үлкен. Максималды өлшемі 5МБ",
            invalidFileType: "Жарамсыз файл түрі. Тек суреттерге рұқсат етіледі",
            addImage: "Сурет қосу",
            deleteImage: "Бұл суретті жою",
            orderHint: "Кіші сандар алдымен көрсетіледі",
            requiredField: "Бұл өріс міндетті",
            successUpload: "Сурет сәтті жүктелді",
            errorUpload: "Суретті жүктеу кезінде қате",
            confirmDelete: "Бұл суретті жойғыңыз келетініне сенімдісіз бе?",
            yes: "Иә",
            no: "Жоқ"
        }
    };

    // Определяем текущий язык из HTML-атрибута lang
    const currentLang = document.documentElement.lang || 'en';
    
    // Получаем переводы для текущего языка или используем английский по умолчанию
    const t = translations[currentLang] || translations['en'];

    const addImageBtn = document.getElementById('add-image');
    const formsetContainer = document.getElementById('formset-container');
    const emptyForm = document.querySelector('.formset-empty');
    const totalForms = document.getElementById('id_images-TOTAL_FORMS');
    
    // Инициализация drag-and-drop для всех существующих полей изображений
    initializeAllDropZones();
    
    // Добавление подсказок для полей порядка
    addOrderFieldHints();

    // Обработчик для добавления нового поля для изображения
    addImageBtn.addEventListener('click', function() {
        addNewImageForm();
    });
    
    // Обработчик для удаления изображения
    formsetContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-formset-row') || 
            e.target.parentElement.classList.contains('delete-formset-row')) {
            
            const deleteCheckbox = e.target.closest('.form-check').querySelector('input[type="checkbox"]');
            const formItem = e.target.closest('.formset-item');
            
            // Если есть предпросмотр изображения, спрашиваем подтверждение
            if (formItem.querySelector('.image-preview')) {
                if (confirm(t.confirmDelete)) {
                    deleteCheckbox.checked = true;
                    formItem.style.opacity = '0.5';
                }
            } else {
                // Если нет изображения, просто помечаем на удаление
                deleteCheckbox.checked = true;
                formItem.style.opacity = '0.5';
            }
        }
    });

    // Валидация формы перед отправкой
    document.querySelector('form').addEventListener('submit', function(e) {
        const titleField = document.getElementById('id_title');
        const descriptionField = document.getElementById('id_description');
        
        let isValid = true;
        
        // Проверка обязательных полей
        if (!titleField.value.trim()) {
            showValidationError(titleField, t.requiredField);
            isValid = false;
        } else {
            clearValidationError(titleField);
        }
        
        if (!descriptionField.value.trim()) {
            showValidationError(descriptionField, t.requiredField);
            isValid = false;
        } else {
            clearValidationError(descriptionField);
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });

    /**
     * Добавляет новую форму для изображения
     */
    function addNewImageForm() {
        // Клонируем пустую форму
        const newForm = emptyForm.cloneNode(true);
        newForm.classList.remove('formset-empty');
        
        // Получаем текущее количество форм
        const formCount = parseInt(totalForms.value);
        
        // Обновляем атрибуты id и name в новой форме
        newForm.innerHTML = newForm.innerHTML.replace(
            new RegExp('images-\\d+-', 'g'),
            `images-${formCount}-`
        );
        
        // Добавляем новую форму в контейнер
        formsetContainer.appendChild(newForm);
        
        // Обновляем счетчик форм
        totalForms.value = formCount + 1;
        
        // Инициализируем drag-and-drop для нового поля
        initializeDropZone(newForm.querySelector('.form-group input[type="file"]'));
        
        // Добавляем подсказку для поля порядка
        addOrderFieldHint(newForm.querySelector('input[name$="-order"]'));
    }

    /**
     * Инициализирует все зоны для перетаскивания файлов
     */
    function initializeAllDropZones() {
        const fileInputs = document.querySelectorAll('.formset-item input[type="file"]');
        fileInputs.forEach(input => {
            initializeDropZone(input);
        });
    }

    /**
     * Инициализирует зону для перетаскивания файлов
     */
    function initializeDropZone(fileInput) {
        if (!fileInput) return;
        
        const formGroup = fileInput.closest('.form-group');
        
        // Создаем зону для перетаскивания
        const dropZone = document.createElement('div');
        dropZone.className = 'drop-zone mb-2';
        dropZone.innerHTML = `<span class="drop-zone__prompt">${t.dragDropText}</span>`;
        
        // Вставляем зону перед input
        formGroup.insertBefore(dropZone, fileInput);
        
        // Скрываем оригинальный input
        fileInput.style.display = 'none';
        
        // Обработчик клика по зоне
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Обработчик выбора файла
        fileInput.addEventListener('change', function() {
            updateThumbnail(dropZone, fileInput.files[0]);
        });
        
        // Обработчики перетаскивания
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('drop-zone--over');
        });
        
        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, function() {
                dropZone.classList.remove('drop-zone--over');
            });
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateThumbnail(dropZone, e.dataTransfer.files[0]);
            }
            
            dropZone.classList.remove('drop-zone--over');
        });
        
        // Если уже есть предпросмотр, отображаем его
        const existingPreview = formGroup.querySelector('.image-preview');
        if (existingPreview) {
            const thumbnail = document.createElement('div');
            thumbnail.className = 'drop-zone__thumb';
            thumbnail.style.backgroundImage = `url('${existingPreview.src}')`;
            
            // Удаляем текст-подсказку
            const prompt = dropZone.querySelector('.drop-zone__prompt');
            if (prompt) {
                dropZone.removeChild(prompt);
            }
            
            dropZone.appendChild(thumbnail);
            
            // Удаляем старый предпросмотр
            existingPreview.remove();
        }
    }

    /**
     * Обновляет миниатюру в зоне перетаскивания
     */
    function updateThumbnail(dropZone, file) {
        // Удаляем текст-подсказку
        let prompt = dropZone.querySelector('.drop-zone__prompt');
        if (prompt) {
            dropZone.removeChild(prompt);
        }
        
        // Удаляем предыдущую миниатюру
        let thumbnail = dropZone.querySelector('.drop-zone__thumb');
        if (thumbnail) {
            dropZone.removeChild(thumbnail);
        }
        
        // Проверяем тип файла
        if (!file.type.startsWith('image/')) {
            showError(dropZone, t.invalidFileType);
            return;
        }
        
        // Проверяем размер файла (максимум 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showError(dropZone, t.fileTooBig);
            return;
        }
        
        // Создаем новую миниатюру
        thumbnail = document.createElement('div');
        thumbnail.className = 'drop-zone__thumb';
        thumbnail.dataset.label = file.name;
        dropZone.appendChild(thumbnail);
        
        // Показываем миниатюру
        const reader = new FileReader();
        reader.onload = function() {
            thumbnail.style.backgroundImage = `url('${reader.result}')`;
        };
        reader.readAsDataURL(file);
        
        // Обновляем поле caption, если оно пустое
        const formItem = dropZone.closest('.formset-item');
        const captionInput = formItem.querySelector('input[name$="-caption"]');
        if (captionInput && !captionInput.value) {
            // Используем имя файла без расширения в качестве подписи
            const fileName = file.name.replace(/\.[^/.]+$/, "");
            captionInput.value = fileName;
        }
    }

    /**
     * Показывает сообщение об ошибке в зоне перетаскивания
     */
    function showError(dropZone, message) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'drop-zone__error alert alert-danger';
        errorMsg.textContent = message;
        
        dropZone.appendChild(errorMsg);
        
        // Удаляем сообщение через 3 секунды
        setTimeout(() => {
            if (errorMsg.parentNode === dropZone) {
                dropZone.removeChild(errorMsg);
                
                // Восстанавливаем текст-подсказку
                const prompt = document.createElement('span');
                prompt.className = 'drop-zone__prompt';
                prompt.textContent = t.dragDropText;
                dropZone.appendChild(prompt);
            }
        }, 3000);
    }

    /**
     * Добавляет подсказки для всех полей порядка
     */
    function addOrderFieldHints() {
        const orderInputs = document.querySelectorAll('input[name$="-order"]');
        orderInputs.forEach(input => {
            addOrderFieldHint(input);
        });
    }

    /**
     * Добавляет подсказку для поля порядка
     */
    function addOrderFieldHint(input) {
        if (!input) return;
        
        const formGroup = input.closest('.form-group');
        const helpText = document.createElement('small');
        helpText.className = 'form-text text-muted';
        helpText.textContent = t.orderHint;
        
        formGroup.appendChild(helpText);
    }

    /**
     * Показывает ошибку валидации для поля
     */
    function showValidationError(field, message) {
        // Удаляем предыдущую ошибку, если есть
        clearValidationError(field);
        
        // Добавляем класс ошибки
        field.classList.add('is-invalid');
        
        // Создаем сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // Добавляем сообщение после поля
        field.parentNode.appendChild(errorDiv);
    }

    /**
     * Очищает ошибку валидации для поля
     */
    function clearValidationError(field) {
        field.classList.remove('is-invalid');
        
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
});
