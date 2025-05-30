from django import template
from decimal import Decimal

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

@register.filter
def multiply(value, arg):
    """
    Умножает значение на аргумент
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='jobs_add_class')
def jobs_add_class(field, css_class):
    """Добавляет CSS класс к виджету поля формы (Jobs app версия)"""
    return field.as_widget(attrs={
        "class": " ".join((field.field.widget.attrs.get('class', ''), css_class))
    })

@register.filter(name='currency')
def currency(value):
    """
    Форматирует число как денежную сумму
    Например: 1234.56 -> 1,234.56 ₸
    """
    if value is None:
        return "0 ₸"
    
    try:
        value = float(value)
        formatted = "{:,.2f}".format(value)
        # Заменяем запятую на пробел для лучшего отображения в русском/казахском формате
        formatted = formatted.replace(',', ' ')
        return f"{formatted} ₸"
    except (ValueError, TypeError):
        return f"0 ₸"