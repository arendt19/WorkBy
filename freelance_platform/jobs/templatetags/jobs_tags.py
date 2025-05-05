from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Разделяет строку по указанному разделителю и возвращает список
    """
    if not value:
        return []
    return value.split(delimiter)

@register.filter
def strip(value):
    """
    Удаляет пробелы в начале и конце строки
    """
    if not value:
        return ''
    return value.strip()

@register.filter
def get_item(dictionary, key):
    """
    Получает значение из словаря по ключу
    """
    return dictionary.get(key)

@register.filter
def dictkey(dictionary, key):
    """
    Проверяет наличие ключа в словаре
    """
    if not dictionary:
        return False
    return key in dictionary

@register.filter
def get_range(value):
    """
    Возвращает диапазон от 1 до value
    """
    return range(1, int(value) + 1)

@register.filter(name='jobs_add_class')
def jobs_add_class(field, css_class):
    """Добавляет CSS класс к виджету поля формы (Jobs app версия)"""
    return field.as_widget(attrs={
        "class": " ".join((field.field.widget.attrs.get('class', ''), css_class))
    }) 